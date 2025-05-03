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
    
    // Log token for debugging but don't store it here
    if (response.data && response.data.access_token) {
      console.log("Access token received:", response.data.access_token)
    } else {
      console.error("No access_token found in response:", response.data)
    }
    
    return response.data
  } catch (error) {
    console.error("API: Login error", error)
    throw error
  }
}

export const signup = async (email, password, licenseKey) => {
  console.log("API: SignUp called")
  try {
    const response = await API.post('/api/users/signup', { email, password, licenseKey })
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

export const getGroups = async () => {
  console.log("API: getGroups called")
  try {
    const response = await API.get(`/api/groups/`)
    console.log("API: getGroups response", response.data)
    return response
  } catch (error) {
    console.error("API: getGroups error", error)
    console.log("API: getGroups error", error.response.data)
    throw error
  }
}

export const leaveGroup = async (id) => {
  console.log("API: leaveGroup called")
  try {
    const response = await API.post(`/api/groups/${id}/leave`)
    console.log("API: leaveGroup response", response.data)
    return response
  } catch (error) {
    console.error("API: leaveGroup error", error)
    throw error
  }
}

export const logout = async () => {
  console.log("API: logout called")
  try {
    const token = localStorage.getItem('authToken');
    console.log("Token retrieved for logout:", token);
    
    if (!token || token === 'undefined') {
      console.error("Invalid token found:", token);
      throw new Error('No valid token found');
    }
    
    // Add token explicitly in headers to ensure it's sent correctly
    const response = await API.post(`/api/auth/logout`, {}, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });
    console.log("API: logout response", response.data)
    localStorage.removeItem('authToken');
    return response
  } catch (error) {
    console.error("API: logout error", error)
    throw error
  }
}

// Task API endpoints
export const getTasks = async () => {
  console.log("API: getTasks called")
  try {
    const response = await API.get('/api/tasks/')
    console.log("API: getTasks response", response.data)
    return response
  } catch (error) {
    console.error("API: getTasks error", error)
    throw error
  }
}

export const createTask = async (taskData) => {
  console.log("API: createTask called")
  try {
    const response = await API.post('/api/tasks/', taskData)
    console.log("API: createTask response", response.data)
    return response
  } catch (error) {
    console.error("API: createTask error", error)
    throw error
  }
}

export const updateTask = async (taskId, taskData) => {
  console.log("API: updateTask called")
  try {
    const response = await API.put(`/api/tasks/${taskId}`, taskData)
    console.log("API: updateTask response", response.data)
    return response
  } catch (error) {
    console.error("API: updateTask error", error)
    throw error
  }
}

export const deleteTask = async (taskId) => {
  console.log("API: deleteTask called")
  try {
    const response = await API.delete(`/api/tasks/${taskId}`)
    console.log("API: deleteTask response", response.data)
    return response
  } catch (error) {
    console.error("API: deleteTask error", error)
    throw error
  }
}

// Invitation API endpoints
export const getInvitations = async () => {
  console.log("API: getInvitations called")
  try {
    const response = await API.get('/api/invites/')
    console.log("API: getInvitations response", response.data)
    return response
  } catch (error) {
    console.error("API: getInvitations error", error)
    throw error
  }
}

export const sendInvitation = async (email, group_id) => {
  console.log("API: sendInvitation called")
  try {
    const response = await API.post('/api/invites/send', { email, group_id })
    console.log("API: sendInvitation response", response.data)
    return response
  } catch (error) {
    console.error("API: sendInvitation error", error)
    throw error
  }
}

export const acceptInvitation = async (group_id) => {
  console.log("API: acceptInvitation called")
  try {
    const response = await API.post('/api/invites/accept', { group_id })
    console.log("API: acceptInvitation response", response.data)
    return response
  } catch (error) {
    console.error("API: acceptInvitation error", error)
    throw error
  }
}

export const declineInvitation = async (group_id) => {
  console.log("API: declineInvitation called")
  try {
    const response = await API.post('/api/invites/decline', { group_id })
    console.log("API: declineInvitation response", response.data)
    return response
  } catch (error) {
    console.error("API: declineInvitation error", error)
    throw error
  }
}
