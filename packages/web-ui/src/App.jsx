import React, { useEffect, useState } from 'react'
import Login from './Login'
import QuoteForm from './QuoteForm'
import QuoteResult from './QuoteResult'
import PolicyDashboard from './PolicyDashboard'
import PolicyDetail from './PolicyDetail'
import { getStoredAddress, getStoredToken, clearStoredSession } from './auth'

export default function App(){
  const [view, setView] = useState('home')
  const [quote, setQuote] = useState(null)
  const [auth, setAuth] = useState({ address: '', token: '' })
  const [message, setMessage] = useState('')
  const [selectedPolicyId, setSelectedPolicyId] = useState(null)

  useEffect(() => {
    const token = getStoredToken()
    const address = getStoredAddress()
    if (token && address) {
      setAuth({ address, token })
    }
  }, [])

  function handleLogin(session) {
    setAuth(session)
    setMessage(`Logged in as ${session.address}`)
  }

  function handleLogout() {
    clearStoredSession()
    setAuth({ address: '', token: '' })
    setMessage('Logged out')
    setView('home')
    setSelectedPolicyId(null)
  }

  function handlePolicyOpen(policyId) {
    setSelectedPolicyId(policyId)
    setView('policyDetail')
  }

  function handlePolicyBack() {
    setSelectedPolicyId(null)
    setView('policies')
  }

  return (
    <div style={{padding:20}}>
      <header style={{display:'flex',gap:10,marginBottom:20}}>
        <button onClick={() => setView('home')}>Home</button>
        <button onClick={() => setView('quote')}>Get Quote</button>
        <button onClick={() => setView('policies')}>My Policies</button>
        {auth.token && <button onClick={handleLogout}>Logout</button>}
      </header>

      {message && <div style={{marginBottom:10}}>{message}</div>}

      {auth.token ? (
        <div style={{marginBottom:20}}>
          <strong>Authenticated as:</strong> {auth.address}
        </div>
      ) : (
        <Login onLogin={handleLogin} />
      )}

      {view === 'home' && (
        <div>
          <h1>Auto Insurance — Customer Portal</h1>
          <p>Welcome. Use the quote flow to generate pricing, then bind a policy and review your active coverage.</p>
        </div>
      )}

      {view === 'quote' && (
        <QuoteForm onResult={(q) => { setQuote(q); setView('quoteResult') }} auth={auth} />
      )}

      {view === 'quoteResult' && quote && (
        <QuoteResult quote={quote} onBack={() => setView('quote')} auth={auth} />
      )}

      {view === 'policies' && (
        <PolicyDashboard token={auth.token} onOpenPolicy={handlePolicyOpen} />
      )}

      {view === 'policyDetail' && selectedPolicyId && (
        <PolicyDetail policyId={selectedPolicyId} auth={auth} onBack={handlePolicyBack} />
      )}
    </div>
  )
}
