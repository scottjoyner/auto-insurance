const GATEWAY_BASE = import.meta.env.VITE_GATEWAY_BASE || "http://localhost:8004"

function createHeaders(token) {
  const headers = { "Content-Type": "application/json" }
  if (token) {
    headers.Authorization = `Bearer ${token}`
  }
  return headers
}

export async function fetchContracts(token) {
  const response = await fetch(`${GATEWAY_BASE}/policies/sample`, {
    headers: createHeaders(token),
  })
  if (!response.ok) {
    throw new Error(`Unable to fetch contract sample: ${response.statusText}`)
  }
  return response.json()
}

export async function fetchOutboxStats(token) {
  const response = await fetch(`${GATEWAY_BASE}/outbox/stats`, {
    headers: createHeaders(token),
  })
  if (!response.ok) {
    throw new Error(`Unable to fetch outbox stats: ${response.statusText}`)
  }
  return response.json()
}
