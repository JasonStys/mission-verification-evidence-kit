-- Jason Stys: immutable local content-identity history, no accounts or automatic retention deletion.
CREATE TABLE IF NOT EXISTS runs(id TEXT PRIMARY KEY, report_json TEXT NOT NULL);
CREATE TRIGGER IF NOT EXISTS runs_no_update BEFORE UPDATE ON runs BEGIN SELECT RAISE(ABORT,'immutable'); END;
CREATE TRIGGER IF NOT EXISTS runs_no_delete BEFORE DELETE ON runs BEGIN SELECT RAISE(ABORT,'immutable'); END;
