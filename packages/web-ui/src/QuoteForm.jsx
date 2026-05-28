import React, { useState } from 'react'
import { requestQuote } from './api'

export default function QuoteForm({ onResult, auth }){
  const [fullName, setFullName] = useState('')
  const [year, setYear] = useState(2015)
  const [make, setMake] = useState('Toyota')
  const [model, setModel] = useState('Corolla')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  async function submit(e){
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      const payload = {
        applicant_data: {
          full_name: fullName,
          vehicle_year: year,
          vehicle_make: make,
          vehicle_model: model,
        },
        product_id: 'personal_auto',
        jurisdiction: 'NC',
        validity_days: 30,
      }
      const quote = await requestQuote(payload, auth?.token)
      onResult(quote)
    } catch (exc) {
      setError(exc.message ?? 'Quote request failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <form onSubmit={submit} style={{maxWidth:600}}>
      <h2>Get a Quote</h2>
      {error && <div style={{color:'red'}}>{error}</div>}
      <div>
        <label>Full name</label><br/>
        <input value={fullName} onChange={(e)=>setFullName(e.target.value)} required />
      </div>
      <div>
        <label>Year</label><br/>
        <input type="number" value={year} onChange={(e)=>setYear(Number(e.target.value))} />
      </div>
      <div>
        <label>Make</label><br/>
        <input value={make} onChange={(e)=>setMake(e.target.value)} />
      </div>
      <div>
        <label>Model</label><br/>
        <input value={model} onChange={(e)=>setModel(e.target.value)} />
      </div>
      <div style={{marginTop:10}}>
        <button type="submit" disabled={loading}>{loading ? 'Requesting...' : 'Request Quote'}</button>
      </div>
    </form>
  )
}
