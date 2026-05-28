import React, { useEffect, useState } from 'react'
import { fetchClaim } from '../api'
import ClaimActions from './ClaimActions'

export default function ClaimDetail({ claim, token, onBack }){
  const [detail, setDetail] = useState(claim)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    async function loadBenefit() {
      if (!claim?.id || !token) {
        setDetail(claim)
        return
      }

      setLoading(true)
      setError('')
      try {
        const fullClaim = await fetchClaim(claim.id, token)
        setDetail(fullClaim || claim)
      } catch (exc) {
        setError(exc.message ?? 'Unable to load claim detail')
        setDetail(claim)
      } finally {
        setLoading(false)
      }
    }

    loadBenefit()
  }, [claim, token])

  if (loading) {
    return <div>Loading claim detail…</div>
  }

  if (!detail) {
    return (
      <div>
        <button onClick={onBack}>Back to queue</button>
        <div>No claim detail available.</div>
      </div>
    )
  }

  return (
    <div>
      <button onClick={onBack}>Back to queue</button>
      <h2>Claim {detail.id}</h2>
      {error && <div style={{color:'red'}}>{error}</div>}
      <div><strong>Claimant:</strong> {detail.claimant}</div>
      <div><strong>Policy:</strong> {detail.policy_id}</div>
      <div><strong>Product:</strong> {detail.product}</div>
      <div><strong>Status:</strong> {detail.status}</div>
      <div><strong>Severity:</strong> {detail.severity}</div>
      <div><strong>Amount:</strong> ${detail.amount}</div>
      <div><strong>Submitted:</strong> {new Date(detail.submitted_at).toLocaleString()}</div>

      <h3 style={{marginTop:20}}>Description</h3>
      <p>{detail.description}</p>

      <h3>Evidence</h3>
      {detail.evidence?.length > 0 ? (
        <ul>
          {detail.evidence.map((item, index) => <li key={index}>{item}</li>)}
        </ul>
      ) : (
        <div>No evidence uploaded.</div>
      )}

      <h3 style={{marginTop:20}}>History</h3>
      {detail.history?.length > 0 ? (
        <ol>
          {detail.history.map((entry, index) => (
            <li key={index}>
              <strong>{new Date(entry.timestamp).toLocaleString()}:</strong> {entry.actor} — {entry.note}
            </li>
          ))}
        </ol>
      ) : (
        <div>No history available.</div>
      )}

      <ClaimActions claim={detail} token={token} onUpdate={setDetail} />
    </div>
  )
}
