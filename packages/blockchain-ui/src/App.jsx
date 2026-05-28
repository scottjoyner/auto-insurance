import React, { useEffect, useState } from 'react'
import ContractsList from './ContractsList'
import SignerManagement from './SignerManagement'
import Login from './Login'
import { getStoredAddress, getStoredToken, clearStoredSession } from './auth'

export default function App(){
  const [address, setAddress] = useState('')
  const [token, setToken] = useState('')
  const [view, setView] = useState('contracts')

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
        <button onClick={() => setView('contracts')}>Contracts</button>
        <button onClick={() => setView('signer')}>Signer Management</button>
        <button onClick={handleLogout}>Logout</button>
      </header>

      <div style={{marginBottom:10}}>
        <strong>Authenticated as:</strong> {address}
      </div>

      {view === 'contracts' && <ContractsList token={token} />}
      {view === 'signer' && <SignerManagement token={token} />}
    </div>
  )
}
