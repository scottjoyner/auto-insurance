import React, { useEffect, useState } from 'react'
import { fetchPolicy } from './api'

const formatDate = (value) => value ? new Date(value).toLocaleDateString() : 'N/A'

export default function PolicyDetail({ policyId, auth, onBack }) {
  const [policy, setPolicy] = useState(null)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    async function loadPolicy() {
      setLoading(true)
      setError('')
      try {
        const data = await fetchPolicy(policyId, auth?.token)
        setPolicy(data)
      } catch (exc) {
        setError(exc.message ?? 'Unable to load policy details')
      } finally {
        setLoading(false)
      }
    }

    if (policyId) {
      loadPolicy()
    }
  }, [policyId, auth?.token])

  if (loading) {
    return <div>Loading policy details...</div>
  }

  if (error) {
    return (
      <div>
        <button onClick={onBack}>Back</button>
        <div style={{color:'red'}}>{error}</div>
      </div>
    )
  }

  if (!policy) {
    return (
      <div>
        <button onClick={onBack}>Back</button>
        <div>No policy selected.</div>
      </div>
    )
  }

  return (
    <div>
      <button onClick={onBack}>Back to policies</button>
      <h2>Policy {policy.policy_id || policy.id}</h2>
      <div style={{marginTop:10}}>
        <strong>Status:</strong> {policy.state}
      </div>
      <div>
        <strong>Product:</strong> {policy.product_id ?? policy.product}
      </div>
      <div>
        <strong>Total premium:</strong> {policy.total_premium ? `$${policy.total_premium}` : 'N/A'}
      </div>
      <div>
        <strong>Effective:</strong> {formatDate(policy.effective_date)}
      </div>
      <div>
        <strong>Expires:</strong> {formatDate(policy.expiration_date)}
      </div>

      <h3 style={{marginTop:20}}>Coverage</h3>
      {policy.coverages && policy.coverages.length > 0 ? (
        <table border="1" cellPadding="6" style={{borderCollapse:'collapse', width:'100%'}}>
          <thead>
            <tr><th>Type</th><th>Limit</th><th>Deductible</th><th>Premium</th></tr>
          </thead>
          <tbody>
            {policy.coverages.map((coverage, index) => (
              <tr key={index}>
                <td>{coverage.type}</td>
                <td>{coverage.limit}</td>
                <td>{coverage.deductible}</td>
                <td>{coverage.premium ? `$${coverage.premium}` : 'N/A'}</td>
              </tr>
            ))}
          </tbody>
        </table>
      ) : (
        <div>No coverage details available.</div>
      )}

      <h3 style={{marginTop:20}}>Audit Documents</h3>
      {policy.documents && policy.documents.length > 0 ? (
        <ul>
          {policy.documents.map((doc, index) => (
            <li key={index}>{doc.doc_type ?? doc.type}: {doc.metadata?.title ?? 'document'}</li>
          ))}
        </ul>
      ) : (
        <div>No documents available.</div>
      )}
    </div>
  )
}
