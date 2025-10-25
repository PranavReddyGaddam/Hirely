import { useState, useEffect } from 'react';

interface User {
  id: string;
  email: string;
  full_name: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

interface LoginCredentials {
  email: string;
  password: string;
}

interface SignupData {
  email: string;
  password: string;
  full_name: string;
}

interface AuthResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
}

const API_BASE_URL = 'http://localhost:8000/api/v1';

export function useAuth() {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [backendStatus, setBackendStatus] = useState<'connected' | 'disconnected' | 'checking'>('checking');

  useEffect(() => {
    checkAuthStatus();
    const cleanupHealthMonitoring = startBackendHealthMonitoring();
    
    // Listen for storage changes (e.g., when user logs out in another tab)
    const handleStorageChange = (e: StorageEvent) => {
      if (e.key === 'hirely_token' && e.newValue === null) {
        console.log('Token removed from another tab, logging out');
        setUser(null);
      }
    };
    
    window.addEventListener('storage', handleStorageChange);
    
    return () => {
      window.removeEventListener('storage', handleStorageChange);
      cleanupHealthMonitoring();
    };
  }, []);

  const checkBackendHealth = async (): Promise<boolean> => {
    try {
      const response = await fetch('http://localhost:8000/health', {
        method: 'GET',
        signal: AbortSignal.timeout(5000) // 5 second timeout
      });
      
      if (response.ok) {
        const data = await response.json();
        if (data.status === 'healthy') {
          setBackendStatus('connected');
          return true;
        }
      }
      setBackendStatus('disconnected');
      return false;
    } catch (err) {
      console.log('Backend health check failed:', err);
      setBackendStatus('disconnected');
      return false;
    }
  };

  const startBackendHealthMonitoring = () => {
    // Check backend health every 10 seconds
    const healthCheckInterval = setInterval(async () => {
      const isHealthy = await checkBackendHealth();
      
      if (!isHealthy && user) {
        console.log('Backend disconnected, logging out user automatically');
        // Clear user session
        setUser(null);
        localStorage.removeItem('hirely_token');
        // Trigger a custom event for notification
        window.dispatchEvent(new CustomEvent('backend-restart', {
          detail: {
            message: 'Backend server has been restarted. You have been logged out for security.',
            type: 'warning'
          }
        }));
      }
    }, 10000); // Check every 10 seconds

    // Cleanup interval on component unmount
    return () => clearInterval(healthCheckInterval);
  };

  const checkAuthStatus = async () => {
    const token = localStorage.getItem('hirely_token');
    if (!token) {
      setIsLoading(false);
      setUser(null);
      return;
    }

    try {
      const response = await fetch(`${API_BASE_URL}/users/me`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        const userData = await response.json();
        setUser(userData);
        console.log('User session restored:', userData.email);
      } else {
        // Token is invalid, remove it
        console.log('Token invalid, clearing session');
        localStorage.removeItem('hirely_token');
        setUser(null);
      }
    } catch (err) {
      console.error('Auth check failed:', err);
      localStorage.removeItem('hirely_token');
      setUser(null);
    } finally {
      setIsLoading(false);
    }
  };

  const login = async (credentials: LoginCredentials): Promise<boolean> => {
    setError(null);
    setIsLoading(true);

    try {
      const response = await fetch(`${API_BASE_URL}/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          email: credentials.email,
          password: credentials.password,
        }),
      });

      if (response.ok) {
        const authData: AuthResponse = await response.json();
        localStorage.setItem('hirely_token', authData.access_token);
        
        // Fetch user profile
        const userResponse = await fetch(`${API_BASE_URL}/users/me`, {
          headers: {
            'Authorization': `Bearer ${authData.access_token}`,
            'Content-Type': 'application/json',
          },
        });

        if (userResponse.ok) {
          const userData = await userResponse.json();
          setUser(userData);
          console.log('User logged in successfully:', userData.email);
          return true;
        }
      } else {
        const errorData = await response.json();
        setError(errorData.detail || 'Login failed');
      }
    } catch (err) {
      setError('Network error during login');
      console.error('Login error:', err);
    } finally {
      setIsLoading(false);
    }

    return false;
  };

  const signup = async (signupData: SignupData): Promise<boolean> => {
    setError(null);
    setIsLoading(true);

    try {
      const response = await fetch(`${API_BASE_URL}/auth/register`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(signupData),
      });

      if (response.ok) {
        // Do not auto-login; redirect to login screen
        return true;
      } else {
        const errorData = await response.json();
        setError(errorData.detail || 'Signup failed');
      }
    } catch (err) {
      setError('Network error during signup');
      console.error('Signup error:', err);
    } finally {
      setIsLoading(false);
    }

    return false;
  };

  const logout = async () => {
    setError(null);
    console.log('Logging out user...');
    
    try {
      const token = localStorage.getItem('hirely_token');
      if (token) {
        await fetch(`${API_BASE_URL}/auth/logout`, {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
          },
        });
      }
    } catch (err) {
      console.error('Logout error:', err);
    } finally {
      setUser(null);
      localStorage.removeItem('hirely_token');
      console.log('User logged out successfully');
    }
  };

  const clearError = () => {
    setError(null);
  };

  const refreshUserSession = async () => {
    const token = localStorage.getItem('hirely_token');
    if (!token) {
      setUser(null);
      return false;
    }

    try {
      const response = await fetch(`${API_BASE_URL}/users/me`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        const userData = await response.json();
        setUser(userData);
        return true;
      } else {
        // Token is invalid
        localStorage.removeItem('hirely_token');
        setUser(null);
        return false;
      }
    } catch (err) {
      console.error('Session refresh failed:', err);
      localStorage.removeItem('hirely_token');
      setUser(null);
      return false;
    }
  };

  const requestPasswordReset = async (email: string): Promise<boolean> => {
    setError(null);
    try {
      const response = await fetch(`${API_BASE_URL}/auth/forgot-password`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email })
      });
      if (response.ok) return true;
      const err = await response.json();
      setError(err.detail || 'Failed to send reset email');
      return false;
    } catch (e) {
      setError('Network error while sending reset email');
      return false;
    }
  };

  return {
    user,
    isLoading,
    error,
    backendStatus,
    login,
    signup,
    logout,
    clearError,
    requestPasswordReset,
    refreshUserSession,
    isAuthenticated: !!user
  };
}
