import axios from 'axios'

// Python middleware
const API = axios.create({
  baseURL: 'http://localhost:5000',
})

// Automatically attach token
API.interceptors.request.use((config) => {
  const token = localStorage.getItem('authToken')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

export const login = async (email, password) => {
  const response = await API.post('/api/auth/login', { email, password })
  return response.data
}
