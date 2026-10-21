/** Jason Stys: real Chromium/Firefox/WebKit acceptance, accessibility and race tests. Index: docs/CODE_INDEX.md. */
import { test, expect } from "@playwright/test";
import AxeBuilder from "@axe-core/playwright";

test.beforeEach(async ({ page }) => {
  await page.goto("/");
  await expect(page.getByText("Declared evidence is complete", { exact: true })).toBeVisible();
});
test("default matrix and full help", async ({ page }) => {
  await expect(page.locator("#rows tr")).toHaveCount(3);
  await expect(page.getByText("PYTHON ↔ SQL CROSS-CHECK")).toBeVisible();
  await page.locator("#help summary").click();
  await expect(page.getByText(/omitted requirements and false declarations/)).toBeVisible();
  await expect(page.getByText("Built by Jason Stys")).toBeVisible();
});
for (const [scenario, reason] of [
  ["missing", "missing test"],
  ["stale", "baseline mismatch"],
  ["regression", "fail"],
  ["fault-gap", "fault gap"],
  ["mixed", "source mismatch"],
]) {
  test(`scenario ${scenario} exposes evidence gap`, async ({ page }) => {
    await page.getByLabel("Evidence scenario").selectOption(scenario!);
    await expect(page.locator("#results")).toBeHidden();
    await page.getByRole("button", { name: "Evaluate baseline" }).click();
    await expect(page.getByText("Baseline needs attention", { exact: true })).toBeVisible();
    await expect(page.locator("#results")).toContainText(reason!);
  });
}
test("filter and configuration invalidation", async ({ page }) => {
  await page.getByLabel("Show", { exact: true }).selectOption("blocked");
  await expect(page.locator("#rows tr")).toHaveCount(0);
  await expect(page.getByText("No requirements match this filter.")).toBeVisible();
  await page.getByLabel("Maximum evidence age").selectOption("3600");
  await expect(page.locator("#results")).toBeHidden();
  await page.getByRole("button", { name: "Evaluate baseline" }).click();
  await expect(page.getByText("Declared evidence is complete", { exact: true })).toBeVisible();
});
test("all downloads are real inert evidence", async ({ page }) => {
  for (const name of ["JSON", "CSV", "HTML", "Replay input"]) {
    const download = page.waitForEvent("download");
    await page.getByRole("link", { name, exact: true }).click();
    const file = await download;
    expect(file.suggestedFilename()).toMatch(/mission-/);
    expect(await file.failure()).toBeNull();
  }
});
test("server failure hides stale evidence", async ({ page }) => {
  await page.route("**/api/run?**", (route) => route.fulfill({ status: 500, body: "Unavailable" }));
  await page.getByRole("button", { name: "Evaluate baseline" }).click();
  await expect(page.getByRole("status")).toContainText("Evidence unavailable");
  await expect(page.locator("#results")).toBeHidden();
});
test("late response cannot restore invalidated results", async ({ page }) => {
  let release: () => void = () => {};
  const pending = new Promise<void>((resolve) => {
    release = resolve;
  });
  await page.route("**/api/run?**", async (route) => {
    await pending;
    await route.continue();
  });
  await page.getByRole("button", { name: "Evaluate baseline" }).click();
  await page.getByLabel("Evidence scenario").selectOption("regression");
  release();
  await expect(page.getByRole("status")).toContainText("Configuration changed");
  await expect(page.locator("#results")).toBeHidden();
});
test("mobile layout stays within viewport", async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 });
  expect(
    await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth),
  ).toBeTruthy();
});
test("WCAG serious and critical checks", async ({ page }) => {
  const scan = await new AxeBuilder({ page }).withTags(["wcag2a", "wcag2aa", "wcag21aa"]).analyze();
  expect(scan.violations).toEqual([]);
});
