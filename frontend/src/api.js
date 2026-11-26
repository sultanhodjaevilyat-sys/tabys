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

// неразрывный пробел: знак ₸ никогда не переносится на новую строку отдельно от суммы
export const tenge = (n) => `${Math.round(n).toLocaleString('ru-RU')}\u00a0₸`

// Дробные числа по-русски: 26.55 → «26,55»
export const num = (n) => Number(n).toLocaleString('ru-RU', { maximumFractionDigits: 2 })

// Склонение: plural(93, 'удаление', 'удаления', 'удалений') → «удаления»
export function plural(n, one, few, many) {
  const a = Math.abs(Math.trunc(n)) % 100
  const b = a % 10
  if (b === 1 && a !== 11) return one
  if (b >= 2 && b <= 4 && (a < 12 || a > 14)) return few
  return many
}
