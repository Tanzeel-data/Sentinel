# 🛡️ Sentinel

### AI Infrastructure Investigation & Safe Remediation Assistant

Sentinel is an AI-powered infrastructure operations assistant designed to investigate infrastructure issues, analyze telemetry, recommend evidence-based remediation, and verify the resulting system state.

The system combines **LLM-powered agents, LangGraph workflow orchestration, MCP-style tools, database telemetry, RAG, and safety guardrails** to provide a structured and safety-conscious infrastructure investigation workflow.

> **Core principle:** Sentinel investigates and recommends. Potentially disruptive remediation requires explicit human approval and is never blindly executed.

---

## 🚀 Key Features

- 🔍 **Infrastructure Monitoring**
  - Identifies servers experiencing elevated CPU or memory utilization.
  - Retrieves current server status and resource telemetry.

- 🧠 **AI Diagnosis**
  - Analyzes observed telemetry and system logs.
  - Identifies likely causes while explicitly representing uncertainty.
  - Separates observed evidence from assumptions.

- 🛠️ **Safe Remediation Recommendations**
  - Produces practical, evidence-based remediation recommendations.
  - Prioritizes investigation and reversible actions before disruptive actions.
  - Includes priority, risk, approval requirements, and verification steps.

- 🛡️ **Safety Guardrails**
  - Validates system commands before execution.
  - Restricts database operations to read-only queries.
  - Detects potentially destructive or disruptive actions.
  - Requires human approval for high-risk remediation.

- ✅ **Verification**
  - Re-checks infrastructure telemetry after the recommendation stage.
  - Determines whether an issue is resolved, partially resolved, unresolved, or supported by insufficient evidence.

- 🧩 **Agentic Workflow**
  - Monitoring → Diagnosis → Remediation → Verification
  - Orchestrated using LangGraph.

- 📚 **Knowledge Retrieval**
  - Uses a vector store and retrieval workflow to provide relevant operational knowledge when required.

- 🖥️ **Streamlit Interface**
  - Provides an interactive dashboard for submitting infrastructure requests and viewing investigation results.

---

## 🏗️ Architecture

```text
                         ┌─────────────────────┐
                         │    Streamlit UI     │
                         │   Infrastructure    │
                         │       Request       │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │   LangGraph         │
                         │   Orchestrator      │
                         └──────────┬──────────┘
                                    │
                ┌───────────────────┼───────────────────┐
                │                   │                   │
                ▼                   ▼                   ▼
        ┌──────────────┐    ┌──────────────┐    ┌──────────────┐
        │  Monitoring  │───▶│ Diagnostician│───▶│ Remediation  │
        │    Agent     │    │    Agent     │    │    Agent     │
        └──────────────┘    └──────────────┘    └──────┬───────┘
                                                        │
                                                        ▼
                                               ┌────────────────┐
                                               │ Safety         │
                                               │ Guardrails     │
                                               └───────┬────────┘
                                                       │
                                                       ▼
                                               ┌────────────────┐
                                               │ Verification   │
                                               │     Agent      │
                                               └────────────────┘

        ┌─────────────────────────────────────────────────────┐
        │                 Infrastructure Tools                │
        │                                                     │
        │  Database │ Logs │ Monitoring │ Commands │ Knowledge │
        └─────────────────────────────────────────────────────┘

        ┌─────────────────────────────────────────────────────┐
        │              Safety & Security Layer                 │
        │                                                     │
        │ Read-only SQL │ Command Validation │ Approval Gate  │
        └─────────────────────────────────────────────────────┘

🔄 Workflow
1. Monitor

Sentinel first gathers current infrastructure telemetry.

Example:

Server: SRV-002
Hostname: db-prod-1
Region: US-West
Status: ACTIVE
CPU: 88.5%
Memory: 92.3%

The monitoring stage identifies resource pressure based on configured operational thresholds.

2. Diagnose

The diagnostician analyzes the available evidence.

For example, elevated CPU and memory usage may indicate:

Heavy database queries
Long-running processes
Connection pressure
Increased workload
Resource constraints

Sentinel does not automatically treat these possibilities as confirmed root causes.

Instead, it reports uncertainty and recommends additional investigation when required.

3. Recommend Remediation

The remediation agent converts the diagnosis into a structured recommendation containing:

Observed issue
Recommended action
Priority
Risk / potential impact
Approval requirement
Verification step

Sentinel prioritizes non-disruptive investigation before actions such as service or server restarts.

4. Safety Validation

Every remediation recommendation is passed through Sentinel's safety layer.

Examples:

Safe investigation
        ↓
Allowed

Disruptive remediation
        ↓
Human approval required

Potentially destructive system commands are blocked.

Database access is restricted to read-only SELECT / WITH queries.

5. Verification

Sentinel checks the current telemetry and determines whether the issue remains active.

Possible outcomes include:

RESOLVED
PARTIALLY_RESOLVED
NOT_RESOLVED
INSUFFICIENT_EVIDENCE

If remediation was not executed because approval was required, Sentinel correctly reports that the issue remains unresolved rather than claiming success.

🛡️ Safety Model

Safety is a core design principle of Sentinel.

System Commands

Only approved diagnostic commands are allowed through the command tool.

Potentially dangerous commands such as:

shutdown
restart
delete

or commands containing shell chaining/operators are rejected or flagged for approval.

Database Queries

The database tool is intentionally read-only.

Allowed:

SELECT server_id, hostname
FROM servers;

Rejected:

DELETE FROM logs;
UPDATE servers
SET cpu_usage_percent = 0;
DROP TABLE servers;

This prevents the AI layer from directly modifying infrastructure state through the database tool.

Human Approval

Disruptive remediation requires explicit human approval.

Sentinel does not claim that an action was executed when it was only recommended.

This separation between:

Recommendation
      ≠
Execution

is fundamental to the system's safety design.

🧰 Technology Stack
Component	Technology
Language	Python
LLM	Google Gemini
Agent Framework	LangChain
Workflow Orchestration	LangGraph
UI	Streamlit
Database	SQL-based telemetry store
Vector Store	ChromaDB
Retrieval	RAG
Tool Layer	MCP-style infrastructure tools
Environment	Python virtual environment
Version Control	Git / GitHub
📁 Project Structure
sentinel/
│
├── app/
│   ├── agents/
│   │   ├── monitoring_agent.py
│   │   ├── diagnostician.py
│   │   ├── remediation.py
│   │   ├── verify.py
│   │   ├── router.py
│   │   ├── data_intelligence.py
│   │   └── incident_analysis_agent.py
│   │
│   ├── database/
│   │   ├── connection.py
│   │   ├── query.py
│   │   └── safe_sql.py
│   │
│   ├── genai/
│   │   └── client.py
│   │
│   ├── graph/
│   │   ├── graph.py
│   │   ├── nodes.py
│   │   ├── edges.py
│   │   ├── state.py
│   │   └── workflow.py
│   │
│   ├── mcp/
│   │   └── tools/
│   │       ├── commands.py
│   │       ├── database.py
│   │       ├── knowledge.py
│   │       └── logs.py
│   │
│   ├── rag/
│   │   ├── ingest.py
│   │   ├── knowledge_base.py
│   │   └── retriever.py
│   │
│   ├── safety/
│   │   └── guardrails.py
│   │
│   ├── tools/
│   │   ├── monitoring.py
│   │   ├── incident_tools.py
│   │   └── registry.py
│   │
│   └── vectorstore/
│       └── indexer.py
│
├── ui/
│   └── main.py
│
├── requirements.txt
├── .gitignore
└── README.md
⚙️ Installation
1. Clone the repository
git clone https://github.com/Tanzeel-data/Sentinel.git
cd Sentinel
2. Create a virtual environment

Windows:

python -m venv venv

Activate it:

.\venv\Scripts\Activate.ps1
3. Install dependencies
pip install -r requirements.txt
4. Configure environment variables

Create a local .env file:

GOOGLE_API_KEY=your_google_gemini_api_key

Never commit .env or API keys to GitHub.

▶️ Running Sentinel

From the project root:

streamlit run ui/main.py

The Streamlit interface will start locally and provide the Sentinel investigation dashboard.

🧪 Example Investigation

Example request:

Investigate servers with high CPU or memory usage
and recommend safe remediation.

Example workflow:

Monitor
   ↓
SRV-002 identified
CPU: 88.5%
Memory: 92.3%
   ↓
Diagnose
   ↓
Resource pressure confirmed
Root cause remains uncertain
   ↓
Recommend
   ↓
Investigate active queries/processes
   ↓
Safety validation
   ↓
Human approval required for disruptive actions
   ↓
Verify
   ↓
NOT_RESOLVED

NOT_RESOLVED is an expected result when disruptive remediation has not been executed because human approval is still required.

🔐 Security Considerations

Sentinel is designed with a defense-in-depth approach:

No arbitrary shell execution
Shell operators are rejected
Destructive commands are blocked
Database operations are read-only
Remediation recommendations are safety-validated
Human approval is required for disruptive actions
API credentials are kept outside source control
The system does not falsely report successful remediation

Sentinel is intended as an AI-assisted decision-support and infrastructure investigation system, not an autonomous production remediation engine.

📌 Current Scope

Sentinel currently focuses on:

Infrastructure telemetry investigation
Server resource monitoring
Log analysis
AI-assisted diagnosis
Evidence-based remediation recommendations
Safety validation
Human approval workflows
Post-remediation verification
Knowledge retrieval

Future extensions could include deeper infrastructure integrations, richer observability sources, approval interfaces, incident history, and controlled execution of approved remediation actions.

🎯 Project Objective

The goal of Sentinel is to demonstrate how agentic AI can be applied to infrastructure operations while maintaining strong safety boundaries.

Instead of allowing an LLM to directly modify infrastructure, Sentinel follows a controlled workflow:

Observe
  ↓
Understand
  ↓
Recommend
  ↓
Validate
  ↓
Approve
  ↓
Verify

This approach aims to combine the reasoning capabilities of modern AI agents with the reliability and control required for infrastructure operations.

👨‍💻 Author

Tanzeel Ur Rehman

BS Computer Science
Iqra University, Karachi

GitHub:
https://github.com/Tanzeel-data

📄 License

This project is intended for educational, research, and portfolio purposes.
