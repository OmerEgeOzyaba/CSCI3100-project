import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import Login from './pages/Login'
import Home from './pages/Home'
import SignUp from './pages/SignUp'
import GroupView from './pages/GroupView'
import MembersView from './pages/MembersView'
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

        {/* Signup route */}
        <Route path="/signup" element={<SignUp />} />
        
        {/* Login route - redirects to dashboard if already logged in */}
        <Route path="/login" element={<LoginRoute />} />
        
        {/* Dashboard route - protected, requires authentication */}
        <Route path="/dashboard" element={
          <ProtectedRoute>
            <Home />
          </ProtectedRoute>
        } />

        {/* GroupView route - protected, requires authentication */}
        <Route path="/group-edit" element={
          <ProtectedRoute>
            <GroupView />
          </ProtectedRoute>
        } />

        {/* GroupView route - protected, requires authentication */}
        <Route path="/members-view" element={
          <ProtectedRoute>
            <MembersView />
          </ProtectedRoute>
        } />
        
        {/* Catch-all route redirects to login */}
        <Route path="*" element={<Navigate to="/login" />} />
      </Routes>
    </Router>
  )
}

export default App
