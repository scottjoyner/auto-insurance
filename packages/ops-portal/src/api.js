import axios from 'axios'

const POLICY_BASE = import.meta.env.VITE_POLICY_BASE || "http://localhost:8002"

function createHeaders(token) {
  const headers = { "Content-Type": "application/json" }
  if (token) {
    headers.Authorization = `Bearer ${token}`
  }
  return headers
}

const sampleClaims = [
  {
    id: 'C-1001',
    claimant: 'Alice Johnson',
    product: 'Personal Auto',
    status: 'NEW',
    severity: 'MEDIUM',
    amount: 1200,
    submitted_at: '2026-05-24T10:12:00Z',
    policy_id: 'P-0001',
    description: 'Rear-end collision at low speed with minor damage.',
    evidence: ['Photo of bumper', 'Police report', 'Repair estimate'],
    history: [
      { timestamp: '2026-05-24T10:15:00Z', actor: 'system', note: 'Claim created' },
    ],
  },
  {
    id: 'C-1002',
    claimant: 'Bob Martin',
    product: 'Personal Auto',
    status: 'INVESTIGATING',
    severity: 'HIGH',
    amount: 5400,
    submitted_at: '2026-05-23T14:22:00Z',
    policy_id: 'P-0002',
    description: 'Single-vehicle rollover with suspected total loss.',
    evidence: ['Tow truck report', 'Photos of vehicle', 'Medical notes'],
    history: [
      { timestamp: '2026-05-23T14:25:00Z', actor: 'system', note: 'Claim created' },
      { timestamp: '2026-05-23T15:10:00Z', actor: 'adjuster', note: 'Assigned for investigation' },
    ],
  },
]

function normalizeClaim(claim) {
  return {
    ...claim,
    submitted_at: claim.submitted_at || claim.timestamp || new Date().toISOString(),
    history: claim.history || [],
  }
}

async function fetchFromBackend(path, token) {
  const response = await axios.get(path, { headers: createHeaders(token) })
  return response.data
}

export async function fetchClaims(token) {
  try {
    return await fetchFromBackend(`${POLICY_BASE}/claims`, token)
  } catch (error) {
    return sampleClaims.map(normalizeClaim)
  }
}

export async function fetchClaim(claimId, token) {
  try {
    return await fetchFromBackend(`${POLICY_BASE}/claims/${encodeURIComponent(claimId)}`, token)
  } catch (error) {
    return sampleClaims.find((claim) => claim.id === claimId) || null
  }
}

export async function updateClaimStatus(claimId, status, token) {
  try {
    const response = await axios.post(
      `${POLICY_BASE}/claims/${encodeURIComponent(claimId)}/status`,
      { status },
      { headers: createHeaders(token) }
    )
    return response.data
  } catch (error) {
    const claim = sampleClaims.find((item) => item.id === claimId)
    if (!claim) {
      throw new Error('Claim not found')
    }

    claim.status = status
    claim.history.push({
      timestamp: new Date().toISOString(),
      actor: 'ops_user',
      note: `Status updated to ${status}`,
    })
    return { success: true, claim }
  }
}
