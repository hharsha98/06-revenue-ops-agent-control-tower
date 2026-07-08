import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from backend.app.agents.supervisor import build_startup_revenue_plan
from backend.app.models.workflow import WorkflowRequest


def main() -> None:
    dataset_path = Path(__file__).with_name("dataset.jsonl")
    cases = [json.loads(line) for line in dataset_path.read_text().splitlines() if line.strip()]
    passed = 0

    for case in cases:
        plan = build_startup_revenue_plan(
            WorkflowRequest(objective=case["objective"], source="manual", autonomy_mode="sandbox")
        )
        actual_agents = {step.agent for step in plan.steps}
        expected_agents = set(case["expected_agents"])
        ok = expected_agents.issubset(actual_agents)
        passed += int(ok)
        print(f"{case['id']}: {'PASS' if ok else 'FAIL'}")

    print(f"score={passed}/{len(cases)}")
    if passed != len(cases):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
