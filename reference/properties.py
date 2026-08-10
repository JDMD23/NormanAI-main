"""Norman non-degeneracy properties — reference implementation.

Properties, not examples (studies/hypothesis.md). Lazy: every violation in one
pass as a table, never fail-fast (studies/pandera.md). Each property declares
its own policy on failure (brain/04) — FAIL gates the build, REPORT does not,
because a detector that fails on non-bugs gets silenced.

Run:  python3 properties.py <path-to-crmx>
"""
from __future__ import annotations
import ast, json, pathlib, sys
from datetime import date, timedelta

ROOT = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else ".")
sys.path.insert(0, str(ROOT / "src"))

from norman.core.entity.company import Company            # noqa: E402
from norman.contexts.fit.formula import load_formula      # noqa: E402
from norman.contexts.fit.scorer import score_company      # noqa: E402

TODAY = date(2026, 8, 10)
CFG = json.loads((ROOT / "config" / "fit-score.json").read_text())
WEIGHTS = {c["id"]: c["weight"] for c in CFG["components"]}
RULES = CFG["spec_rules"]
F = load_formula()

RICH = dict(
    name="rich", added_on=TODAY, added_from="prop", hq_city="New York",
    funding_stage="series-a", nyc_employees=40, nyc_open_jobs=8,
    funding_velocity="Fast", velocity_basis="measured",
    latest_funding_date=TODAY - timedelta(days=60), latest_funding_usd=25e6,
    total_funding_usd=40e6, founded_months_ago=30,
    industries=("Fintech",), lead_investors=("Sequoia",), investors=("Sequoia", "a16z"),
)
# One input-change per component that SHOULD move its contribution.
DELTAS = {
    "employees": dict(nyc_employees=2),
    "jobs": dict(nyc_open_jobs=0),
    "growth": dict(funding_velocity="Slow"),
    "industry": dict(industries=("Cannabis",)),
    "funding": dict(latest_funding_date=TODAY - timedelta(days=900), latest_funding_usd=1e5),
    "investors": dict(lead_investors=(), investors=()),
    "stage_fit": dict(funding_stage="late"),
    "hq": dict(hq_city="San Francisco"),
}

failures: list[tuple[str, str, str]] = []   # (policy, property, detail)


def score(**over):
    c = dict(RICH); c.update(over); return score_company(Company(**c), F, TODAY)


def p1_reachable():
    r = score()
    for cid in WEIGHTS:
        if cid in r.missing:
            failures.append(("FAIL", "P1 reachable",
                             f"{cid}: no input makes it fire — structurally dead"))


def p2_discriminates():
    base = score()
    for cid, delta in DELTAS.items():
        moved = score(**delta).subs.get(cid) != base.subs.get(cid)
        if not moved:
            failures.append(("FAIL", "P2 discriminates",
                             f"{cid}: its input changed and its contribution did not"))


def p3_within_weight():
    """No component may contribute more than its declared weight — and a bonus
    FLOOR that exceeds that weight silently erases the signal beneath it."""
    probes = [{}, *DELTAS.values(),
              dict(latest_funding_usd=500e6), dict(nyc_employees=500), dict(nyc_open_jobs=200)]
    peak: dict[str, float] = {}
    for pr in probes:
        for cid, v in score(**pr).subs.items():
            peak[cid] = max(peak.get(cid, 0.0), v)
    for cid, w in WEIGHTS.items():
        if peak.get(cid, 0.0) > w + 1e-9:
            failures.append(("FAIL", "P3 within weight",
                             f"{cid}: contributes {peak[cid]:.1f} against a declared weight of {w}"))


def p4_floor_below_ceiling():
    """Static twin of P3: a *_pts constant naming a component must not exceed it."""
    for k, v in RULES.items():
        if not isinstance(v, (int, float)) or not k.endswith("_pts"):
            continue
        for cid, w in WEIGHTS.items():
            if cid in k and v > w:
                failures.append(("FAIL", "P4 floor<=ceiling",
                                 f"{k}={v} exceeds the '{cid}' weight of {w} — "
                                 f"every input at or above the floor scores identically"))


def p5_reachability():
    """No caller outside its own test file. REPORT, not FAIL: a dead alias and a
    disconnected mechanism both trip this and only one is a bug (BI5)."""
    src = ROOT / "src"
    defs: dict[str, str] = {}
    VALIDATOR_HINTS = ("_is_", "_are_", "unique", "coherent", "ordered", "positive",
                       "compiles", "model_post_init", "exactly_once", "travels_with")
    for p in src.rglob("*.py"):
        if "__pycache__" in str(p):
            continue
        try:
            tree = ast.parse(p.read_text())
        except SyntaxError:
            continue
        for n in ast.walk(tree):
            if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and not n.name.startswith("_"):
                defs.setdefault(n.name, str(p.relative_to(ROOT)))
    blob = "\n".join(p.read_text() for p in src.rglob("*.py") if "__pycache__" not in str(p))
    for name, where in sorted(defs.items()):
        if blob.count(name) > 1:
            continue
        kind = ("framework-dispatched" if any(h in name for h in VALIDATOR_HINTS)
                else "NO CALLER")
        if kind == "NO CALLER":
            failures.append(("REPORT", "P5 reachability", f"{name} ({where}) — no caller in src/"))


for fn in (p1_reachable, p2_discriminates, p3_within_weight, p4_floor_below_ceiling, p5_reachability):
    fn()

print(f"{'POLICY':<8} {'PROPERTY':<22} DETAIL")
print("-" * 100)
for policy, prop, detail in failures:
    print(f"{policy:<8} {prop:<22} {detail}")
gating = [f for f in failures if f[0] == "FAIL"]
print("-" * 100)
print(f"{len(failures)} findings — {len(gating)} gate the build, {len(failures)-len(gating)} report only")
sys.exit(1 if gating else 0)
