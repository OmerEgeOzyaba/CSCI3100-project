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

export const signup = async (email, password, licenseKey) => {
  console.log("API: SignUp called")
  try {
    const response = await API.post('/api/auth/signup', { email, password, licenseKey })
    console.log("API: Signup response", response.data)
    return response
  } catch (error) {
    console.error("API: Signup error", error)
    throw error
  }
}

export const createGroup = async (name, description) => {
  console.log("API: createGroup called")
  try {
    const response = await API.post('/api/groups/', { name, description })
    console.log("API: createGroup response", response.data)
    return response
  } catch (error) {
    console.error("API: createGroup error", error)
    throw error
  }
}

export const updateGroup = async (id, name, description) => {
  console.log("API: updateGroup called")
  try {
    const response = await API.put(`/api/groups/${id}`, { name, description })
    console.log("API: updateGroup response", response.data)
    return response
  } catch (error) {
    console.error("API: updateGroup error", error)
    throw error
  }
}

export const getMembers = async (id) => {
  console.log("API: getMembers called")
  try {
    const response = await API.get(`/api/groups/${id}`)
    console.log("API: getMembers response", response.data)
    return response
  } catch (error) {
    console.error("API: getMembers error", error)
    throw error
  }
}
