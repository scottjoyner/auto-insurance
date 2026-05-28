import React, { useEffect, useState } from 'react'
import { fetchPolicies } from './api'

const formatDate = (value) => value ? new Date(value).toLocaleDateString() : 'N/A'

export default function PolicyDashboard({ token, onOpenPolicy }) {
  const [policies, setPolicies] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [stateFilter, setStateFilter] = useState('ALL')

  useEffect(() => {
    async function loadPolicies() {
      setLoading(true)
      setError('')
      try {
        const items = await fetchPolicies(token)
        setPolicies(items)
      } catch (exc) {
        setError(exc.message ?? 'Unable to load policies')
      } finally {
        setLoading(false)
      }
    }

    if (token) {
      loadPolicies()
    }
  }, [token])

  const filtered = stateFilter === 'ALL'
    ? policies
    : policies.filter((policy) => policy.state === stateFilter)

  return (
    <div>
      <h2>My Policies</h2>
      <div style={{marginBottom:10}}>
        <label>Filter by state:&nbsp;</label>
        <select value={stateFilter} onChange={(e) => setStateFilter(e.target.value)}>
          <option value="ALL">All</option>
          <option value="ACTIVE">Active</option>
          <option value="PENDING_BIND">Pending Bind</option>
          <option value="CANCELLED">Cancelled</option>
          <option value="EXPIRED">Expired</option>
        </select>
      </div>
      {loading && <div>Loading policies...</div>}
      {error && <div style={{color:'red'}}>{error}</div>}
      {!loading && filtered.length === 0 && (
        <div>No policies found for the selected state.</div>
      )}
      {!loading && filtered.length > 0 && (
        <table border="1" cellPadding="8" style={{borderCollapse:'collapse', width:'100%'}}>
          <thead>
            <tr>
              <th>Policy ID</th>
              <th>State</th>
              <th>Product</th>
              <th>Premium</th>
              <th>Effective</th>
              <th>Expires</th>
              <th>Action</th>
            </tr>
          </thead>
          <tbody>
            {filtered.map((policy) => (
              <tr key={policy.policy_id || policy.id}>
                <td>{policy.policy_id || policy.id}</td>
                <td>{policy.state}</td>
                <td>{policy.product_id ?? policy.product}</td>
                <td>{policy.total_premium ? `$${policy.total_premium}` : 'N/A'}</td>
                <td>{formatDate(policy.effective_date)}</td>
                <td>{formatDate(policy.expiration_date)}</td>
                <td>
                  <button onClick={() => onOpenPolicy(policy.policy_id || policy.id)}>
                    View
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  )
}
