from fnmatch import fnmatch
from typing import Literal

from pydantic import BaseModel


class RiskDecision(BaseModel):
    allowed: bool
    execution_mode: Literal["simulated", "approval_required", "live_blocked", "live"]
    reason: str


def assess_action_risk(
    action: str,
    target: str,
    autonomy_mode: str,
    allowlist: list[str],
) -> RiskDecision:
    if autonomy_mode == "sandbox":
        return RiskDecision(
            allowed=True,
            execution_mode="simulated",
            reason=f"{action} will run against sandbox adapters only.",
        )

    if autonomy_mode == "approval":
        return RiskDecision(
            allowed=False,
            execution_mode="approval_required",
            reason=f"{action} needs a human approval checkpoint before execution.",
        )

    if not any(fnmatch(target, pattern) for pattern in allowlist):
        return RiskDecision(
            allowed=False,
            execution_mode="live_blocked",
            reason=f"{target} is not allowlisted for {action}.",
        )

    return RiskDecision(
        allowed=True,
        execution_mode="live",
        reason=f"{action} may execute against the configured live integration.",
    )

