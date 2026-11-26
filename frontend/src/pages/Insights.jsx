import { num, tenge } from '../api.js'
import { useApi } from '../useApi.js'
import { Badge, Loader, PageHeader } from '../components/ui.jsx'

const quads = [
  ['Загадка', 'Маржа высокая, продаж мало'],
  ['Звезда', 'Популярно и выгодно'],
  ['Собака', 'Мало продаж и низкая маржа'],
  ['Лошадка', 'Популярно, но маржа низкая'],
]

export default function Insights() {
  const { data, error, loading } = useApi('/menu-matrix')
  if (loading || error) return <Loader error={error} />
  return (
    <>
      <PageHeader title="Матрица меню">
        Метод Касаваны–Смита. Популярность высокая, если доля продаж ≥ {num(data.popularity_line_pct)} %.
        Маржа высокая, если ≥ средней по меню ({tenge(data.avg_margin)}).
      </PageHeader>
      <div className="matrix">
        <div className="axis-y">Маржа ↑</div>
        {quads.map(([g, hint]) => (
          <div className={`quad q-${g}`} key={g}>
            <div className="quad-head"><Badge group={g} /><span className="muted">{hint}</span></div>
            {data.items.filter((i) => i.group === g).map((i) => (
              <div className="pill" key={i.dish_id}>{i.emoji} {i.dish} <span className="muted">· {num(i.share)} % · {tenge(i.margin)}</span></div>
            ))}
          </div>
        ))}
        <div className="axis-x">Популярность →</div>
      </div>
      <div className="card">
        <h2>Что делать с каждым блюдом</h2>
        <table>
          <thead><tr><th>Блюдо</th><th>Группа</th><th>Цена</th><th>Маржа</th><th>Доля продаж</th><th>Совет</th></tr></thead>
          <tbody>
            {data.items.map((i) => (
              <tr key={i.dish_id}><td>{i.emoji} {i.dish}</td><td><Badge group={i.group} /></td><td>{tenge(i.price)}</td>
                <td>{tenge(i.margin)}</td><td>{num(i.share)} %</td><td>{i.advice}</td></tr>
            ))}
          </tbody>
        </table>
      </div>
    </>
  )
}
