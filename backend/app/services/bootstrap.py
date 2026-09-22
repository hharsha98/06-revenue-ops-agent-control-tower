from threading import Lock

from backend.app.models.workflow import WorkflowRequest
from backend.app.services.audit_log import audit_log
from backend.app.services.catalog import SCENARIOS
from backend.app.services.knowledge import seed_knowledge_store
from backend.app.services.workflow_runner import run_agent_workflow

_lock = Lock()
_ready = False


def ensure_demo_ready() -> None:
    """Load evidence and replay the three demo scenarios once per process."""
    global _ready
    if _ready:
        return
    with _lock:
        if _ready:
            return
        seed_knowledge_store()
        audit_log.record(
            "system.ready",
            "Demo corpus loaded. Autonomy defaults to sandbox. No live credentials are configured.",
        )
        for scenario in SCENARIOS:
            run_agent_workflow(
                WorkflowRequest(
                    objective=scenario.objective,
                    source=scenario.source,
                    autonomy_mode="sandbox",
                    account=scenario.account,
                )
            )
        _ready = True
