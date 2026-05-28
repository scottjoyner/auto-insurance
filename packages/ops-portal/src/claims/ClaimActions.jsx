import React, { useState } from 'react'
import { updateClaimStatus } from '../api'

const transitions = [
  { label: 'Approve', value: 'APPROVED' },
  { label: 'Deny', value: 'DENIED' },
  { label: 'Request Info', value: 'REQUEST_INFO' },
  { label: 'Escalate', value: 'INVESTIGATING' },
]

export default function ClaimActions({ claim, token, onUpdate }) {
  const [message, setMessage] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  async function runTransition(status) {
    if (!claim?.id) {
      setError('Cannot update missing claim')
      return
    }
    setLoading(true)
    setError('')
    setMessage('')

    try {
      const result = await updateClaimStatus(claim.id, status, token)
      if (result?.success) {
        onUpdate(result.claim || { ...claim, status })
        setMessage(`Claim updated to ${status}`)
      } else {
        setError(result?.message || 'Update failed')
      }
    } catch (exc) {
      setError(exc.message ?? 'Unable to update claim')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={{marginTop:24}}>
      <h3>Actions</h3>
      {message && <div style={{color:'green'}}>{message}</div>}
      {error && <div style={{color:'red'}}>{error}</div>}
      <div style={{display:'flex', gap:10, flexWrap:'wrap'}}>
        {transitions.map((transition) => (
          <button
            key={transition.value}
            onClick={() => runTransition(transition.value)}
            disabled={loading || claim.status === transition.value}
          >
            {transition.label}
          </button>
        ))}
      </div>
    </div>
  )
}
