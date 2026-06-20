# Requiem Agents — PLAN.md

## Meta

- **Fecha:** 2026-06-20
- **Fase:** PLAN
- **Dependencia:** DESIGN.md v2 aprobado

## Visión General

Implementación por fases. Cada fase produce artefactos verificables. Las fases 0-3 son el MVP (Raven -> Necromancer -> Shade -> Revenant -> Raven). Las fases 4-6 son telemetría y frontend.

## Fase 0 — Project Setup

### 0.1 Estructura de directorios
- Crear estructura completa en ~/Requiem/
- Subdirectorios: raven/, requiem-mcp/, necromancer/, necromancer/shades/, shared/, dashboard/, dashboard-api/

### 0.2 Git + GitHub
- git init en ~/Requiem/
- Crear repo público MIT en GitHub (cuenta: DarkArty07)
- .gitignore: .env, .venv/, state.db, node_modules/, __pycache__/, *.pyc, .cache/
- LICENSE: MIT
- Commit inicial

### 0.3 Verificación
- ls -la ~/Requiem/ muestra estructura completa
- git status limpio
- git remote -v muestra repo GitHub
- grep -r "API_KEY\|SECRET\|TOKEN" . --exclude-dir=.git no encuentra secrets trackeados

## Fase 1 — Raven (hermes-agent v0.17)

### 1.1 Venv + instalación
```bash
python3.11 -m venv ~/Requiem/raven/.venv
source ~/Requiem/raven/.venv/bin/activate
pip install 'hermes-agent[mcp]'==0.17.0
```

Método: pip install en venv dedicado. Sin wrapper (regla de Chris). PATH-based resolution.

### 1.2 Configuración
- HERMES_HOME=~/Requiem/raven/
- config.yaml en ~/Requiem/raven/config.yaml
- Modelo: DeepSeek V4 Pro vía opencode-go
- MCP server: requiem-mcp (stdio, apunta a ~/Requiem/requiem-mcp/server.py)
- .env con OPENCODE_GO_API_KEY (gitignored)

### 1.3 SOUL.md de Raven
- System prompt con temática Horror Gótico
- Vibecoding + aprendizaje continuo + preferencias + skills
- NO lee código, NO debuggea
- Tools: delegate (MCP), memory, skills, session_status
- Hereda lo mejor de Hermes pero no es Hermes en totalidad

### 1.4 Verificación
- hermes --version muestra 0.17.0
- hermes config show lee de ~/Requiem/raven/
- hermes mcp test requiem-mcp conecta

## Fase 2 — Requiem MCP Server

### 2.1 Implementación
- server.py: MCP server (Python, stdio transport)
- tools.py: 5 tools MCP
  - activate_necromancer(project_root, project_name, formal_task) -> task_id
  - check_task_status(task_id) -> status + result
  - check_session_status() -> string visual
  - get_eval_report() -> métricas
  - shutdown_necromancer() -> confirmación
- requirements.txt: mcp, httpx, sqlite3

### 2.2 OpenCode Go client
- shared/opencode_client.py
- HTTP client para OpenCode Go API
- Endpoint: https://opencode.ai/zen/go/v1/chat/completions
- Formato: OpenAI Chat Completions
- Auth: Bearer token desde .env

### 2.3 Verificación
- python server.py arranca sin errores
- hermes mcp test requiem-mcp muestra tools discoverables
- activate_necromancer sin project_root devuelve error guard

## Fase 3 — Necromancer + Revenant + Shades

### 3.1 Necromancer
- necromancer.py: servicio orquestador
- Recibe tareas del MCP server
- Descompone en subtareas
- Spawnea Shades (asyncio)
- Invoca Revenant después de cada Shade
- Devuelve resultados al MCP server
- soul.md: system prompt del Necromancer

### 3.2 Revenant
- revenant.py: módulo auditor
- Invocado por Necromancer
- Su propio system prompt (revenant_soul.md)
- Tools: read_file, search_files (solo lectura)
- Veto power: PASS o FAIL con feedback
- 3 FAILS -> escala a Raven

### 3.3 Shades
- Shade of Programming: programming.md (system prompt)
  - Tools: read_file, write_file, terminal, search_files
  - Modelo: deepseek-v4-flash
- Shade of Research: research.md (system prompt)
  - Tools: read_file, search_files, web_search
  - Modelo: deepseek-v4-flash
- tools.py: implementación custom de tools (sin hermes-agent)

### 3.4 SQLite state
- shared/state.db
- Schema: agent_calls, sessions, tasks, audits
- Todas las llamadas registran tokens, costo, duración, resultado

### 3.5 Verificación
- Flujo end-to-end: Raven -> Necromancer -> Shade -> Revenant -> Raven
- Revenant rechaza output inválido -> Necromancer re-delega
- 3 rechazos -> escala a Raven
- Session status muestra datos reales
- SQLite registra todas las interacciones

## Fase 4 — Telemetría (Eval)

### 4.1 Metrics collection
- shared/eval.py: funciones de tracking
- Todas las llamadas a agentes registran en SQLite
- Métricas: tokens, costo, duración, pass/fail, reintentos, escaladas

### 4.2 Session monitor
- shared/session_monitor.py
- Consulta SQLite + OpenCode Go API
- Formatea salida visual: "glm-5.2 | 65.5K/256K | [███░░░] 26% | 51m | ⏲ 2m 42s"

### 4.3 Verificación
- get_eval_report() retorna métricas correctas
- Session status muestra datos en tiempo real
- SQLite tiene registros de todas las interacciones

## Fase 5 — Frontend Dashboard

### 5.1 React setup
- Vite + React en dashboard/
- package.json con dependencias
- vite.config.js con proxy a API

### 5.2 Gothic Horror CSS
- dashboard/src/styles/gothic.css
- Tema: #0a0a0a fondo, #c0c0c0 texto, #8b0000 acentos
- Serif gótica para títulos, mono para datos
- Angular, frío, sin bordes redondeados

### 5.3 Componentes
- SessionStatus.jsx: sesiones activas con formato visual
- Stats.jsx: tareas, pass rate, costo, tokens
- Config.jsx: modelo por agente, editar parámetros
- ActivityLog.jsx: eventos en vivo
- ProjectInfo.jsx: panel general de Requiem Agents

### 5.4 Dashboard API
- dashboard-api/server.py: FastAPI
- Endpoints: GET /sessions, GET /stats, GET /config, GET /activity, POST /config
- Lee de SQLite compartido
- Puerto 3001

### 5.5 Verificación
- localhost:3000 muestra dashboard
- Datos en tiempo real desde SQLite
- Tema Gothic Horror aplicado
- Configuración editable desde el panel

## Fase 6 — Integration and Testing

### 6.1 End-to-end test
- Usuario -> Raven -> Necromancer -> Shade of Programming -> Revenant PASS -> Raven -> Usuario
- Usuario -> Raven -> Necromancer -> Shade of Research -> Revenant FAIL x3 -> Escala a Raven

### 6.2 Security check
- git log --all --format='%H %s' | grep -i key no encuentra commits con secrets
- .gitignore cubre: .env, .venv/, state.db, node_modules/
- git secrets --scan limpio (si disponible)

### 6.3 README.md
- Descripción del proyecto
- Arquitectura
- Instalación paso a paso
- Uso básico
- Tema Horror Gótico

## Orden de Ejecución

```
Fase 0 (setup) -> Fase 1 (Raven) -> Fase 2 (MCP) -> Fase 3 (Necromancer)
                                                        |
                                                        v
Fase 6 (testing) <- Fase 5 (frontend) <- Fase 4 (eval) <-+
```

Las fases 0-3 son el MVP. Las fases 4-6 son telemetría y UI.
