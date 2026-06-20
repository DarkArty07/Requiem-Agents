# Requiem Agents

> *From darkness, creation.*

A **Gothic Horror** multi-agent orchestration system. Raven interprets user intent, Necromancer commands the Shades, and the Revenant audits every output before it reaches the user. Quality gates at every level.

## Architecture

```
                  ┌─────────────────────────────────────┐
                  │               USER                   │
                  └───────────────┬─────────────────────┘
                                  │
                          (vibecoding intent)
                                  │
                  ┌───────────────▼─────────────────────┐
                  │              RAVEN                   │
                  │   (hermes-agent v0.17, expensive)    │
                  │   Interprets, formalizes, delegates  │
                  └───────────────┬─────────────────────┘
                                  │
                    ┌─────────────▼─────────────┐
                    │      MCP PROTOCOL         │
                    │  (requiem-mcp server)     │
                    └─────────────┬─────────────┘
                                  │
                  ┌───────────────▼─────────────────────┐
                  │           NECROMANCER                │
                  │  (Custom Python, medium model)       │
                  │  Decomposes tasks, delegates to      │
                  │  Shades, coordinates execution       │
                  └───────┬───────────────────┬─────────┘
                          │                   │
              ┌───────────▼─────┐   ┌─────────▼───────────┐
              │  SHADE OF       │   │  SHADE OF            │
              │  PROGRAMMING    │   │  RESEARCH            │
              │  (write code,   │   │  (read code,         │
              │   run commands) │   │   investigate)       │
              └───────────┬─────┘   └─────────┬───────────┘
                          │                   │
                          └───────┬───────────┘
                                  │
                  ┌───────────────▼─────────────────────┐
                  │            REVENANT                  │
                  │  (Custom Python, medium model)       │
                  │  Audits, vetoes, escalates           │
                  └───────────────┬─────────────────────┘
                                  │
                  ┌───────────────▼─────────────────────┐
                  │        DASHBOARD (FastAPI + React)   │
                  │  Telemetry, session monitoring,      │
                  │  configuration management            │
                  └─────────────────────────────────────┘
```

## Agent Roles

| Agent | Role | Model | Tools |
|-------|------|-------|-------|
| **Raven** | Assistant — vibecoding, formalization | deepseek-v4-pro | Full hermes-agent |
| **Necromancer** | Orchestrator — decompose, delegate, coordinate | glm-5.2 | None (delegates to Shades) |
| **Revenant** | Auditor — review, veto, escalate | glm-5.2 | None (reviews output) |
| **Shade of Programming** | Executor — write code, run commands | deepseek-v4-flash | read_file, write_file, terminal, search_files |
| **Shade of Research** | Executor — read code, investigate | deepseek-v4-flash | read_file, search_files |

## Tech Stack

- **Orchestration:** [hermes-agent](https://hermes-agent.nousresearch.com) v0.17
- **Backend API:** FastAPI + Uvicorn
- **Frontend:** React + Vite
- **Database:** SQLite (telemetry)
- **Communication:** MCP (Model Context Protocol)

## Installation

```bash
# Clone the repository
git clone https://github.com/DarkArty07/Requiem-Agents.git
cd Requiem-Agents

# Python backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r dashboard-api/requirements.txt
pip install -r requirements-dev.txt  # development dependencies

# Frontend dashboard
cd dashboard
npm install
cd ..

# Set your environment
export OPENCODE_GO_API_KEY="your-key-here"
export REQUIEM_PROJECT_ROOT=$(pwd)
```

## Usage

### Start Raven (hermes-agent)

Configure hermes-agent to use the Raven profile:

```bash
hermes config set profile raven
hermes run
```

Raven connects to the MCP server which activates the Necromancer for task execution.

### Start Dashboard Backend

```bash
cd dashboard-api
python server.py
# Starts on http://localhost:3001
```

### Start Dashboard Frontend

```bash
cd dashboard
npm run dev
# Starts on http://localhost:3000
```

### Run Tests

```bash
pytest tests/ -v
```

## Project Structure

```
Requiem/
├── raven/
│   └── SOUL.md              # Raven system prompt
├── necromancer/
│   ├── soul.md               # Necromancer system prompt
│   ├── revenant_soul.md      # Revenant system prompt
│   ├── necromancer.py        # Orchestrator service
│   ├── revenant.py           # Auditor module
│   ├── tools.py              # Custom tool implementations
│   └── shades/
│       ├── programming.md    # Shade of Programming prompt
│       └── research.md       # Shade of Research prompt
├── requiem-mcp/
│   └── server.py             # MCP bridge server
├── shared/
│   ├── eval.py               # SQLite telemetry
│   ├── session_monitor.py    # Visual session status
│   └── opencode_client.py    # HTTP client for LLM API
├── dashboard-api/
│   └── server.py             # FastAPI backend
├── dashboard/
│   └── ...                   # React + Vite frontend
├── tests/
│   ├── conftest.py           # pytest fixtures
│   ├── test_eval.py          # Telemetry tests
│   ├── test_tools.py         # Custom tool tests
│   ├── test_dashboard_api.py # Dashboard API tests
│   └── test_necromancer_logic.py  # Structural tests
├── pytest.ini
└── requirements-dev.txt
```

## License

MIT — see [LICENSE](LICENSE).

## GitHub

[https://github.com/DarkArty07/Requiem-Agents](https://github.com/DarkArty07/Requiem-Agents)
