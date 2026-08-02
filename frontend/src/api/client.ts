import axios from 'axios'

const client = axios.create({
  baseURL: 'http://localhost:8000',
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000,
})

client.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response) {
      const message = error.response.data?.detail || error.response.data?.message || 'An error occurred'
      return Promise.reject(new Error(message))
    } else if (error.request) {
      return Promise.reject(new Error('Cannot connect to server. Please ensure the backend is running.'))
    }
    return Promise.reject(error)
  }
)

export default client
