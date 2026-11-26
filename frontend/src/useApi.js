import { useEffect, useState } from 'react'
import { api } from './api.js'

// Хук загрузки данных: { data, error, loading }
export function useApi(path) {
  const [state, setState] = useState({ data: null, error: null, loading: true })
  useEffect(() => {
    let alive = true
    api(path)
      .then((data) => alive && setState({ data, error: null, loading: false }))
      .catch((error) => alive && setState({ data: null, error: error.message, loading: false }))
    return () => { alive = false }
  }, [path])
  return state
}
