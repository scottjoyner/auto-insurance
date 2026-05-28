import React, { useEffect, useState } from 'react'
import { fetchClaims } from '../api'

function statusLabel(status) {
  switch (status) {
    case 'NEW': return 'New'
    case 'INVESTIGATING': return 'Investigating'
    case 'APPROVED': return 'Approved'
    case 'DENIED': return 'Denied'
    case 'REQUEST_INFO': return 'Needs Info'
    default: return status
  }
}

export default function ClaimsList({ token, onOpen }){
  const [claims, setClaims] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    async function loadClaims() {
      setLoading(true)
      setError('')
      try {
        const items = await fetchClaims(token)
        setClaims(items)
      } catch (exc) {
        setError(exc.message ?? 'Unable to load claims')
      } finally {
        setLoading(false)
      }
    }

    loadClaims()
  }, [token])

  return (
    <div>
      <h2>Claims Queue</h2>
      {loading && <div>Loading claims…</div>}
      {error && <div style={{color:'red'}}>{error}</div>}
      {!loading && claims.length === 0 && <div>No claims found.</div>}
      {!loading && claims.length > 0 && (
        <table border="1" cellPadding="8" style={{borderCollapse:'collapse', width:'100%'}}>
          <thead>
            <tr>
              <th>ID</th>
              <th>Claimant</th>
              <th>Product</th>
              <th>Severity</th>
              <th>Status</th>
              <th>Amount</th>
              <th>Submitted</th>
              <th>Action</th>
            </tr>
          </thead>
          <tbody>
            {claims.map((claim) => (
              <tr key={claim.id}>
                <td>{claim.id}</td>
                <td>{claim.claimant}</td>
                <td>{claim.product}</td>
                <td>{claim.severity}</td>
                <td>{statusLabel(claim.status)}</td>
                <td>${claim.amount}</td>
                <td>{new Date(claim.submitted_at).toLocaleString()}</td>
                <td><button onClick={() => onOpen(claim)}>Open</button></td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  )
}
