import React, { useState, useEffect } from 'react'
import SessionStatus from './components/SessionStatus'
import Stats from './components/Stats'
import Config from './components/Config'
import ActivityLog from './components/ActivityLog'
import ProjectInfo from './components/ProjectInfo'

export default function App() {
  const [sessions, setSessions] = useState({ agents: [] })
  const [stats, setStats] = useState({})
  const [activity, setActivity] = useState({ activity: [] })
  const [config, setConfig] = useState({})
  const [error, setError] = useState(null)

  const fetchJson = async (url) => {
    const res = await fetch(url)
    if (!res.ok) throw new Error(`HTTP ${res.status}`)
    return res.json()
  }

  useEffect(() => {
    const load = async () => {
      try {
        const [s, st, a, c] = await Promise.all([
          fetchJson('/api/sessions'),
          fetchJson('/api/stats'),
          fetchJson('/api/activity'),
          fetchJson('/api/config'),
        ])
        setSessions(s)
        setStats(st)
        setActivity(a)
        setConfig(c)
        setError(null)
      } catch (e) {
        setError(e.message)
      }
    }
    load()
    const interval = setInterval(load, 5000)
    return () => clearInterval(interval)
  }, [])

  return (
    <div className="app">
      <header className="app-header">
        <h1 className="app-title">Requiem Agents</h1>
        <p className="app-subtitle">Gothic Horror Multi-Agent System</p>
        {error && <div className="app-error">Connection error: {error}</div>}
      </header>
      <div className="app-grid">
        <div className="grid-item grid-item--full">
          <ProjectInfo />
        </div>
        <SessionStatus agents={sessions.agents || []} />
        <Stats data={stats} />
        <Config config={config} onUpdate={setConfig} />
        <div className="grid-item grid-item--full">
          <ActivityLog activity={activity.activity || []} />
        </div>
      </div>
    </div>
  )
}
