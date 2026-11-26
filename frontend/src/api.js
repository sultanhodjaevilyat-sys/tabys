// Обёртка над fetch: все запросы идут на /api (Vite проксирует их на FastAPI :8000)
export async function api(path, options = {}) {
  const res = await fetch(`/api${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
    body: options.body ? JSON.stringify(options.body) : undefined,
  })
  if (!res.ok) {
    let detail = res.statusText
    try { detail = (await res.json()).detail || detail } catch { /* not json */ }
    throw new Error(detail)
  }
  return res.json()
}

export const tenge = (n) => `${Math.round(n).toLocaleString('ru-RU')} ₸`
