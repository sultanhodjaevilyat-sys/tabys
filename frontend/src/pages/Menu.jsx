import { useState } from 'react'
import { num, tenge } from '../api.js'
import { useApi } from '../useApi.js'
import { Badge, Loader, PageHeader } from '../components/ui.jsx'

export default function Menu() {
  const { data, error, loading } = useApi('/menu')
  const [cat, setCat] = useState('Все')
  const [open, setOpen] = useState(null)
  if (loading || error) return <Loader error={error} />
  const cats = ['Все', ...new Set(data.map((d) => d.category))]
  const list = cat === 'Все' ? data : data.filter((d) => d.category === cat)
  return (
    <>
      <PageHeader title="Меню и техкарты">Себестоимость считается по техкарте: Σ (норма × цена ингредиента). Нажмите на блюдо, чтобы открыть техкарту.</PageHeader>
      <div className="filters">
        {cats.map((c) => <button key={c} className={c === cat ? 'chip active' : 'chip'} onClick={() => setCat(c)}>{c}</button>)}
      </div>
      <div className="grid3">
        {list.map((d) => (
          <div className="card dish" key={d.id} onClick={() => setOpen(open === d.id ? null : d.id)}>
            <div className="dish-top"><span className="emoji">{d.emoji}</span><Badge group={d.group} /></div>
            <h3>{d.name}</h3>
            <div className="dish-meta"><b>{tenge(d.price)}</b><span>себестоимость {tenge(d.cost)}</span><span>маржа {tenge(d.margin)}</span></div>
            <div className="muted">Продано за 4 недели: {d.sold} · доля себестоимости {num(d.food_cost_pct)} %</div>
            {open === d.id && (
              <table className="recipe">
                <thead><tr><th>Ингредиент</th><th>Норма</th><th>₸</th></tr></thead>
                <tbody>{d.recipe.map((r) => <tr key={r.ingredient}><td>{r.ingredient}</td><td>{num(r.qty)} {r.unit}</td><td>{num(r.cost)}</td></tr>)}</tbody>
              </table>
            )}
          </div>
        ))}
      </div>
    </>
  )
}
