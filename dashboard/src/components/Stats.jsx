import React from 'react'

export default function Stats({ data }) {
  const totalCalls = data?.total_calls ?? 0
  const totalCost = data?.total_cost_usd ?? 0
  const passRate = data?.audit_pass_rate ?? 0
  const escalations = data?.escalations ?? 0

  return (
    <div className="grid-item">
      <h2 className="grid-item__title">Telemetry</h2>
      <div className="stats-grid">
        <div className="stat-item">
          <div className="stat-value">{totalCalls}</div>
          <div className="stat-label">Total Calls</div>
        </div>
        <div className="stat-item">
          <div className="stat-value">${totalCost.toFixed(4)}</div>
          <div className="stat-label">Total Cost</div>
        </div>
        <div className="stat-item">
          <div className="stat-value" style={{ color: passRate > 80 ? '#55cc55' : passRate > 50 ? '#ccaa33' : '#ff4444' }}>
            {passRate}%
          </div>
          <div className="stat-label">Audit Pass Rate</div>
        </div>
        <div className="stat-item">
          <div className="stat-value" style={{ color: escalations > 0 ? '#ff4444' : '#666' }}>
            {escalations}
          </div>
          <div className="stat-label">Escalations</div>
        </div>
      </div>
      {data?.by_agent && (
        <table className="agent-table" style={{ marginTop: 12 }}>
          <thead>
            <tr>
              <th>Agent</th>
              <th>Calls</th>
              <th>Tokens</th>
              <th>Avg Duration</th>
            </tr>
          </thead>
          <tbody>
            {Object.entries(data.by_agent).map(([name, s]) => (
              <tr key={name}>
                <td>{name}</td>
                <td>{s.calls}</td>
                <td>{(s.input_tokens + s.output_tokens).toLocaleString()}</td>
                <td>{s.avg_duration?.toFixed(1) ?? '—'}s</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  )
}
