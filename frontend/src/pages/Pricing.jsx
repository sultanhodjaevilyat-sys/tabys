import { useState } from 'react'
import { useSearchParams } from 'react-router-dom'
import { api, tenge } from '../api.js'
import { useApi } from '../useApi.js'
import { Loader, PageHeader } from '../components/ui.jsx'

export default function Pricing() {
  const { data, error, loading } = useApi('/billing/plans')
  const [params] = useSearchParams()
  const [email, setEmail] = useState('')
  const [busy, setBusy] = useState('')
  const [err, setErr] = useState('')
  if (loading || error) return <Loader error={error} />

  async function buy(plan) {
    setErr('')
    if (email && !/^\S+@\S+\.\S+$/.test(email)) return setErr('Проверьте e-mail')
    setBusy(plan)
    try {
      const r = await api('/billing/checkout', { method: 'POST', body: { plan, email } })
      window.location.href = r.url // переход на страницу оплаты Stripe
    } catch (e) {
      setErr(e.message)
      setBusy('')
    }
  }

  return (
    <>
      <PageHeader title="Тарифы">Оплата подписки через Stripe Checkout (тестовый режим). Тестовая карта: 4242 4242 4242 4242, любая будущая дата, любой CVC.</PageHeader>
      {params.get('canceled') && <div className="card error">Оплата отменена — можно попробовать снова.</div>}
      <label className="email">E-mail для чека (необязательно)
        <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} placeholder="owner@cafe.kz" />
      </label>
      {err && <div className="card error">{err}</div>}
      <div className="grid3">
        {data.map((p) => (
          <div className={`card plan ${p.id === 'business' ? 'featured' : ''}`} key={p.id}>
            {p.id === 'business' && <span className="tag">Популярный</span>}
            <h3>{p.name}</h3>
            <div className="price">{tenge(p.price)}<span>/мес</span></div>
            <ul>{p.features.map((f) => <li key={f}>✓ {f}</li>)}</ul>
            <button className="btn" disabled={!!busy} onClick={() => buy(p.id)}>{busy === p.id ? 'Переходим к оплате…' : 'Оформить подписку'}</button>
          </div>
        ))}
      </div>
    </>
  )
}
