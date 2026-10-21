/** Jason Stys: race-safe, text-only evidence UI. Variables current/generation; exact lines: docs/CODE_INDEX.md. */
import "./style.css";
import { downloadUrl, reason, timestamp, visibleRows, type Report } from "./format";

/** Require the reviewed document structure instead of silently ignoring missing controls. */
function element<T extends HTMLElement>(id: string): T {
  const node = document.getElementById(id);
  if (!node) throw new Error("Missing application element");
  return node as T;
}
const form = element<HTMLFormElement>("controls");
const scenario = element<HTMLSelectElement>("scenario");
const age = element<HTMLSelectElement>("max_age");
const results = element("results");
const message = element("message");
const filter = element<HTMLSelectElement>("filter");
let current: Report | null = null;
let generation = 0;

/** Create text nodes only, including all applicant-supplied descriptions and reason strings. */
function node(tag: string, value: string, className = ""): HTMLElement {
  const result = document.createElement(tag);
  result.textContent = value;
  result.className = className;
  return result;
}
/** Render one coherent accepted report; never mix pending settings with previous evidence. */
function render(report: Report, selected: string, maxAge: number): void {
  current = report;
  element("verdict").textContent = report.summary.ready
    ? "Declared evidence is complete"
    : "Baseline needs attention";
  const stats = element("stats");
  stats.replaceChildren();
  for (const [label, value] of [
    ["Requirements", report.summary.total],
    ["Verified", report.summary.verified],
    ["Blocked", report.summary.blocked],
    ["Accepted tests", report.summary.accepted_tests],
  ] as const) {
    const card = node("div", "", "stat");
    card.append(node("strong", String(value)), node("span", label));
    stats.append(card);
  }
  element("source").textContent = report.input.source;
  element("as-of").textContent = timestamp(report.input.as_of) + " · fixed fixture clock";
  element("identity").textContent = report.id;
  const tests = element("test-cards");
  tests.replaceChildren();
  for (const test of report.tests) {
    const card = node("article", "", "test-card");
    card.append(
      node("span", test.id, "eyebrow"),
      node("h3", test.title),
      node(
        "p",
        test.accepted ? "Accepted · latest attempt" : test.reasons.map(reason).join(" · "),
        test.accepted ? "pass" : "blocked",
      ),
    );
    card.append(
      node(
        "p",
        test.result
          ? `Attempt ${test.result.attempt} · ${test.result.status} · ${test.result.id}`
          : "No result supplied",
      ),
    );
    tests.append(card);
  }
  const downloads = element("downloads");
  downloads.replaceChildren();
  for (const format of ["json", "csv", "html", "input"]) {
    const link = node(
      "a",
      format === "input" ? "Replay input" : format.toUpperCase(),
    ) as HTMLAnchorElement;
    link.href = downloadUrl(selected, maxAge, format);
    link.download = "";
    downloads.append(link);
  }
  results.hidden = false;
  message.textContent = report.summary.release_source_matches
    ? "Evaluation complete · independent SQL verdicts agree."
    : "Evaluation complete · release source does not match candidate source.";
  renderRows();
}
/** Change only the visible table; exports and summary always retain the entire report. */
function renderRows(): void {
  const body = element("rows");
  body.replaceChildren();
  if (!current) return;
  const rows = visibleRows(current.requirements, filter.value);
  element("empty").hidden = rows.length > 0;
  for (const row of rows) {
    const tr = node("tr", "");
    const identity = node("th", "");
    identity.setAttribute("scope", "row");
    identity.append(
      node("strong", `${row.id} / r${row.revision}`),
      node("span", row.title, "row-title"),
      node("small", row.criticality),
    );
    const verdict = node("td", "");
    verdict.append(
      node("span", row.status, `pill ${row.status}`),
      node("small", row.reasons.map(reason).join(" · ")),
    );
    tr.append(
      identity,
      node("td", row.tests.join(", ") || "No tests"),
      node("td", row.faults.join(", ") || "No declared faults"),
      verdict,
    );
    body.append(tr);
  }
}
/** Evaluate finite settings with a generation token; late responses cannot resurrect stale results. */
async function evaluate(): Promise<void> {
  const ticket = ++generation;
  const selected = scenario.value;
  const maxAge = Number(age.value);
  results.hidden = true;
  current = null;
  message.textContent = "Evaluating traceability…";
  try {
    const response = await fetch(
      `/api/run?${new URLSearchParams({ scenario: selected, max_age: String(maxAge) })}`,
    );
    if (!response.ok) throw new Error("Request failed");
    const report = (await response.json()) as Report;
    if (ticket !== generation) return;
    if (!report.verification.sql_agrees) throw new Error("Verification unavailable");
    render(report, selected, maxAge);
  } catch {
    if (ticket === generation) {
      results.hidden = true;
      message.textContent =
        "Evidence unavailable. Check the local service, then evaluate again. No previous result is shown.";
    }
  }
}
/** Editing invalidates both rendered evidence and in-flight requests until explicit reevaluation. */
function invalidate(): void {
  ++generation;
  current = null;
  results.hidden = true;
  message.textContent = "Configuration changed. Evaluate to refresh evidence and downloads.";
}
form.addEventListener("submit", (event) => {
  event.preventDefault();
  void evaluate();
});
scenario.addEventListener("change", invalidate);
age.addEventListener("change", invalidate);
filter.addEventListener("change", renderRows);
void evaluate();
