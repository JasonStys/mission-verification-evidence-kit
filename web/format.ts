/** Jason Stys: typed report rendering helpers. Functions/fields: docs/CODE_INDEX.md. */
export interface Requirement {
  id: string;
  title: string;
  revision: number;
  criticality: string;
  tests: string[];
  faults: string[];
  reasons: string[];
  status: "verified" | "blocked";
}
export interface TestEvidence {
  id: string;
  title: string;
  accepted: boolean;
  reasons: string[];
  result: null | {
    id: string;
    attempt: number;
    status: string;
    completed: number;
    artifact: string;
  };
}
export interface Report {
  id: string;
  input: { source: string; as_of: number };
  requirements: Requirement[];
  tests: TestEvidence[];
  summary: {
    total: number;
    verified: number;
    blocked: number;
    accepted_tests: number;
    release_source_matches: boolean;
    ready: boolean;
  };
  verification: { sql_agrees: boolean; provenance_authenticated: boolean };
}
/** Convert a reason code into readable text, without accepting markup. */
export function reason(value: string): string {
  return value.replaceAll("-", " ");
}
/** Filter the already computed matrix without changing the actual report or gate. */
export function visibleRows(rows: Requirement[], filter: string): Requirement[] {
  return filter === "all" ? rows : rows.filter((row) => row.status === filter);
}
/** Generate same-origin downloads from the evaluated, not currently edited, settings. */
export function downloadUrl(scenario: string, age: number, format: string): string {
  return (
    "/api/report?" + new URLSearchParams({ scenario, max_age: String(age), format }).toString()
  );
}
/** Format a declared epoch second without accidentally describing it as a live timestamp. */
export function timestamp(value: number): string {
  return new Date(value * 1000).toISOString().replace(".000Z", " UTC").replace("T", " ");
}
