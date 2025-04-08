import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import Login from './pages/Login'
import Home from './pages/Home'
import './App.css'

function App() {
  // Check if user is logged in by looking for authToken in localStorage
  const isAuthenticated = () => {
    return localStorage.getItem('authToken') !== null
  }

  // Protected route component that redirects to login if not authenticated
  const ProtectedRoute = ({ children }) => {
    return isAuthenticated() ? children : <Navigate to="/login" />
  }

  // Redirect to dashboard if already logged in
  const LoginRoute = () => {
    return isAuthenticated() ? <Navigate to="/dashboard" /> : <Login />
  }

  return (
    <Router>
      <Routes>
        {/* Default route - redirect to login */}
        <Route path="/" element={<Navigate to="/login" />} />
        
        {/* Login route - redirects to dashboard if already logged in */}
        <Route path="/login" element={<LoginRoute />} />
        
        {/* Dashboard route - protected, requires authentication */}
        <Route path="/dashboard" element={
          <ProtectedRoute>
            <Home />
          </ProtectedRoute>
        } />
        
        {/* Catch-all route redirects to login */}
        <Route path="*" element={<Navigate to="/login" />} />
      </Routes>
    </Router>
  )
}

export default App
