# Plan evidence revalidation

The work queue turns declared gate results into a review checklist. Blocked tests come first, critical before standard; accepted tests follow with their declared freshness deadlines. Each item lists affected requirements, rejection reasons and the **expected source, test definition and requirement revisions** needed for current evidence. It never runs a test, changes an attempt or waives a rule.

Freshness accepts age equal to max_age. The first invalid integer second is completed+max_age+1; the report also lists the earliest accepted-evidence expiry. These use the supplied fixed as_of timestamp and are not live reminders. Accepted evidence is not automatically invalidated by merely opening a report later.

Coverage work distinguishes missing procedures, fault obligations with no configured test link, and linked tests needing revalidation. Historical chronology conflicts explicitly require investigation; adding a passing attempt alone does not erase inconsistent history. Release-source mismatch is a separate action and cannot be repaired by inflating test counts. The SQL-backed requirement verdict remains authoritative and unchanged.

The UI and full JSON/HTML/CLI gate/history include the same run-hashed queue. Results, artifact hashes and supplied metadata remain declarations, not authenticated proof of truth or completeness. This civilian educational kit is not flight qualification, authorization or safety certification.
