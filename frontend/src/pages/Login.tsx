import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { Mail, Lock, User, Loader2 } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import toast from 'react-hot-toast';

export default function Login() {
  const [isLogin, setIsLogin] = useState(true);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [fullName, setFullName] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const { login, register } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    try {
      if (isLogin) {
        await login(email, password);
        toast.success('Welcome back!');
        navigate('/');
      } else {
        await register(email, password, fullName);
        toast.success('Account created successfully!');
        navigate('/profile');
      }
    } catch {
      toast.error(
        isLogin
          ? 'Authentication failed. Check your credentials.'
          : 'Failed to create account. Email might already be in use.'
      );
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <>
      <div className="app-background">
        <div className="floating-orb" />
        <div className="floating-orb" />
        <div className="floating-orb" />
      </div>

      <div className="login-page">
        <motion.div
          initial={{ opacity: 0, y: 30, scale: 0.95 }}
          animate={{ opacity: 1, y: 0, scale: 1 }}
          transition={{ duration: 0.5, ease: [0.4, 0, 0.2, 1] }}
          className="login-card glass"
        >
          <div className="login-logo">
            <motion.div
              className="login-logo-icon"
              animate={{ rotate: [0, 5, -5, 0] }}
              transition={{ duration: 4, repeat: Infinity, ease: 'easeInOut' }}
            >
              C
            </motion.div>
            <h1>CareerOS</h1>
            <p>{isLogin ? 'Welcome back' : 'Create your account'}</p>
          </div>

          <form onSubmit={handleSubmit} className="login-form">
            <AnimatePresence mode="wait">
              {!isLogin && (
                <motion.div
                  key="fullname"
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: 'auto' }}
                  exit={{ opacity: 0, height: 0 }}
                  transition={{ duration: 0.25 }}
                  className="form-group"
                >
                  <label className="form-label">Full Name</label>
                  <div className="neu-input-icon">
                    <User className="icon" />
                    <input
                      type="text"
                      className="neu-input"
                      value={fullName}
                      onChange={(e) => setFullName(e.target.value)}
                      placeholder="John Doe"
                      required={!isLogin}
                    />
                  </div>
                </motion.div>
              )}
            </AnimatePresence>

            <div className="form-group">
              <label className="form-label">Email</label>
              <div className="neu-input-icon">
                <Mail className="icon" />
                <input
                  type="email"
                  className="neu-input"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="you@example.com"
                  required
                />
              </div>
            </div>

            <div className="form-group">
              <label className="form-label">Password</label>
              <div className="neu-input-icon">
                <Lock className="icon" />
                <input
                  type="password"
                  className="neu-input"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••"
                  required
                />
              </div>
            </div>

            <button
              type="submit"
              className="btn-primary"
              disabled={isSubmitting}
              style={{ width: '100%', justifyContent: 'center', marginTop: 8 }}
            >
              {isSubmitting ? (
                <>
                  <Loader2 className="spinner" size={18} />
                  {isLogin ? 'Signing in...' : 'Creating account...'}
                </>
              ) : (
                isLogin ? 'Sign In' : 'Create Account'
              )}
            </button>
          </form>

          <div className="login-toggle">
            {isLogin ? "Don't have an account? " : 'Already have an account? '}
            <span onClick={() => setIsLogin(!isLogin)}>
              {isLogin ? 'Sign up' : 'Sign in'}
            </span>
          </div>
        </motion.div>
      </div>
    </>
  );
}
