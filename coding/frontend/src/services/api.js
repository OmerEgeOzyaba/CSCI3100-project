import axios from 'axios'

// Python middleware
const API = axios.create({
  baseURL: 'http://localhost:5001',
  withCredentials: true,
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
  }
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
  console.log("API: Login called")
  try {
    const response = await API.post('/api/auth/login', { email, password })
    console.log("API: Login response", response.data)
    return response.data
  } catch (error) {
    console.error("API: Login error", error)
    throw error
  }
}
