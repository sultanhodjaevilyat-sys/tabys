import { Link } from 'react-router-dom'
import PosModel3D from '../components/PosModel3D.jsx'

const features = [
  ['🔍', 'Аудитор потерь', 'Сравнивает продажи по техкартам с фактическим расходом склада и проверяет кассу. Пишет простыми словами: «Говядина: перерасход 26 кг ≈ 106 000 ₸, вечер Вт и Чт».', '/audit'],
  ['📦', 'Прогноз и автозаказ', 'Считает спрос на неделю по дням недели и сам собирает заказ поставщикам — меньше списаний и стоп-листов.', '/warehouse'],
  ['📊', 'Советник по меню', 'Делит блюда на Звёзд, Лошадок, Загадок и Собак по популярности и марже и подсказывает, что делать с ценой.', '/insights'],
  ['🤖', 'AI-ассистент', 'Спросите «где я теряю деньги?» — агент сам вызовет нужные функции, возьмёт цифры из базы и ответит.', '/assistant'],
]

export default function Home() {
  return (
    <>
      <section className="hero">
        <div className="hero-text">
          <span className="eyebrow">Автоматизация кафе и ресторанов · Казахстан</span>
          <h1>Касса, которая <span className="accent">находит, где теряются деньги</span></h1>
          <p className="lead">
            iiko, Paloma 365 и Rosta записывают тысячи операций, но не говорят владельцу, где он теряет прибыль.
            Tabys делает это: аудит склада и кассы, прогноз закупок, анализ меню и AI-ассистент — в одной подписке.
          </p>
          <div className="actions">
            <Link to="/dashboard" className="btn">Открыть панель</Link>
            <Link to="/assistant" className="btn ghost">Спросить AI-ассистента</Link>
          </div>
        </div>
        <div className="hero-3d">
          <PosModel3D height={440} />
          <p className="caption">3D-модель рабочего места Tabys: моноблок с панелью владельца, принтер чеков, платёжный терминал и денежный ящик. Крутите мышкой, колесом — приближение.</p>
        </div>
      </section>

      <section className="grid4">
        {features.map(([icon, title, text, to]) => (
          <Link to={to} className="card feature" key={title}>
            <div className="feature-icon">{icon}</div>
            <h3>{title}</h3>
            <p>{text}</p>
          </Link>
        ))}
      </section>

      <section className="card compare">
        <h2>Почему не просто iiko / Paloma / Rosta?</h2>
        <table>
          <thead><tr><th>Функция</th><th>iiko</th><th>Paloma 365</th><th>Rosta</th><th>Tabys</th></tr></thead>
          <tbody>
            {[
              ['Касса, меню, склад', '✓', '✓', '✓', '✓'],
              ['QR-оплата и чаевые', 'партнёры', '—', '✓', '✓'],
              ['Аудит потерь склада и кассы', 'отчёты', 'отчёты', '—', 'автоматически'],
              ['Прогноз спроса и автозаказ', 'платный модуль', '—', '—', '✓'],
              ['AI-ассистент владельца', '—', '—', '—', '✓'],
            ].map((r) => <tr key={r[0]}>{r.map((c, i) => <td key={i}>{c}</td>)}</tr>)}
          </tbody>
        </table>
      </section>
    </>
  )
}
