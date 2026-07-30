import axios from 'axios'

export const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Interceptor buat handle error secara global (opsional, tapi bagus buat konsistensi)
api.interceptors.response.use(
  (response) => response,
  (error) => {
    const message = error.response?.data?.detail || error.message || 'Terjadi kesalahan'
    console.error('[API Error]', message)
    return Promise.reject(error)
  },
)