/** Jason Stys — extracted declared-evidence revalidation queue and genuine JSON export.
 * Functions: owned journey; variables: expected critical test, deadline and source-bound baseline.
 * Exact lines: docs/CODE_INDEX.md. Planning human review does not authenticate declarations or run tests.
 */
import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import path from "node:path";
import { expect } from "@playwright/test";
import { runNativeJourney } from "./native_browser.mjs";

await runNativeJourney(async ({ page, request, outputDirectory }) => {
  await expect(page.getByText("Declared evidence is complete", { exact: true })).toBeVisible();
  await expect(page.locator("#revalidation-queue details")).toHaveCount(3);
  await page.locator("#scenario").selectOption("regression");
  await page.getByRole("button", { name: "Evaluate baseline" }).click();
  await expect(page.getByText("Baseline needs attention", { exact: true })).toBeVisible();
  const run = await (await request.get("api/run?scenario=regression")).json();
  assert.equal(run.verification.sql_agrees, true);
  assert.equal(run.verification.provenance_authenticated, false);
  const queue = run.revalidation.tests;
  assert.deepEqual(
    [queue[0].test, queue[0].state, queue[0].critical, queue[0].first_invalid_second],
    ["TEST-STORE", "blocked", true, null],
  );
  assert.deepEqual(queue[0].reasons, ["fail"]);
  assert.deepEqual(queue[0].expected.baselines, { "REQ-STORE": 1 });
  assert.equal(queue[0].expected.source, "a".repeat(40));
  assert.equal(queue[1].first_invalid_second, 1800084601);
  assert.equal(queue[1].seconds_until_invalid, 1800084601 - run.revalidation.as_of);
  await page.locator("#revalidation-queue summary").first().click();
  await expect(page.locator("#revalidation-queue details").first()).toContainText(
    "capture current test evidence",
  );
  const pending = page.waitForEvent("download");
  await page.getByRole("link", { name: "JSON", exact: true }).click();
  const download = await pending;
  const file = path.join(outputDirectory, "native-revalidation.json");
  await download.saveAs(file);
  assert.deepEqual(JSON.parse(await readFile(file, "utf8")), run);
  await page.locator("#scenario").selectOption("missing");
  await page.getByRole("button", { name: "Evaluate baseline" }).click();
  await expect(page.locator("#revalidation-queue")).toContainText("missing procedure");
  assert.equal((await request.get("api/run?max_age=0")).status(), 400);
});
