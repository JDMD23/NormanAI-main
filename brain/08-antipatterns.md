# 08 — Antipatterns: the recurring failure catalog

What to look for first when auditing a codebase. Ordered roughly by how often each
is the *actual* root cause of a slow, fragile project. Each entry: smell → why it
kills → the move.

## 1. The distributed monolith
Services split by the org chart or by fashion, still coupled by shared databases,
synchronized deploys, or chatty synchronous call chains. All the costs of
distribution, none of the benefits. **Move:** merge back or draw real boundaries
(own data, async or versioned contracts, independent deploys) — usually merge back.

## 2. The god object / god module
One class/module/table that everything imports and every feature touches (`utils.py`
at 4k lines, `User` doing auth+billing+prefs+audit). Every change collides here;
every developer must understand it. **Move:** split by *reason to change*; break
import cycles first — cycles are how gods are born.

## 3. Logic in the wrong layer
Business rules in controllers, templates, SQL triggers, or shell scripts around the
app — anywhere but the domain core. Symptom: answering "where is the rule that X?"
takes grep + prayer; the same rule exists in three layers, disagreeing. **Move:**
functional core (see 02); each rule gets exactly one home.

## 4. Configuration sprawl / flag soup
Dozens of env vars and feature flags, interactions untested, half stale, defaults
undocumented. Effective behavior in production is unknowable; every flag doubles the
state space. **Move:** delete stale flags on a schedule (flags have expiry dates);
config gets types, validation-at-boot (crash on bad config, don't limp), and one
documented source of truth.

## 5. The test suite that tests nothing
High coverage, mock-everything tests asserting that mocks were called — implementation
mirrored, behavior unverified. Refactors break 200 tests while real bugs pass.
It's worse than no suite: cost without safety, plus false confidence. **Move:** delete
mock-theater tests; test the core with real values, the seams with real integrations.

## 6. Silent failure
`except: pass`, swallowed promise rejections, ignored return codes, retries hiding
persistent failure, empty catch blocks "to be safe." Data corrupts quietly; the bug
surfaces weeks later, far from the cause, unreproducible. **Move:** crash loudly by
default; every deliberate suppression gets a comment stating why and a log/metric.

## 7. The unowned mutable
Shared caches, module-level singletons, globals mutated from many places, two systems
writing one table. Nobody can say what value it holds or who set it. Root cause of the
worst debugging sessions. **Move:** one writer per value; explicit ownership; derived
data recomputable from source.

## 8. Résumé-driven / fashion-driven architecture
Kubernetes + microservices + event sourcing + a service mesh for a CRUD app with
three users. The complexity tax lands on every feature, deploy, and incident forever.
**Move:** boring tech, modular monolith, one database (see 02, 07). Deleting
infrastructure is a legitimate, high-ROI engineering act.

## 9. The permanent prototype
"Temporary" scripts and hacks that acquired users: no tests, hardcoded paths, secrets
inline, one person understands it, now load-bearing. **Move:** the moment something
gains users or feeds another system, it gets the production floor: version control,
config extraction, error reporting, a test on the money path, a second person who
understands it.

## 10. Broken feedback loops
30-minute CI, flaky tests everyone re-runs, un-runnable local setup, deploys gated on
a person, review turnaround measured in days. Not one dramatic failure — a compounding
tax on every change, and the top predictor of team slowness. **Move:** treat loop
latency as a first-class defect; fix the slowest loop first (see 06).

## 11. Knowledge silos
Bus factor of one on critical systems; no ADRs; review as rubber stamp; the "wizard"
whose vacation stops the team. Fragility that looks like efficiency. **Move:** ADRs
for non-obvious decisions, real review (the second person must actually understand),
rotate ownership of scary areas.

## 12. Premature abstraction
Interfaces with one implementation, plugin systems with no second plugin, "generic"
engines configured by YAML that only one workflow uses, wrappers wrapping wrappers.
Indirection without options — every reader pays, nobody collects. **Move:** inline
it; re-abstract when the second real use case arrives and shows where the seam
actually is (see 01 on wrong abstractions vs duplication).

---

### Meta-pattern
Almost every entry is one of two failures: **complexity nobody is paying for**
(8, 12, 4) or **coupling nobody can see** (1, 2, 3, 7, 11). When a codebase feels
bad but the smell isn't on this list, ask which of those two it is — the answer
usually names the fix.
