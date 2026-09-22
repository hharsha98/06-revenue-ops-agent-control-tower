# Demo script

## 60-second story

This is a RevenueOps control tower for a startup operator. The queue already has
an Acme AI SSO failure, a pricing follow-up, and a stale onboarding guide. A
supervisor agent plans the work. Specialists retrieve company evidence, score the
account, triage urgency, and prepare sandbox Gmail, Slack, or GitHub actions.
The risk guard checks citations and autonomy. Nothing is sent. The audit trail
and a 3-case eval set are part of the same screen.

## Click path

1. `bash scripts/serve.sh`
2. Open `http://127.0.0.1:8060`.
3. Read the KPI strip, the open queue, and the book of business. These come from
   the API, not from placeholder copy.
4. Click **Run sandbox workflow**. The objective is the Acme AI security review.
5. On **Workflow**, read the timeline. Knowledge cites `security-sso.md`. Outreach
   shows a sandbox Gmail draft. Slack is a sandbox post. Status stays `completed`
   because sandbox drafts are allowed.
6. Open **Evidence** and search `pricing`. The pricing playbook should hit.
7. Open **Evals** and run the suite. Expect `3/3 passed`.
8. Open **Readiness**. The recommended studio badge is **Early**: the demo loop
   is live, the public host is not.

## What not to claim

- Do not call the keyword store pgvector. The schema exists; the running path does not use it.
- Do not say Gmail, Slack, or GitHub were actually called.
- Do not give this product another repository's Contabo or sslip URL.
