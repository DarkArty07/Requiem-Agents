import React from 'react'

export default function ProjectInfo() {
  return (
    <div className="grid-item">
      <h2 className="grid-item__title">Project</h2>
      <div className="project-info__name">Requiem Agents</div>
      <p className="project-info__desc">
        A Gothic Horror multi-agent system built with Hermes Agent, MCP, and
        autonomous AI agents. Inspired by the dread architecture of dark
        cathedrals and the cold precision of machinery.
      </p>
      <a
        className="project-info__link"
        href="https://github.com/DarkArty07/Requiem-Agents"
        target="_blank"
        rel="noopener noreferrer"
      >
        GitHub → DarkArty07/Requiem-Agents
      </a>
      <div className="project-info__arch">
        <strong>Raven</strong> <span>→</span> Scans and delegates
        <br />
        <strong>MCP Server</strong> <span>→</span> Bridges Raven to Necromancer
        <br />
        <strong>Necromancer</strong> <span>→</span> Decomposes tasks, spawns Shades
        <br />
        <strong>Shades</strong> <span>→</span> Execute subtasks (Programming &amp; Research)
        <br />
        <strong>Revenant</strong> <span>→</span> Audits output with veto power
      </div>
    </div>
  )
}
