import { Link } from 'react-router-dom'
import { tenge } from '../api.js'
import { useApi } from '../useApi.js'
import { BarChart, Loader, PageHeader, StatCard } from '../components/ui.jsx'

export default function Dashboard() {
  const { data, error, loading } = useApi('/dashboard')
  if (loading || error) return <Loader error={error} />
  return (
    <>
      <PageHeader title="Панель владельца">Период: {data.period}</PageHeader>
      <div className="grid4">
        <StatCard label="Выручка за 7 дней" value={tenge(data.revenue)} hint={`${data.revenue_change_pct > 0 ? '+' : ''}${data.revenue_change_pct} % к прошлой неделе`} />
        <StatCard label="Чеков" value={data.orders} hint={`Средний чек ${tenge(data.avg_check)}`} />
        <StatCard label="Food cost" value={`${data.food_cost_pct} %`} hint="Норма для кафе 25–35 %" />
        <StatCard label="Найдено потерь за 4 недели" value={tenge(data.losses_28d)} hint={`${data.alerts} сигнала аудитора`} tone="danger" />
      </div>
      <div className="card">
        <h2>Выручка по дням</h2>
        <BarChart items={data.by_day} valueKey="revenue" labelKey="day" format={tenge} />
      </div>
      <div className="card tip">
        <b>Совет дня от Интеллекта:</b> найдено {data.alerts} сигнала о потерях. <Link to="/audit">Открыть аудитора →</Link>
        {' '}или <Link to="/assistant">спросить AI-ассистента</Link>.
      </div>
    </>
  )
}
