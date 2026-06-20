import React from 'react'

function formatDuration(seconds) {
  if (seconds == null) return '—'
  if (seconds < 60) return `${Math.round(seconds)}s`
  if (seconds < 3600) return `${Math.floor(seconds / 60)}m ${Math.round(seconds % 60)}s`
  const h = Math.floor(seconds / 3600)
  const m = Math.floor((seconds % 3600) / 60)
  return `${h}h ${m}m`
}

function formatTokens(n) {
  if (n >= 1_000_000) return `${(n / 1_000_000).toFixed(1)}M`
  if (n >= 1000) return `${(n / 1000).toFixed(1)}K`
  return String(n)
}

function barClass(pct) {
  if (pct > 80) return 'token-bar__fill token-bar__fill--high'
  if (pct > 50) return 'token-bar__fill token-bar__fill--medium'
  return 'token-bar__fill token-bar__fill--low'
}

export default function SessionStatus({ agents }) {
  return (
    <div className="grid-item">
      <h2 className="grid-item__title">Active Agents</h2>
      {agents.length === 0 ? (
        <p style={{ color: '#666', fontSize: '0.85rem' }}>No agent data yet</p>
      ) : (
        <table className="agent-table">
          <thead>
            <tr>
              <th>Agent</th>
              <th>Model</th>
              <th>Tokens</th>
              <th>Context</th>
              <th>Duration</th>
            </tr>
          </thead>
          <tbody>
            {agents.map((a) => (
              <tr key={a.agent_name}>
                <td style={{ color: '#c0c0c0' }}>{a.agent_name}</td>
                <td style={{ color: '#999', fontSize: '0.72rem' }}>{a.model}</td>
                <td style={{ color: '#aaa' }}>
                  {formatTokens(a.total_tokens)}
                </td>
                <td style={{ minWidth: 120 }}>
                  <div className="token-bar">
                    <div
                      className={barClass(a.context_pct)}
                      style={{ width: `${Math.min(a.context_pct, 100)}%` }}
                    />
                  </div>
                  <span style={{ fontFamily: "'JetBrains Mono', monospace", fontSize: '0.65rem', color: a.context_pct > 80 ? '#ff4444' : '#888' }}>
                    {a.context_pct}%
                  </span>
                </td>
                <td style={{ color: '#888', fontSize: '0.75rem' }}>
                  {formatDuration(a.duration_seconds)}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  )
}
