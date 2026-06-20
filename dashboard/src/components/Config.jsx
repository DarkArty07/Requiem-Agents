import React, { useState } from 'react'

const MODEL_OPTIONS = [
  'deepseek-v4-pro',
  'deepseek-v4-flash',
  'glm-5.2',
  'kimi-k2',
]

const AGENT_LABELS = {
  raven: 'Raven',
  necromancer: 'Necromancer',
  revenant: 'Revenant',
  'shade-programming': 'Shade (Programming)',
  'shade-research': 'Shade (Research)',
}

export default function Config({ config, onUpdate }) {
  const [local, setLocal] = useState({ ...config })
  const [saving, setSaving] = useState(false)
  const [status, setStatus] = useState('')

  const handleChange = (agent, model) => {
    setLocal((prev) => ({ ...prev, [agent]: model }))
  }

  const handleSave = async () => {
    setSaving(true)
    setStatus('')
    try {
      const res = await fetch('/api/config', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ config: local }),
      })
      if (!res.ok) throw new Error(`HTTP ${res.status}`)
      const updated = await res.json()
      onUpdate(updated)
      setStatus('Saved successfully')
    } catch (e) {
      setStatus(`Error: ${e.message}`)
    } finally {
      setSaving(false)
    }
  }

  const hasChanges = Object.keys(local).some((k) => local[k] !== config[k])

  return (
    <div className="grid-item">
      <h2 className="grid-item__title">Configuration</h2>
      <div className="config-form">
        {Object.keys(AGENT_LABELS).map((agent) => (
          <div className="config-row" key={agent}>
            <label className="config-label" htmlFor={`cfg-${agent}`}>
              {AGENT_LABELS[agent]}
            </label>
            <select
              id={`cfg-${agent}`}
              className="config-select"
              value={local[agent] || ''}
              onChange={(e) => handleChange(agent, e.target.value)}
            >
              {MODEL_OPTIONS.map((m) => (
                <option key={m} value={m}>{m}</option>
              ))}
            </select>
          </div>
        ))}
        <button
          className="config-save"
          onClick={handleSave}
          disabled={saving || !hasChanges}
        >
          {saving ? 'Saving...' : 'Save Changes'}
        </button>
        {status && <div className="config-status">{status}</div>}
      </div>
    </div>
  )
}
