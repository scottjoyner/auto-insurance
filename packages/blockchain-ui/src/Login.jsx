import React, { useState } from 'react'
import { requestNonce, verifySignature, setStoredSession } from './auth'

const DEFAULT_ADMIN_ADDRESS = '0x0000000000000000000000000000000000000000'

export default function Login({ onLogin }) {
  const [error, setError] = useState('')
  const [status, setStatus] = useState('')

  async function connectWallet() {
    setError('')
    if (!window.ethereum) {
      setError('No Ethereum wallet detected. Install MetaMask or use another provider.')
      return
    }

    try {
      const [account] = await window.ethereum.request({ method: 'eth_requestAccounts' })
      const checksum = account
      setStatus('Requesting login nonce...')
      const nonceResponse = await requestNonce(checksum)
      const signature = await window.ethereum.request({
        method: 'personal_sign',
        params: [nonceResponse.nonce, checksum],
      })
      setStatus('Verifying signature...')
      const result = await verifySignature(checksum, signature)
      setStoredSession(checksum, result.access_token)
      onLogin({ address: checksum, token: result.access_token })
      setStatus('Logged in successfully')
    } catch (exc) {
      setError(exc.message ?? 'Unable to login')
      setStatus('')
    }
  }

  function loginAsAdmin() {
    const address = DEFAULT_ADMIN_ADDRESS
    const token = 'sample-admin-token'
    setStoredSession(address, token)
    onLogin({ address, token })
    setStatus('Logged in as admin fallback user')
  }

  return (
    <div style={{marginBottom:20}}>
      <h2>Admin Login</h2>
      <p>Use MetaMask or a fallback admin account to authenticate.</p>
      <button onClick={connectWallet}>Login with Ethereum</button>
      <button style={{marginLeft:8}} onClick={loginAsAdmin}>Use Admin Fallback</button>
      {status && <div>{status}</div>}
      {error && <div style={{color:'red'}}>{error}</div>}
    </div>
  )
}
