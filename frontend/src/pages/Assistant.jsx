import { useEffect, useRef, useState } from 'react'
import { api } from '../api.js'
import { PageHeader } from '../components/ui.jsx'

const examples = ['Где я теряю деньги?', 'Что заказать поставщикам на неделю?', 'Какие блюда убрать или подорожать?', 'Расскажи про лагман', 'Как прошла неделя?']
const toolNames = {
  get_dashboard: 'выручка', get_stock_losses: 'аудит склада', get_cashier_anomalies: 'аудит кассы',
  get_forecast: 'прогноз', get_purchase_order: 'заказ поставщику', get_menu_matrix: 'матрица меню',
  get_dish_info: 'карточка блюда',
}

export default function Assistant() {
  const [messages, setMessages] = useState([
    { role: 'model', text: 'Здравствуйте! Я AI-ассистент Tabys. Спросите про выручку, потери, закупки или меню — я посмотрю данные и отвечу.' },
  ])
  const [input, setInput] = useState('')
  const [busy, setBusy] = useState(false)
  const endRef = useRef(null)
  useEffect(() => {
    // Фигурные скобки обязательны: эффект не должен ничего возвращать.
    // В новых браузерах scrollIntoView() возвращает Promise, и React принял бы его за функцию очистки.
    endRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  async function send(text) {
    const q = (text ?? input).trim()
    if (!q || busy) return
    setInput('')
    const history = messages.slice(1).map(({ role, text }) => ({ role, text }))
    setMessages((m) => [...m, { role: 'user', text: q }])
    setBusy(true)
    try {
      const r = await api('/agent/chat', { method: 'POST', body: { message: q, history } })
      setMessages((m) => [...m, { role: 'model', text: r.answer, tools: r.tools_used, mode: r.mode }])
    } catch (e) {
      setMessages((m) => [...m, { role: 'model', text: `Ошибка: ${e.message}` }])
    } finally {
      setBusy(false)
    }
  }

  return (
    <>
      <PageHeader title="AI-ассистент владельца">
        Агент на Gemini с вызовом функций (tool calling): сам решает, какие данные достать из базы — потери, прогноз, меню — и объясняет простыми словами.
      </PageHeader>
      <div className="card chat">
        <div className="messages">
          {messages.map((m, i) => (
            <div key={i} className={`msg ${m.role}`}>
              <div className="bubble">{m.text}</div>
              {m.tools?.length > 0 && (
                <div className="tools">
                  🔧 {m.tools.map((t) => toolNames[t] || t).join(', ')}
                  {m.mode === 'demo' && <span className="demo"> · демо-режим (нет ключа Gemini)</span>}
                </div>
              )}
            </div>
          ))}
          {busy && <div className="msg model"><div className="bubble typing">Анализирую данные…</div></div>}
          <div ref={endRef} />
        </div>
        <div className="examples">{examples.map((e) => <button key={e} className="chip" onClick={() => send(e)}>{e}</button>)}</div>
        <form className="composer" onSubmit={(e) => { e.preventDefault(); send() }}>
          <input value={input} onChange={(e) => setInput(e.target.value)} placeholder="Например: почему упала прибыль?" maxLength={1000} />
          <button className="btn" disabled={busy}>Отправить</button>
        </form>
      </div>
    </>
  )
}
