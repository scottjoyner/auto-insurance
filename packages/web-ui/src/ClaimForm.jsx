import React, { useState } from 'react'
import { submitClaim } from './api'

export default function ClaimForm({ auth, onResult }) {
  const [policyId, setPolicyId] = useState('')
  const [lossDate, setLossDate] = useState('')
  const [incidentType, setIncidentType] = useState('Collision')
  const [description, setDescription] = useState('')
  const [estimatedAmount, setEstimatedAmount] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  async function submit(e) {
    e.preventDefault()
    setError('')
    setLoading(true)

    if (!policyId || !lossDate || !description) {
      setError('Please fill in the policy, date of loss, and description.')
      setLoading(false)
      return
    }

    try {
      const payload = {
        policy_id: policyId,
        loss_date: lossDate,
        incident_type: incidentType,
        description,
        estimated_amount: estimatedAmount ? Number(estimatedAmount) : null,
      }
      const claim = await submitClaim(payload, auth?.token)
      onResult(claim)
    } catch (exc) {
      setError(exc.message ?? 'Unable to submit claim')
    } finally {
      setLoading(false)
    }
  }

  return (
    <form onSubmit={submit} style={{maxWidth:640}}>
      <h2>Submit a Claim</h2>
      {error && <div style={{color:'red', marginBottom:10}}>{error}</div>}
      <div style={{marginBottom:10}}>
        <label>Policy ID</label><br />
        <input
          value={policyId}
          onChange={(e) => setPolicyId(e.target.value)}
          placeholder="P-0001"
          required
          style={{width:'100%'}}
        />
      </div>
      <div style={{display:'grid', gridTemplateColumns:'1fr 1fr', gap:10}}>
        <div>
          <label>Date of loss</label><br />
          <input
            type="date"
            value={lossDate}
            onChange={(e) => setLossDate(e.target.value)}
            required
            style={{width:'100%'}}
          />
        </div>
        <div>
          <label>Incident type</label><br />
          <select value={incidentType} onChange={(e) => setIncidentType(e.target.value)} style={{width:'100%'}}>
            <option>Collision</option>
            <option>Theft</option>
            <option>Vandalism</option>
            <option>Weather</option>
            <option>Other</option>
          </select>
        </div>
      </div>

      <div style={{marginTop:10}}>
        <label>Description</label><br />
        <textarea
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          required
          rows={5}
          style={{width:'100%'}}
        />
      </div>

      <div style={{marginTop:10}}>
        <label>Estimated damage amount</label><br />
        <input
          type="number"
          value={estimatedAmount}
          onChange={(e) => setEstimatedAmount(e.target.value)}
          placeholder="1500"
          style={{width:'100%'}}
        />
      </div>

      <div style={{marginTop:20}}>
        <button type="submit" disabled={loading}>
          {loading ? 'Submitting claim...' : 'Submit Claim'}
        </button>
      </div>
    </form>
  )
}
