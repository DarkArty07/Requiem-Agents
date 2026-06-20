import React from 'react'

function agentClass(name) {
  if (name === 'raven') return 'activity-agent--raven'
  if (name === 'necromancer') return 'activity-agent--necromancer'
  if (name === 'revenant') return 'activity-agent--revenant'
  if (name.startsWith('shade')) return 'activity-agent--shade'
  return ''
}

function resultClass(result) {
  if (result === 'pass') return 'activity-result activity-result--pass'
  if (result === 'fail') return 'activity-result activity-result--fail'
  if (result === 'escalated') return 'activity-result activity-result--escalated'
  return 'activity-result activity-result--default'
}

function formatTime(ts) {
  try {
    const d = new Date(ts)
    return d.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', second: '2-digit' })
  } catch {
    return ts || ''
  }
}

function truncate(s, max = 40) {
  if (!s) return '—'
  return s.length > max ? s.slice(0, max) + '…' : s
}

export default function ActivityLog({ activity }) {
  return (
    <div className="grid-item">
      <h2 className="grid-item__title">Activity Log</h2>
      <div className="activity-list">
        {activity.length === 0 ? (
          <p style={{ color: '#666', fontSize: '0.85rem', padding: 8 }}>
            No activity recorded yet
          </p>
        ) : (
          activity.map((entry, i) => (
            <div className="activity-entry" key={entry.timestamp + '-' + i}>
              <span className="activity-time">{formatTime(entry.timestamp)}</span>
              <span className={`activity-agent ${agentClass(entry.agent_name)}`}>
                {entry.agent_name}
              </span>
              <span className="activity-action">{truncate(entry.action)}</span>
              {entry.duration_seconds != null && (
                <span style={{ fontFamily: "'JetBrains Mono', monospace", fontSize: '0.65rem', color: '#555', minWidth: 40 }}>
                  {entry.duration_seconds.toFixed(1)}s
                </span>
              )}
              <span className={resultClass(entry.result)}>
                {entry.result ? entry.result.toUpperCase() : '—'}
              </span>
            </div>
          ))
        )}
      </div>
    </div>
  )
}
