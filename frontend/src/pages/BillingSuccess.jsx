import { useEffect, useState } from 'react'
import { Link, useSearchParams } from 'react-router-dom'
import { api } from '../api.js'
import { Loader, PageHeader } from '../components/ui.jsx'

// Статусы из базы показываем по-русски: «active» владельцу ни о чём не говорит
const STATUS = { active: 'активна', pending: 'ожидает оплаты', canceled: 'отменена' }

export default function BillingSuccess() {
  const [params] = useSearchParams()
  const [sub, setSub] = useState(null)
  const [error, setError] = useState(null)
  useEffect(() => {
    // Спрашиваем бэкенд: он проверит статус сессии в Stripe и активирует подписку
    api(`/billing/verify?session_id=${encodeURIComponent(params.get('session_id') || '')}`).then(setSub).catch((e) => setError(e.message))
  }, [params])
  if (!sub) return <Loader error={error} />
  return (
    <>
      <PageHeader title={sub.status === 'active' ? '🎉 Подписка активна' : 'Оплата обрабатывается'} />
      <div className="card">
        <p>Тариф: <b>{sub.plan_name}</b></p>
        <p>Статус: <b>{STATUS[sub.status] || sub.status}</b>{sub.mode === 'demo' && ' (демо-режим: ключ Stripe не задан, оплата сымитирована)'}</p>
        {sub.email && <p>Чек отправлен на: {sub.email}</p>}
        <Link to="/dashboard" className="btn">Перейти в панель</Link>
      </div>
    </>
  )
}
