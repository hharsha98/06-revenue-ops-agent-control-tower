from typing import Literal

from pydantic import BaseModel


class EvaluationSummary(BaseModel):
    cases_passed: int
    cases_failed: int
    citation_coverage: float
    tool_call_success_rate: float
    average_latency_seconds: int


class EvaluationCase(BaseModel):
    name: str
    result: Literal["pass", "fail"]
    detail: str


class EvaluationReport(BaseModel):
    status: Literal["completed"]
    summary: EvaluationSummary
    cases: list[EvaluationCase]
