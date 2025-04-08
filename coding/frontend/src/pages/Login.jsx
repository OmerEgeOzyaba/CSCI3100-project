import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  Container,
  TextField,
  Button,
  Typography,
  Box,
  Alert,
} from '@mui/material'
import { login } from '../services/api'

export default function Login() {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [success, setSuccess] = useState(false)
  const [loading, setLoading] = useState(false)
  const navigate = useNavigate()

  const handleLogin = async (e) => {
    e.preventDefault()
    setError('')
    setSuccess(false)
    setLoading(true)

    try {
      const data = await login(username, password)
      console.log('Login response:', data)
      // Store both tokens in localStorage
      localStorage.setItem('authToken', data.access_token)
      localStorage.setItem('refreshToken', data.refresh_token)
      
      // Redirect to dashboard page after successful login
      navigate('/dashboard')
    } catch (err) {
      console.error(err)
      if (err.response) {
        // Server responded with an error
        setError(`Login failed: ${err.response.data.error || 'Please check your credentials.'}`)
      } else if (err.request) {
        // Network error
        setError('Network error. Please check your connection and try again.')
      } else {
        setError('Login failed. Please try again.')
      }
      setSuccess(false)
    } finally {
      setLoading(false)
    }
  }

  return (
    <Container maxWidth="xs">
      <Box sx={{ mt: 8, display: 'flex', flexDirection: 'column', gap: 2 }}>
        <Typography variant="h5" align="center">Login</Typography>

        {error && <Alert severity="error">{error}</Alert>}

        <form onSubmit={handleLogin}>
          <TextField
            label="Username"
            fullWidth
            margin="normal"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            disabled={loading}
          />
          <TextField
            label="Password"
            type="password"
            fullWidth
            margin="normal"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            disabled={loading}
          />
          <Button 
            type="submit" 
            variant="contained" 
            fullWidth 
            sx={{ mt: 2 }}
            disabled={loading}
          >
            {loading ? 'Logging in...' : 'Login'}
          </Button>
        </form>
      </Box>
    </Container>
  )
}
