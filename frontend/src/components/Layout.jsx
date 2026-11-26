import { useEffect, useState } from 'react'
import { NavLink, Outlet } from 'react-router-dom'
import { api } from '../api.js'

const links = [
  ['/dashboard', 'Панель'],
  ['/menu', 'Меню'],
  ['/warehouse', 'Склад и прогноз'],
  ['/audit', 'Аудитор потерь'],
  ['/insights', 'Матрица меню'],
  ['/assistant', 'AI-ассистент'],
  ['/pricing', 'Тарифы'],
]

export default function Layout() {
  const [open, setOpen] = useState(false)
  const [health, setHealth] = useState(null)
  useEffect(() => {
    // Показываем, в каком режиме работают AI и оплата: с настоящими ключами или в демо
    api('/health').then(setHealth).catch(() => setHealth({ offline: true }))
  }, [])
  return (
    <div className="app">
      <header className="nav">
        <NavLink to="/" className="logo" onClick={() => setOpen(false)}>
          <span className="logo-mark">T</span> Tabys
        </NavLink>
        <button className="burger" aria-label="Меню" onClick={() => setOpen(!open)}>☰</button>
        <nav className={open ? 'links open' : 'links'}>
          {links.map(([to, label]) => (
            <NavLink key={to} to={to} onClick={() => setOpen(false)}>{label}</NavLink>
          ))}
        </nav>
      </header>
      <main className="container">
        <Outlet />
      </main>
      <footer className="footer">
        <p><b>Tabys</b> — «табыс» по-казахски значит «прибыль». Проект группы IT-1 2315: Sultanhodjaev Ilyat, Budon Maxim, Amanzhol Ahmetzhan.</p>
        <p className="muted">Данные кафе тестовые (сгенерированы). React · FastAPI · PostgreSQL · Gemini · Stripe · three.js</p>
        {health && (
          <p className="status">
            {health.offline ? (
              <span className="dot off">● API недоступен — запустите бэкенд</span>
            ) : (
              <>
                <span className={health.ai === 'gemini' ? 'dot on' : 'dot demo'}>● AI: {health.ai === 'gemini' ? 'Gemini' : 'демо-режим'}</span>
                <span className={health.payments === 'stripe' ? 'dot on' : 'dot demo'}>● Оплата: {health.payments === 'stripe' ? 'Stripe test' : 'демо-режим'}</span>
              </>
            )}
          </p>
        )}
      </footer>
    </div>
  )
}
