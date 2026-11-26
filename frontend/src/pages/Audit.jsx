import { num, plural, tenge } from '../api.js'
import { useApi } from '../useApi.js'
import { Loader, PageHeader } from '../components/ui.jsx'

export default function Audit() {
  const { data, error, loading } = useApi('/audit')
  if (loading || error) return <Loader error={error} />
  const bad = data.stock.filter((x) => x.suspicious)
  const badCash = data.cashiers.filter((x) => x.suspicious)
  return (
    <>
      <PageHeader title="Аудитор потерь">
        Ожидаемый расход = продажи × норма по техкарте. Если фактический расход больше ожидаемого на 5 % и более — это сигнал.
        На кассе сравниваем удаления после пречека на 100 чеков между кассирами.
      </PageHeader>
      <div className="grid2">
        {bad.map((x) => (
          <div className="card incident" key={x.ingredient_id}>
            <span className="tag">Склад</span>
            <h3>{x.ingredient}: перерасход {num(x.overuse)} {x.unit} (+{num(x.overuse_pct)} %)</h3>
            <p className="big">≈ {tenge(x.loss_tenge)} за 4 недели</p>
            <p>Больше всего — <b>{x.worst_days.join(' и ')}</b>. Стоит проверить выход порций и вечерние смены.</p>
          </div>
        ))}
        {badCash.map((x) => (
          <div className="card incident" key={x.employee_id}>
            <span className="tag">Касса</span>
            <h3>{x.employee}: {x.voids} {plural(x.voids, 'удаление', 'удаления', 'удалений')} после пречека</h3>
            <p className="big">{tenge(x.void_amount)} · в {num(x.vs_others)} раза чаще коллег</p>
            <p>{num(x.per_100)} удаления на 100 чеков. Стоит сверить с камерами и попросить объяснительную.</p>
          </div>
        ))}
      </div>
      <div className="card">
        <h2>Все продукты</h2>
        <table>
          <thead><tr><th>Продукт</th><th>По техкарте</th><th>Факт</th><th>Разница</th><th>Потеря</th></tr></thead>
          <tbody>
            {data.stock.map((x) => (
              <tr key={x.ingredient_id} className={x.suspicious ? 'warn' : ''}>
                <td>{x.ingredient}</td><td>{num(x.expected)} {x.unit}</td><td>{num(x.actual)} {x.unit}</td>
                <td>{x.overuse_pct > 0 ? '+' : ''}{num(x.overuse_pct)} %</td><td>{tenge(x.loss_tenge)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </>
  )
}
