import { tenge } from '../api.js'
import { useApi } from '../useApi.js'
import { Loader, PageHeader } from '../components/ui.jsx'

export default function Warehouse() {
  const { data, error, loading } = useApi('/forecast')
  if (loading || error) return <Loader error={error} />
  const order = data.purchase_order.filter((x) => x.to_buy > 0)
  const days = data.forecast[0].days.map((d) => d.day)
  return (
    <>
      <PageHeader title="Склад и прогноз">
        Прогноз = среднее продаж в такой же день недели за 4 недели × тренд. Заказ = прогноз × техкарта × 1,15 (страховой запас) − остаток.
      </PageHeader>
      <div className="card">
        <h2>Заказ поставщикам на неделю · {tenge(order.reduce((s, x) => s + x.sum_tenge, 0))}</h2>
        <table>
          <thead><tr><th>Продукт</th><th>Поставщик</th><th>Остаток</th><th>Хватит на</th><th>Нужно на неделю</th><th>Купить</th><th>Сумма</th></tr></thead>
          <tbody>
            {data.purchase_order.map((x) => (
              <tr key={x.ingredient_id} className={x.days_left < 3 ? 'warn' : ''}>
                <td>{x.ingredient}</td><td>{x.supplier}</td><td>{x.stock} {x.unit}</td>
                <td>{x.days_left} дн.</td><td>{x.need_week} {x.unit}</td>
                <td><b>{x.to_buy > 0 ? `${x.to_buy} ${x.unit}` : '—'}</b></td><td>{x.sum_tenge ? tenge(x.sum_tenge) : '—'}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <div className="card">
        <h2>Прогноз продаж на 7 дней (порций)</h2>
        <table>
          <thead><tr><th>Блюдо</th>{days.map((d) => <th key={d}>{d}</th>)}<th>Итого</th><th>Тренд</th></tr></thead>
          <tbody>
            {data.forecast.map((f) => (
              <tr key={f.dish_id}><td>{f.dish}</td>{f.days.map((d) => <td key={d.date}>{d.qty}</td>)}<td><b>{f.total}</b></td>
                <td className={f.trend >= 1 ? 'up' : 'down'}>{f.trend >= 1 ? '▲' : '▼'} {Math.round((f.trend - 1) * 100)} %</td></tr>
            ))}
          </tbody>
        </table>
      </div>
    </>
  )
}
