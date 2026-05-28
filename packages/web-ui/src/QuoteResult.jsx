import React, { useState } from 'react'
import { bindPolicy } from './api'

export default function QuoteResult({ quote, onBack, auth }){
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const [loading, setLoading] = useState(false)

  async function purchase() {
    if (!auth?.token) {
      setError('Please login with your wallet before purchasing.')
      return
    }

    setLoading(true)
    setError('')
    setSuccess('')
    try {
      const effective = new Date()
      const expiration = new Date()
      expiration.setFullYear(effective.getFullYear() + 1)

      const payload = {
        quote_id: quote.quote_id || quote.id,
        effective_date: effective.toISOString(),
        expiration_date: expiration.toISOString(),
        bind_method: 'HUMAN_APPROVAL',
        ai_confidence: 0.0,
      }
      const result = await bindPolicy(payload, auth.token)
      setSuccess(result.message || 'Policy bind request submitted')
    } catch (exc) {
      setError(exc.message ?? 'Purchase failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div>
      <h2>Quote Result</h2>
      <p>Quote ID: {quote.quote_id || quote.id}</p>
      <p>Product: {quote.product_id}</p>
      <p>Jurisdiction: {quote.jurisdiction}</p>
      <p>Premium: ${quote.total_premium ?? quote.premium}</p>
      {error && <div style={{color:'red'}}>{error}</div>}
      {success && <div style={{color:'green'}}>{success}</div>}
      <div style={{marginTop:10}}>
        <button onClick={onBack}>Back</button>
        <button style={{marginLeft:10}} onClick={purchase} disabled={loading}>
          {loading ? 'Submitting...' : 'Purchase'}
        </button>
      </div>
    </div>
  )
}
