import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import { AuthProvider } from './context/AuthContext';
import { JobsProvider } from './context/JobsContext';
import ProtectedRoute from './components/ProtectedRoute';
import Layout from './components/Layout';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import Jobs from './pages/Jobs';
import Profile from './pages/Profile';

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <JobsProvider>
          <Toaster
            position="top-right"
            toastOptions={{
              style: {
                background: 'rgba(15, 14, 26, 0.95)',
                color: '#f0eef6',
                border: '1px solid rgba(255, 255, 255, 0.08)',
                backdropFilter: 'blur(12px)',
                fontSize: '0.875rem',
                fontFamily: 'Inter, sans-serif',
              },
              success: {
                iconTheme: {
                  primary: '#10b981',
                  secondary: '#f0eef6',
                },
              },
              error: {
                iconTheme: {
                  primary: '#f43f5e',
                  secondary: '#f0eef6',
                },
              },
            }}
          />
          <Routes>
            <Route path="/login" element={<Login />} />
            <Route
              element={
                <ProtectedRoute>
                  <Layout />
                </ProtectedRoute>
              }
            >
              <Route path="/" element={<Dashboard />} />
              <Route path="/jobs" element={<Jobs />} />
              <Route path="/profile" element={<Profile />} />
            </Route>
            {/* Catch-all: redirect to dashboard */}
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </JobsProvider>
      </AuthProvider>
    </BrowserRouter>
  );
}
