import React, { useState } from 'react'
import { requestNonce, verifySignature, setStoredSession } from './auth'

export default function Login({ onLogin }) {
  const [address, setAddress] = useState('')
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
      setAddress(checksum)
      setStatus('Requesting login nonce...')
      const nonceResponse = await requestNonce(checksum)
      const message = nonceResponse.nonce
      const signature = await window.ethereum.request({
        method: 'personal_sign',
        params: [message, checksum],
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

  return (
    <div style={{marginBottom:20}}>
      <h2>Customer Login</h2>
      <p>Authenticate with an Ethereum wallet to track your customer session.</p>
      <button onClick={connectWallet}>Login with Ethereum</button>
      {address && <div>Address: {address}</div>}
      {status && <div>{status}</div>}
      {error && <div style={{color:'red'}}>{error}</div>}
    </div>
  )
}
