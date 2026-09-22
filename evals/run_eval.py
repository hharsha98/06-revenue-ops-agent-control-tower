import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def main() -> None:
    from backend.app.services.evals_runner import run_eval_suite
    from backend.app.services.knowledge import seed_knowledge_store

    seed_knowledge_store()
    report = run_eval_suite()
    for case in report["cases"]:
        print(f"{case['id']}: {'PASS' if case['ok'] else 'FAIL'}")
    print(f"score={report['score']}")
    if report["status"] != "passed":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
