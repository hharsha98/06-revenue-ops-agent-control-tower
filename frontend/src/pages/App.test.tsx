import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, expect, test, vi } from "vitest";
import { App } from "./App";

const workflowResponse = {
  workflow_id: "wf_test123",
  status: "completed",
  objective: "Customer says SSO fails before security review. Answer from docs and escalate if needed.",
  autonomy_mode: "sandbox",
  plan: {
    workflow_id: "wf_test123",
    workflow_name: "customer-support-revenueops",
    steps: [],
    requires_approval: false,
    safety_notes: []
  }
};

const eventResponse = [
  {
    workflow_id: "wf_test123",
    sequence: 1,
    agent: "SupervisorAgent",
    event_type: "workflow.planned",
    message: "Planned 4 specialist agent steps.",
    tools: [],
    tool_calls: []
  },
  {
    workflow_id: "wf_test123",
    sequence: 2,
    agent: "OutreachAgent",
    event_type: "agent.completed",
    message: "Draft or send the customer-facing response according to autonomy mode.",
    tools: ["send_gmail"],
    tool_calls: [
      {
        tool_name: "send_gmail",
        target: "trial.customer@sandbox.example.com",
        mode: "sandbox",
        allowed: true,
        execution_mode: "simulated",
        summary: "Created sandbox Gmail draft to trial.customer@sandbox.example.com"
      }
    ]
  }
];

const overview = {
  product: "revenueops-control-tower",
  display_name: "RevenueOps Agent Control Tower",
  autonomy_mode: "sandbox",
  positioning: "This build has no public host.",
  recommended_badge: "Early",
  readiness: {
    recommended_badge: "Early",
    summary: "Native demo is working.",
    live: ["Operator tower"],
    early: ["Sandbox tools"],
    building: ["Public host"]
  },
  kpis: [
    { id: "open_alerts", label: "open alerts", value: "4", detail: "Seeded queue." },
    { id: "evidence_chunks", label: "evidence chunks", value: "6", detail: "In-memory store." }
  ],
  agents: [
    {
      name: "KnowledgeAgent",
      role: "Retrieves evidence.",
      tools: ["retrieve_docs"],
      status: "ready",
      last_message: "Waiting for a workflow."
    }
  ],
  alerts: [
    {
      id: "alert_sso_acme",
      severity: "critical",
      title: "Acme AI SSO failing before security review",
      detail: "Security questionnaire is tomorrow.",
      account: "Acme AI",
      owner_agent: "TicketTriageAgent",
      status: "open",
      source: "seed"
    }
  ],
  accounts: [
    {
      company: "Acme AI",
      segment: "B2B SaaS",
      team_size: 42,
      signal: "Security questionnaire is tomorrow.",
      fit_score: 86,
      plan: "enterprise-trial"
    }
  ],
  documents: [
    { source: "security-sso.md", chunks: 1, preview: "Enterprise customers can use SAML SSO." }
  ],
  scenarios: [
    {
      id: "sso-security-review",
      title: "SSO failure before security review",
      account: "Acme AI",
      source: "gmail",
      objective: "Customer says SSO fails before security review. Answer from docs and escalate if needed.",
      summary: "Cite the SSO guide."
    }
  ],
  recent_workflows: [],
  latest_events: [],
  audit_events: [],
  knowledge: { documents: 1, chunks: 1 }
};

function jsonResponse(body: unknown, ok = true) {
  return { ok, status: ok ? 200 : 500, json: async () => body };
}

beforeEach(() => {
  vi.restoreAllMocks();
});

test("loads tower KPIs from the API and renders a sandbox workflow timeline", async () => {
  const fetchMock = vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
    const url = String(input);
    if (url === "/health") return jsonResponse({ status: "ok", service: "tower", product: "revenueops-control-tower", autonomy_mode: "sandbox" });
    if (url === "/api/overview") return jsonResponse(overview);
    if (url === "/api/workflows/run" && init?.method === "POST") return jsonResponse(workflowResponse);
    if (url === "/api/workflows/wf_test123/events") return jsonResponse(eventResponse);
    if (url === "/api/documents/search") {
      return jsonResponse({
        query: "SSO security review",
        results: [
          { source: "security-sso.md", chunk_index: 0, content: "Collect the request ID before escalation.", score: 1 }
        ]
      });
    }
    throw new Error(`unexpected fetch ${url}`);
  });
  vi.stubGlobal("fetch", fetchMock);

  render(<App />);

  expect(await screen.findByText("4")).toBeInTheDocument();
  expect(screen.getByText("open alerts")).toBeInTheDocument();
  expect(screen.queryByText("96%")).not.toBeInTheDocument();
  expect(screen.getByText(/Acme AI SSO failing/i)).toBeInTheDocument();

  await userEvent.click(screen.getByRole("button", { name: /run sandbox workflow/i }));

  await waitFor(() => {
    expect(screen.getByText(/workflow wf_test123 completed/i)).toBeInTheDocument();
  });
  expect(screen.getByText(/Created sandbox Gmail draft/i)).toBeInTheDocument();
  expect(fetchMock).toHaveBeenCalledWith(
    "/api/workflows/run",
    expect.objectContaining({ method: "POST" })
  );
  expect(fetchMock).toHaveBeenCalledWith("/api/workflows/wf_test123/events", expect.anything());

  await userEvent.click(screen.getByRole("button", { name: "Evidence" }));
  await userEvent.click(screen.getByRole("button", { name: /search evidence/i }));
  expect(await screen.findByText(/Collect the request ID/i)).toBeInTheDocument();
});
