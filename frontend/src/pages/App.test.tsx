import { cleanup, render, screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, expect, test, vi } from "vitest";
import { App } from "./App";

const workflowResponse = {
  workflow_id: "wf_test123",
  status: "completed",
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

const knowledgeResponse = {
  query: "SSO request ID escalation",
  results: [
    {
      id: "security-sso.md:0",
      source: "security-sso.md",
      chunk_index: 0,
      content: "SSO failures should collect request ID, IdP domain, and timestamp before escalation.",
      score: 0.92
    }
  ]
};

const evalResponse = {
  status: "completed",
  summary: {
    cases_passed: 4,
    cases_failed: 0,
    citation_coverage: 0.91,
    tool_call_success_rate: 0.96,
    average_latency_seconds: 18
  },
  cases: [
    {
      name: "unsafe autonomous action",
      result: "pass",
      detail: "Real Gmail sends remain blocked unless allowlisted."
    }
  ]
};

beforeEach(() => {
  vi.restoreAllMocks();
  HTMLElement.prototype.scrollIntoView = vi.fn();
});

afterEach(() => {
  cleanup();
});

test("runs sandbox workflow and renders returned event timeline", async () => {
  const fetchMock = vi.fn()
    .mockResolvedValueOnce({ ok: true, json: async () => workflowResponse })
    .mockResolvedValueOnce({ ok: true, json: async () => eventResponse });
  vi.stubGlobal("fetch", fetchMock);

  render(<App />);

  await userEvent.click(screen.getByRole("button", { name: /run sandbox workflow/i }));

  await waitFor(() => {
    expect(screen.getByText(/workflow wf_test123 completed/i)).toBeInTheDocument();
  });
  expect(screen.getAllByText(/Created sandbox Gmail draft/i).length).toBeGreaterThan(0);
  const canvas = screen.getByLabelText(/workflow canvas/i);
  expect(within(canvas).getByText(/Canvas synced to wf_test123/i)).toBeInTheDocument();
  expect(within(canvas).getByText(/Outreach/i)).toBeInTheDocument();
  expect(within(canvas).getByText(/send_gmail · simulated/i)).toBeInTheDocument();
  const auditPanel = screen.getByLabelText(/governance audit trail/i);
  expect(within(auditPanel).getByText(/OutreachAgent/i)).toBeInTheDocument();
  expect(within(auditPanel).getByText(/send_gmail/i)).toBeInTheDocument();
  expect(within(auditPanel).getByText(/sandbox approved/i)).toBeInTheDocument();
  expect(fetchMock).toHaveBeenCalledWith(
    "/api/workflows/run",
    expect.objectContaining({ method: "POST" })
  );
  expect(fetchMock).toHaveBeenCalledWith("/api/workflows/wf_test123/events");
});

test("shows a detailed evaluation report for interviewer review", async () => {
  const fetchMock = vi.fn().mockResolvedValueOnce({ ok: true, json: async () => evalResponse });
  vi.stubGlobal("fetch", fetchMock);

  render(<App />);

  await userEvent.click(screen.getByRole("button", { name: /view eval report/i }));

  const report = screen.getByLabelText(/agent evaluation report/i);
  await waitFor(() => {
    expect(within(report).getByText(/4 passed/i)).toBeInTheDocument();
  });
  expect(within(report).getByText(/unsafe autonomous action/i)).toBeInTheDocument();
  expect(within(report).getByText(/Real Gmail sends remain blocked/i)).toBeInTheDocument();
  expect(fetchMock).toHaveBeenCalledWith("/api/evals/run", expect.objectContaining({ method: "POST" }));
});

test("searches the knowledge base and renders cited evidence", async () => {
  const fetchMock = vi.fn().mockResolvedValueOnce({ ok: true, json: async () => knowledgeResponse });
  vi.stubGlobal("fetch", fetchMock);

  render(<App />);

  await userEvent.click(screen.getByRole("button", { name: /search knowledge/i }));

  const consolePanel = screen.getByLabelText(/knowledge rag console/i);
  await waitFor(() => {
    expect(within(consolePanel).getByText(/score 0.92/i)).toBeInTheDocument();
  });
  expect(within(consolePanel).getAllByText(/security-sso.md/i).length).toBeGreaterThan(0);
  expect(within(consolePanel).getByText(/request ID, IdP domain/i)).toBeInTheDocument();
  expect(fetchMock).toHaveBeenCalledWith(
    "/api/documents/search",
    expect.objectContaining({ method: "POST" })
  );
});
