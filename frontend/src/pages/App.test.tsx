import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, expect, test, vi } from "vitest";
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

beforeEach(() => {
  vi.restoreAllMocks();
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
  expect(screen.getByText(/Created sandbox Gmail draft/i)).toBeInTheDocument();
  expect(fetchMock).toHaveBeenCalledWith(
    "/api/workflows/run",
    expect.objectContaining({ method: "POST" })
  );
  expect(fetchMock).toHaveBeenCalledWith("/api/workflows/wf_test123/events");
});

