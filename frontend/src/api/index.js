import axios from 'axios'

const api = axios.create({ baseURL: '/api', timeout: 15000 })

api.interceptors.request.use((config) => {
  const raw = localStorage.getItem('user')
  if (raw) {
    try {
      const { id } = JSON.parse(raw)
      if (id) config.headers['X-User-Id'] = id
    } catch (e) {
      /* ignore */
    }
  }
  return config
})

export default api
