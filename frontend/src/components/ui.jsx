// Переиспользуемые компоненты интерфейса
export function StatCard({ label, value, hint, tone }) {
  return (
    <div className={`card stat ${tone || ''}`}>
      <div className="stat-label">{label}</div>
      <div className="stat-value">{value}</div>
      {hint && <div className="stat-hint">{hint}</div>}
    </div>
  )
}

export function PageHeader({ title, children, how, howLabel = 'Как считается?' }) {
  return (
    <div className="page-head">
      <h1>{title}</h1>
      {children && <p className="lead">{children}</p>}
      {/* Формулы — под «Как считается?»: владельцу сначала нужен смысл, а не математика */}
      {how && <details className="how"><summary>{howLabel}</summary><p>{how}</p></details>}
    </div>
  )
}

export function Loader({ error }) {
  if (error) return <div className="card error">Ошибка: {error}. Проверьте, что бэкенд запущен (uvicorn на порту 8000).</div>
  return <div className="loader">Загрузка…</div>
}

export function Badge({ group }) {
  const cls = { 'Звезда': 'star', 'Лошадка': 'horse', 'Загадка': 'puzzle', 'Собака': 'dog' }[group] || ''
  const icon = { 'Звезда': '⭐', 'Лошадка': '🐴', 'Загадка': '❓', 'Собака': '🐶' }[group] || ''
  return <span className={`badge ${cls}`}>{icon} {group}</span>
}

export function BarChart({ items, valueKey, labelKey, format = (v) => v, short = format }) {
  const max = Math.max(...items.map((i) => i[valueKey]), 1)
  return (
    <div className="bars">
      {items.map((i) => (
        <div className="bar-col" key={i[labelKey]} title={format(i[valueKey])}>
          {/* значение видно сразу, без наведения мыши: на телефоне и для 40+ подсказка title незаметна */}
          <b className="bar-value">{short(i[valueKey])}</b>
          <div className="bar" style={{ height: `${(i[valueKey] / max) * 80}%` }} />
          <span>{i[labelKey]}</span>
        </div>
      ))}
    </div>
  )
}
