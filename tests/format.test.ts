/** Jason Stys: pure UI contracts. Functions/variables: docs/CODE_INDEX.md. */
import { describe, it, expect } from "vitest";
import { downloadUrl, reason, timestamp, visibleRows, type Requirement } from "../web/format";
describe("evidence formatting", () => {
  it("makes reason codes readable without markup interpretation", () => {
    expect(reason("baseline-mismatch")).toBe("baseline mismatch");
    expect(reason("<script>")).toBe("<script>");
  });
  it("formats fixed UTC seconds", () => {
    expect(timestamp(1800000000)).toBe("2027-01-15 08:00:00 UTC");
  });
  it("constructs encoded same-origin downloads", () => {
    expect(downloadUrl("a&x=y", 86400, "json")).toBe(
      "/api/report?scenario=a%26x%3Dy&max_age=86400&format=json",
    );
  });
  it("filters without mutating the report", () => {
    const rows = [{ status: "verified" }, { status: "blocked" }] as Requirement[];
    expect(visibleRows(rows, "all")).toEqual(rows);
    expect(visibleRows(rows, "blocked")).toEqual([rows[1]]);
    expect(visibleRows(rows, "verified")).toEqual([rows[0]]);
    expect(visibleRows(rows, "unknown")).toEqual([]);
    expect(rows).toHaveLength(2);
  });
});
