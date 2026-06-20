# Requiem Agents — DESIGN.md v2

## Meta

- **Proyecto:** Requiem Agents
- **Creador:** Chris (prometeo)
- **Fecha:** 2026-06-20
- **Fase:** DESIGN → PLAN
- **Predecesor:** Aether Agents (cerrado — 306 sesiones, 26 decisiones, 6 Daimons)
- **Directorio:** /home/prometeo/Requiem/
- **Tema:** Horror Gótico
- **Licencia:** MIT

## Filosofía

Requiem Agents es una arquitectura multi-agente de próxima generación, diseñada a partir de las lecciones aprendidas de Aether Agents. Resuelve dos problemas de raíz:

1. **Costo excesivo en tokens de input** — el modelo caro ya no lee código
2. **Validación sin contrapeso** — el Auditor es peer del Orquestador, no subordinado

### Principios

- **Separación de costo:** modelo caro arriba (entender al humano), barato abajo (ejecutar)
- **Checks and balances:** el Auditor desafía al Orquestador de igual a igual
- **Especialización:** cada rol hace una sola cosa y la hace bien
- **Vibecoding:** el Asistente interpreta inspiración, no ejecuta tareas técnicas
- **Aprendizaje continuo:** si algo parece aprendizaje, lo es — se guarda
- **Orquestar con calidad:** el objetivo del proyecto es orquestar con calidad

## Arquitectura

```
USUARIO
   │
   ▼
┌──────────────────┐
│     RAVEN        │  ← Asistente (hermes-agent v0.17, modelo caro)
│  (vibecoding)    │     Razonamiento de alto nivel
│  NUNCA lee código │     Interpreta al usuario
│  Aprendizaje     │     Formaliza ideas
│  continuo        │     Memoria + skills + preferencias
└──────────────────┘
         │
    MCP: activate_necromancer(
      project_root, project_name, formal_task
    )
         │
         ▼
┌──────────────────┐     ┌──────────────────┐
│   NECROMANCER    │────►│    REVENANT       │
│  (orquestador)   │     │   (auditor)       │
│  Custom Python   │     │   Custom Python   │
│  Lee código      │     │   Peer del        │
│  Descompone      │     │   Necromancer     │
│  Delega Shades   │     │   Juzga outputs   │
│  Modelo medio    │     │   Veto power      │
│  On/off por Raven│     │   Modelo medio    │
└──────────────────┘     └──────────────────┘
    │        │        │
    ▼        ▼        ▼
┌───────┐ ┌───────┐ ┌───────┐
│Shade  │ │Shade  │ │Shade  │
│of Prog│ │of Res │ │of X   │
└───────┘ └───────┘ └───────┘
  flash      flash     flash
  ¢¢         ¢¢        ¢¢
```

## Stack Tecnológico

| Componente | Tecnología | Razón |
|------------|-----------|-------|
| Raven | hermes-agent v0.17.0 (pip, venv dedicado) | Único agente que usa el framework |
| Necromancer | Custom Python (OpenAI/Anthropic API style) | No necesita framework |
| Revenant | Custom Python (mismo estilo API) | No necesita framework |
| Shades | Custom Python (mismo estilo API) | Modelos baratos, tools limitadas |
| Comunicación | MCP (Raven ↔ Necromancer) | Estándar, soportado por hermes-agent v0.17 |
| Proveedor | OpenCode Go (único por ahora) | API estilo OpenAI, límites de uso claros |
| Telemetría | SQLite compartido | Tracking de todas las interacciones |
| Frontend | React + Vite + CSS Gothic Horror | Panel de control y configuración |
| Dashboard API | FastAPI (Python) | Lee de SQLite, sirve al frontend |
| Licencia | MIT | Público en GitHub |

## Roles

### Raven — El Asistente

- Framework: hermes-agent v0.17.0 (único que lo usa)
- Modelo: DeepSeek V4 Pro (o equivalente de razonamiento fuerte)
- Costo: $$$ — pero solo hace razonamiento de alto nivel
- Función: Vibecoding — interpretar al usuario, formalizar ideas, entregar resultados
- NUNCA hace: Leer código, debuggear, ejecutar comandos de implementación
- Memoria: Preferencias del usuario, historial, estilo (same tools que Hermes actual)
- Herramientas: Mínimas — delegación MCP, memoria, skills. NO herramientas técnicas
- Ciclo de vida: Persistente (sesión de hermes-agent)

Responsabilidades:
1. Entender lo que el usuario quiere (incluso cuando no lo dice claramente)
2. Formar preferencias del usuario desde lo que aprende (prioridad 1)
3. Aprendizaje continuo — si algo parece aprendizaje, lo es, guardarlo (prioridad 2)
4. Workflows y formas de hacer cosas van a skills que Raven crea (prioridad 3)
5. Formalizar ideas vagas en tareas estructuradas
6. Activar Necromancer con project_root + project_name + formal_task
7. Recibir resultados del Necromancer y presentarlos al usuario
8. Escalar al usuario cuando Necromancer y Revenant no se ponen de acuerdo (máx 3 rechazos)

Inspiración: Raven hereda lo mejor de Hermes para vibecodear cómodo, pero no es Hermes en totalidad.

### Necromancer — El Orquestador

- Framework: Custom Python (sin hermes-agent)
- Modelo: GLM-5.2 / Kimi K2 (modelo medio vía OpenCode Go)
- Costo: $$ — lee código pero con modelo más barato que Raven
- Función: Descomponer tareas, delegar a Shades, coordinar ejecución
- NUNCA hace: Hablar con el usuario, decidir arquitectura sin consultar
- Memoria: Codebase, patrones de delegación, qué Shade sirve para qué tarea
- Herramientas: read_file, search_files, terminal, spawn_shade, invoke_revenant
- Ciclo de vida: On/off — Raven lo activa, muere cuando Raven muere o lo apaga

Responsabilidades:
1. Recibir tareas formalizadas de Raven (con project_root obligatorio)
2. Leer código relevante para entender el contexto técnico
3. Siempre buscar la mejor manera de usar a sus Shades
4. Descomponer tareas complejas en subtareas atómicas
5. Asignar cada subtarea a la Shade correcta
6. Coordinar ejecución paralela cuando sea posible
7. Invocar a Revenant después de que cada Shade termine
8. Recoger resultados aprobados y devolverlos a Raven

### Revenant — El Auditor

- Framework: Custom Python (sin hermes-agent)
- Modelo: Modelo medio (mismo nivel que Necromancer vía OpenCode Go)
- Costo: $$ — valida pero no ejecuta
- Función: Peer del Necromancer — revisa, desafía, aprueba o rechaza
- NUNCA hace: Ejecutar código, hablar con el usuario, delegar a Shades directamente
- Memoria: Fallos pasados, edge cases recurrentes, criterios de calidad
- Herramientas: read_file, search_files (SOLO lectura)
- Ciclo de vida: Invocado por Necromancer — vive dentro del proceso de Necromancer

Poder de veto: El Revenant puede bloquear cualquier output que no pase validación. El Necromancer no puede sobreescribirlo. Solo Raven (escala al usuario) puede romper el empate.

### Shades — Los Agentes Ejecutores

- Framework: Custom Python (sin hermes-agent)
- Modelo: Flash / pequeño (mínimo costo vía OpenCode Go)
- Costo: ¢ — ejecución barata
- Nomenclatura: "Shade of X" — Shade of Programming, Shade of Research, etc.
- Función: Ejecutar tareas atómicas específicas de su dominio
- Tools: Limitadas por dominio — NO hacen cosas fuera de su scope

Shades iniciales:
- Shade of Programming: tools=[read_file, write_file, terminal, search_files], modelo=DeepSeek V4 Flash
- Shade of Research: tools=[read_file, search_files, web_search], modelo=DeepSeek V4 Flash

Shades de fase 2 (futuro): Shade of UX, Shade of Security

## Protocolo de Resolución de Conflictos

1. Necromancer produce output de Shade
2. Revenant revisa → PASA → devuelve a Raven → Usuario
3. Revenant revisa → FAIL → re-delega al Necromancer con feedback
4. Rechazo #1 → reintenta
5. Rechazo #2 → reintenta con más contexto
6. Rechazo #3 → escala a Raven con expediente completo
7. Raven decide (o consulta al usuario)

## Comunicación

### Raven ↔ Necromancer: MCP

Tools expuestas:
- activate_necromancer(project_root OBLIGATORIO, project_name OBLIGATORIO, formal_task) → task_id
- check_task_status(task_id) → status + result
- check_session_status() → string visual "modelo │ tokens │ % │ tiempo"
- get_eval_report() → métricas consolidadas
- shutdown_necromancer() → confirmación

Sin project_root y project_name, activate_necromancer no se ejecuta. Es un guard obligatorio.

### Necromancer ↔ Shades: invocación directa (async)

Necromancer invoca Shades como asyncio tasks. Cada Shade es una llamada API con su system prompt y tools.

### Necromancer ↔ Revenant: invocación de función

Revenant es una función que Necromancer llama después de cada Shade. Mismo proceso, distinto system prompt.

## Telemetría (Eval)

Métricas capturadas:
- Interacciones por agente
- Tokens por agente (input + output)
- Tasa de aprobación Revenant (% PASS vs FAIL)
- Tiempo por tarea (latencia)
- Reintentos por tarea
- Escaladas a Raven
- Presupuesto OpenCode Go ($ consumidos)
- Tareas por sesión

SQLite schema:
```sql
CREATE TABLE agent_calls (
    id INTEGER PRIMARY KEY,
    timestamp TEXT,
    session_id TEXT,
    agent_name TEXT,
    action TEXT,
    task_id TEXT,
    input_tokens INTEGER,
    output_tokens INTEGER,
    cost_usd REAL,
    duration_seconds REAL,
    result TEXT,
    metadata TEXT
);
```

## Frontend — Panel de Control

Stack: React (Vite) + CSS Gothic Horror + FastAPI (Python)
Puertos: localhost:3000 (React) + localhost:3001 (API)
Data source: SQLite compartido

Funciones: Sesiones activas, Estadísticas, Configuración, Log de actividad, Info del proyecto

Tema Horror Gótico:
- Colores: Fondo #0a0a0a, texto #c0c0c0, acentos #8b0000
- Tipografía: Serif gótica para títulos, mono para datos
- Bordes: Finos, 1px solid #333, glow rojo en hover
- Cards: Fondo #111, angular, sin bordes redondeados
- Animaciones: Fade-in lento, parpadeo sutil

## Memoria por Rol

- Raven: Preferencias del usuario, estilo, historial, skills → hermes-agent memory + skills
- Necromancer: Codebase, patrones de delegación, capacidades de Shades → SQLite + SOUL
- Revenant: Fallos pasados, edge cases, criterios de rechazo → SQLite + SOUL
- Shades: Conocimiento de dominio específico → System prompts

## Instalación de hermes-agent (Raven)

Método: pip install en venv dedicado (método primario recomendado)

```bash
python3.11 -m venv ~/Requiem/raven/.venv
source ~/Requiem/raven/.venv/bin/activate
pip install 'hermes-agent[mcp]'==0.17.0
export PATH="$HOME/Requiem/raven/.venv/bin:$PATH"
export HERMES_HOME="$HOME/Requiem/raven"
```

Sin wrapper (regla de Chris). PATH-based resolution. MCP SDK incluido con [mcp] extra.

## Estructura del Proyecto

```
/home/prometeo/Requiem/
├── DESIGN.md, PLAN.md, README.md, .gitignore, LICENSE
├── raven/           (hermes-agent v0.17: .venv, config.yaml, SOUL.md, .env, skills/, memory/)
├── requiem-mcp/     (MCP server: server.py, tools.py, requirements.txt)
├── necromancer/     (necromancer.py, revenant.py, shades/, soul.md, revenant_soul.md, tools.py)
├── shared/          (opencode_client.py, session_monitor.py, eval.py, state.db)
├── dashboard/       (React: src/, package.json, vite.config.js)
└── dashboard-api/   (FastAPI: server.py, requirements.txt)
```

## Comparación con Aether Agents

| Dimensión | Aether Agents | Requiem Agents |
|-----------|---------------|----------------|
| Agente principal | Hermes (hace todo) | Raven (solo interpreta) |
| Framework | Todos usan hermes-agent | Solo Raven |
| Lectura de código | Hermes $$$ | Necromancer $$ |
| Validación | Athena subordinada | Revenant peer con veto |
| Comunicación | ACP | MCP |
| Proveedor | Múltiples | OpenCode Go (único) |
| Motor inferencia | hermes-agent todos | Custom Python |
| Telemetría | No formal | SQLite + dashboard |
| Frontend | No | React + Gothic Horror |
| Costo | Alto | Bajo |
