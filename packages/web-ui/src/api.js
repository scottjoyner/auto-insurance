const QUOTE_BASE = import.meta.env.VITE_API_BASE || "http://localhost:8001"
const POLICY_BASE = import.meta.env.VITE_POLICY_BASE || "http://localhost:8002"

function createHeaders(token) {
  const headers = { "Content-Type": "application/json" }
  if (token) {
    headers.Authorization = `Bearer ${token}`
  }
  return headers
}

export async function requestQuote(payload, token) {
  const response = await fetch(`${QUOTE_BASE}/quotes`, {
    method: "POST",
    headers: createHeaders(token),
    body: JSON.stringify(payload),
  })
  if (!response.ok) {
    const text = await response.text()
    throw new Error(`Quote request failed: ${response.status} ${text}`)
  }
  return response.json()
}

export async function bindPolicy(payload, token) {
  const response = await fetch(`${POLICY_BASE}/policies/bind`, {
    method: "POST",
    headers: createHeaders(token),
    body: JSON.stringify(payload),
  })
  if (!response.ok) {
    const text = await response.text()
    throw new Error(`Policy bind failed: ${response.status} ${text}`)
  }
  return response.json()
}

export async function fetchPolicies(token) {
  const response = await fetch(`${POLICY_BASE}/policies`, {
    headers: createHeaders(token),
  })
  if (!response.ok) {
    const text = await response.text()
    throw new Error(`Unable to load policies: ${response.status} ${text}`)
  }
  return response.json()
}

export async function fetchPolicy(policyId, token) {
  const response = await fetch(`${POLICY_BASE}/policies/${encodeURIComponent(policyId)}`, {
    headers: createHeaders(token),
  })
  if (!response.ok) {
    const text = await response.text()
    throw new Error(`Unable to load policy details: ${response.status} ${text}`)
  }
  return response.json()
}
