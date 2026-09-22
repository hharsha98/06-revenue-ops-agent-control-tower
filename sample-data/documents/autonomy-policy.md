Sandbox mode simulates Gmail, Slack, and GitHub. The tool result is a draft, and
the audit log records that nothing left the machine. Approval mode stops before a
side effect and waits for an operator. Real mode may run only against allowlisted
domains, channels, and repositories, and only when credentials are configured.

This demo does not ship live credentials. Real mode fails closed. Prompt-injection
text in a customer objective is called out by the risk guard and is not a reason
to widen the allowlist.
