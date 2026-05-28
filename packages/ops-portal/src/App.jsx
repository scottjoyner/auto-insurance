import React, { useEffect, useState } from 'react'
import ClaimsList from './claims/ClaimsList'
import ClaimDetail from './claims/ClaimDetail'
import Login from './Login'
import { getStoredAddress, getStoredToken, clearStoredSession } from './auth'

export default function App(){
  const [view, setView] = useState('list')
  const [selected, setSelected] = useState(null)
  const [address, setAddress] = useState('')
  const [token, setToken] = useState('')

  useEffect(() => {
    const storedAddress = getStoredAddress()
    const storedToken = getStoredToken()
    if (storedAddress && storedToken) {
      setAddress(storedAddress)
      setToken(storedToken)
    }
  }, [])

  function handleLogin(session) {
    setAddress(session.address)
    setToken(session.token)
  }

  function handleLogout() {
    clearStoredSession()
    setAddress('')
    setToken('')
  }

  if (!token) {
    return (
      <div style={{padding:20}}>
        <Login onLogin={handleLogin} />
      </div>
    )
  }

  return (
    <div style={{padding:20}}>
      <header style={{display:'flex',gap:10,marginBottom:20}}>
        <button onClick={() => setView('list')}>Claims</button>
        <button onClick={() => setView('reports')}>Reports</button>
        <button onClick={handleLogout}>Logout</button>
      </header>

      <div style={{marginBottom:10}}>
        <strong>Authenticated as:</strong> {address}
      </div>

      {view === 'list' && (
        <ClaimsList token={token} onOpen={(c) => { setSelected(c); setView('detail') }} />
      )}

      {view === 'detail' && selected && (
        <ClaimDetail claim={selected} token={token} onBack={() => { setView('list'); setSelected(null) }} />
      )}
    </div>
  )
}
