import { Link } from 'react-router-dom'

export default function NotFound() {
  return (
    <div className="card empty">
      <h1>404</h1>
      <p>Такой страницы нет — но и потерь тут тоже нет 🙂</p>
      <Link to="/" className="btn">На главную</Link>
    </div>
  )
}
