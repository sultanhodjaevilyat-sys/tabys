import { useState } from 'react'
import { NavLink, Outlet } from 'react-router-dom'

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
      </footer>
    </div>
  )
}
