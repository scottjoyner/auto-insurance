import React from 'react'

const sampleContracts = [
  { name: 'PolicyRegistry', address: '0xAa...01' },
  { name: 'AuditEventRegistry', address: '0xBb...02' }
]

export default function ContractsList(){
  return (
    <div>
      <h2>Deployed Contracts</h2>
      <table border="1" cellPadding="6">
        <thead><tr><th>Name</th><th>Address</th><th>Action</th></tr></thead>
        <tbody>
          {sampleContracts.map(c => (
            <tr key={c.address}>
              <td>{c.name}</td>
              <td>{c.address}</td>
              <td><button>View</button></td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
