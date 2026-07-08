# Interview Demo Script

## 60-second story

"This is a RevenueOps agent control tower for startups. A founder can ask it to handle a
customer issue end-to-end. One supervisor agent plans the work, specialist agents retrieve
company knowledge, triage support urgency, draft customer communication, post internal updates,
and create GitHub issues. The important part is not just the agents; it is the production layer:
sandbox mode, allowlists, audit logs, evals, traces, Docker, Kubernetes, and Terraform."

## Demo scenario

Input:

> A trial customer from Acme AI says SSO is failing before tomorrow's security review. Find the
> right answer, alert the team, and create an engineering issue if docs are stale.

Expected workflow:

1. Supervisor creates a plan.
2. KnowledgeAgent retrieves SSO docs.
3. TicketTriageAgent marks urgency as high.
4. RiskGuardAgent checks citations and action permissions.
5. OutreachAgent drafts customer email.
6. EngineeringHandoffAgent creates a GitHub issue in sandbox mode.
7. Dashboard shows timeline, tasks, eval gates, and audit trail.

