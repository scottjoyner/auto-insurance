import React, { useState } from 'react'

export default function SignerManagement(){
  const [signer, setSigner] = useState('0x000...')
  const [newKey, setNewKey] = useState('')

  function rotate(){
    // Placeholder — real rotation should call secure backend/Vault
    if(!newKey) return alert('Enter new key (simulated)')
    setSigner(newKey.slice(0,10) + '...')
    setNewKey('')
    alert('Signer rotated (simulated)')
  }

  return (
    <div>
      <h2>Signer Management</h2>
      <p>Current signer: {signer}</p>
      <div>
        <label>New signer key (paste or use Vault)</label><br/>
        <input value={newKey} onChange={(e)=>setNewKey(e.target.value)} style={{width:400}} />
      </div>
      <div style={{marginTop:8}}>
        <button onClick={rotate}>Rotate Signer (simulated)</button>
      </div>
    </div>
  )
}
