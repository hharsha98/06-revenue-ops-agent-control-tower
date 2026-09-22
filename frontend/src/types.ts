export type AutonomyMode = "sandbox" | "approval" | "real";
export type WorkflowSource = "gmail" | "slack" | "github" | "manual";
export type TowerView = "tower" | "run" | "agents" | "evidence" | "alerts" | "audit" | "evals" | "readiness";

export type Health = {
  status: string;
  service: string;
  product: string;
  autonomy_mode: string;
  host?: string;
  port?: number;
};

export type Kpi = {
  id: string;
  label: string;
  value: string;
  detail: string;
};

export type AgentCard = {
  name: string;
  role: string;
  tools: string[];
  status: string;
  last_message: string;
};

export type Scenario = {
  id: string;
  title: string;
  account: string;
  source: WorkflowSource;
  objective: string;
  summary: string;
};

export type Alert = {
  id: string;
  severity: "critical" | "high" | "medium" | "low";
  title: string;
  detail: string;
  account: string;
  owner_agent: string;
  status: "open" | "acknowledged" | "resolved";
  source: "seed" | "live";
};

export type Account = {
  company: string;
  segment: string;
  team_size: number;
  signal: string;
  fit_score: number;
  plan: string;
};

export type DocumentRecord = {
  source: string;
  chunks: number;
  preview: string;
};

export type ToolCall = {
  tool_name: string;
  target: string;
  mode: AutonomyMode;
  allowed: boolean;
  execution_mode: string;
  summary: string;
  details?: Record<string, string>;
};

export type AgentEvent = {
  workflow_id?: string;
  sequence: number;
  agent: string;
  event_type: string;
  message: string;
  tools: string[];
  tool_calls: ToolCall[];
};

export type WorkflowRun = {
  workflow_id: string;
  status: string;
  objective?: string;
  autonomy_mode?: AutonomyMode;
  plan?: {
    workflow_id: string;
    workflow_name: string;
    steps: Array<{ agent: string; purpose: string; tools: string[] }>;
    requires_approval: boolean;
    safety_notes: string[];
  };
};

export type WorkflowSummary = {
  workflow_id: string;
  status: string;
  workflow_name: string;
  objective: string;
  autonomy_mode: string;
  agents: string[];
};

export type AuditEvent = {
  event_type: string;
  message: string;
  workflow_id?: string | null;
  created_at?: string | null;
};

export type Readiness = {
  recommended_badge: "Live" | "Early" | "Building";
  summary: string;
  live: string[];
  early: string[];
  building: string[];
};

export type Overview = {
  product: string;
  display_name: string;
  autonomy_mode: string;
  positioning: string;
  recommended_badge: Readiness["recommended_badge"];
  readiness: Readiness;
  kpis: Kpi[];
  agents: AgentCard[];
  alerts: Alert[];
  accounts: Account[];
  documents: DocumentRecord[];
  scenarios: Scenario[];
  recent_workflows: WorkflowSummary[];
  latest_events: AgentEvent[];
  audit_events: AuditEvent[];
  knowledge: { documents: number; chunks: number };
};

export type SearchResult = {
  source: string;
  chunk_index: number;
  content: string;
  score: number;
};

export type EvalCase = {
  id: string;
  ok: boolean;
  expected_agents: string[];
  actual_agents: string[];
  missing_agents: string[];
  evidence: Array<{ term: string; found: boolean; source: string | null }>;
};

export type EvalReport = {
  status: string;
  passed: number;
  total: number;
  score: string;
  cases: EvalCase[];
};
