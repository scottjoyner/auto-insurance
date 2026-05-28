const AUTH_BASE = import.meta.env.VITE_AUTH_BASE || "http://localhost:8005"

export function getStoredToken() {
  return localStorage.getItem("auth_token")
}

export function getStoredAddress() {
  return localStorage.getItem("auth_address")
}

export function setStoredSession(address, token) {
  localStorage.setItem("auth_address", address)
  localStorage.setItem("auth_token", token)
}

export function clearStoredSession() {
  localStorage.removeItem("auth_address")
  localStorage.removeItem("auth_token")
}

export async function requestNonce(address) {
  const response = await fetch(`${AUTH_BASE}/auth/nonce?address=${encodeURIComponent(address)}`)
  if (!response.ok) {
    throw new Error(`Unable to request nonce: ${response.statusText}`)
  }
  return response.json()
}

export async function verifySignature(address, signature) {
  const response = await fetch(`${AUTH_BASE}/auth/verify`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ address, signature }),
  })
  if (!response.ok) {
    const text = await response.text()
    throw new Error(`Authentication failed: ${response.status} ${text}`)
  }
  return response.json()
}
