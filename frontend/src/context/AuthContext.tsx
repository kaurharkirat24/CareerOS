import { createContext, useContext, useReducer, useEffect, ReactNode } from 'react';
import api from '../lib/api';

interface User {
  email: string;
  full_name: string | null;
}

interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
}

type AuthAction =
  | { type: 'SET_LOADING'; payload: boolean }
  | { type: 'LOGIN_SUCCESS'; payload: { user: User; token: string } }
  | { type: 'LOGOUT' }
  | { type: 'SET_USER'; payload: User };

const initialState: AuthState = {
  user: null,
  token: localStorage.getItem('token'),
  isAuthenticated: false,
  isLoading: true,
};

function authReducer(state: AuthState, action: AuthAction): AuthState {
  switch (action.type) {
    case 'SET_LOADING':
      return { ...state, isLoading: action.payload };
    case 'LOGIN_SUCCESS':
      return {
        ...state,
        user: action.payload.user,
        token: action.payload.token,
        isAuthenticated: true,
        isLoading: false,
      };
    case 'SET_USER':
      return {
        ...state,
        user: action.payload,
        isAuthenticated: true,
        isLoading: false,
      };
    case 'LOGOUT':
      return {
        ...state,
        user: null,
        token: null,
        isAuthenticated: false,
        isLoading: false,
      };
    default:
      return state;
  }
}

interface AuthContextType extends AuthState {
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string, fullName: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [state, dispatch] = useReducer(authReducer, initialState);

  // Hydrate user on mount if token exists
  useEffect(() => {
    const hydrate = async () => {
      const token = localStorage.getItem('token');
      if (!token) {
        dispatch({ type: 'SET_LOADING', payload: false });
        return;
      }
      try {
        const res = await api.get('/auth/me');
        dispatch({ type: 'SET_USER', payload: res.data });
      } catch {
        localStorage.removeItem('token');
        dispatch({ type: 'LOGOUT' });
      }
    };
    hydrate();
  }, []);

  const login = async (email: string, password: string) => {
    const formData = new URLSearchParams();
    formData.append('username', email);
    formData.append('password', password);
    const res = await api.post('/auth/token', formData);
    const token = res.data.access_token;
    localStorage.setItem('token', token);
    
    // Fetch user profile
    const userRes = await api.get('/auth/me');
    dispatch({ type: 'LOGIN_SUCCESS', payload: { user: userRes.data, token } });
  };

  const register = async (email: string, password: string, fullName: string) => {
    const res = await api.post('/auth/register', {
      email,
      password,
      full_name: fullName,
    });
    const token = res.data.access_token;
    localStorage.setItem('token', token);
    
    const userRes = await api.get('/auth/me');
    dispatch({ type: 'LOGIN_SUCCESS', payload: { user: userRes.data, token } });
  };

  const logout = () => {
    localStorage.removeItem('token');
    dispatch({ type: 'LOGOUT' });
  };

  return (
    <AuthContext.Provider value={{ ...state, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
