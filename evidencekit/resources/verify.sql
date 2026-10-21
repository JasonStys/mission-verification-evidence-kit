-- Jason Stys: independent traceability verdicts; :document is bound JSON, never SQL text.
-- Latest attempt is authoritative; chronology, revisions, age and ALL test/fault obligations must agree.
WITH
d AS (SELECT json(:document) AS j),
req AS (SELECT value AS j FROM d, json_each(d.j,'$.requirements')),
test AS (SELECT value AS j FROM d, json_each(d.j,'$.tests')),
fault AS (SELECT value AS j FROM d, json_each(d.j,'$.faults')),
result AS (SELECT value AS j,
 ROW_NUMBER() OVER (PARTITION BY value->>'test' ORDER BY CAST(value->>'attempt' AS INTEGER) DESC) AS rank
 FROM d, json_each(d.j,'$.results')),
accepted AS (
 SELECT t.j FROM test t, d
 JOIN result x ON x.j->>'test'=t.j->>'id' AND x.rank=1
 WHERE x.j->>'status'='pass' AND x.j->>'source'=d.j->>'source'
 AND x.j->>'definition'=t.j->>'definition'
 AND CAST(d.j->>'as_of' AS INTEGER)-CAST(x.j->>'completed' AS INTEGER)
 BETWEEN 0 AND CAST(d.j->>'max_age' AS INTEGER)
 AND NOT EXISTS (
  SELECT 1 FROM json_each(t.j,'$.requirements') link JOIN req r ON r.j->>'id'=link.value
  WHERE json_extract(x.j,'$.baselines.' || link.value) != CAST(r.j->>'revision' AS INTEGER))
 AND NOT EXISTS (
  SELECT 1 FROM result a JOIN result b ON a.j->>'test'=b.j->>'test'
  WHERE a.j->>'test'=t.j->>'id' AND CAST(a.j->>'attempt' AS INTEGER)<CAST(b.j->>'attempt' AS INTEGER)
  AND CAST(a.j->>'completed' AS INTEGER)>CAST(b.j->>'completed' AS INTEGER))
)
SELECT r.j->>'id' AS id,
 CAST(
 EXISTS (SELECT 1 FROM test t, json_each(t.j,'$.requirements') link WHERE link.value=r.j->>'id')
 AND NOT EXISTS (
  SELECT 1 FROM test t, json_each(t.j,'$.requirements') link
  WHERE link.value=r.j->>'id' AND NOT EXISTS (SELECT 1 FROM accepted a WHERE a.j->>'id'=t.j->>'id'))
 AND NOT EXISTS (
  SELECT 1 FROM fault f, json_each(f.j,'$.requirements') fr
  WHERE fr.value=r.j->>'id' AND NOT EXISTS (
   SELECT 1 FROM accepted a, json_each(a.j,'$.requirements') ar, json_each(a.j,'$.faults') af
   WHERE ar.value=r.j->>'id' AND af.value=f.j->>'id'))
 AS INTEGER) AS verified
FROM req r ORDER BY id;
