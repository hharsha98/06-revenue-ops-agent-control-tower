import json

from backend.app.agents.supervisor import build_startup_revenue_plan
from backend.app.core.paths import repo_root
from backend.app.models.workflow import WorkflowRequest
from backend.app.services.knowledge import knowledge_store


def run_eval_suite() -> dict:
    dataset_path = repo_root() / "evals" / "dataset.jsonl"
    cases = [
        json.loads(line)
        for line in dataset_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    results: list[dict] = []
    passed = 0
    for case in cases:
        plan = build_startup_revenue_plan(
            WorkflowRequest(objective=case["objective"], source="manual", autonomy_mode="sandbox")
        )
        actual = [step.agent for step in plan.steps]
        expected = list(case["expected_agents"])
        missing = [agent for agent in expected if agent not in actual]
        evidence = []
        for term in case.get("required_evidence", []):
            hits = knowledge_store.search(term, limit=1)
            evidence.append(
                {
                    "term": term,
                    "found": bool(hits),
                    "source": hits[0].source if hits else None,
                }
            )
        ok = not missing
        passed += int(ok)
        results.append(
            {
                "id": case["id"],
                "ok": ok,
                "expected_agents": expected,
                "actual_agents": actual,
                "missing_agents": missing,
                "evidence": evidence,
            }
        )
    total = len(results)
    return {
        "status": "passed" if passed == total and total else "failed",
        "passed": passed,
        "total": total,
        "score": f"{passed}/{total}",
        "cases": results,
    }
