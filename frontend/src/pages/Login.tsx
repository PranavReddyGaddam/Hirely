import { useState } from 'react';
import { Eye, EyeOff } from 'lucide-react';
import { Link, useNavigate } from 'react-router-dom';
import Header from '../components/Header';
import { useAuth } from '../hooks/useAuth';

export default function Login() {
  const [formData, setFormData] = useState({
    email: '',
    password: ''
  });
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  
  const { login, error, clearError } = useAuth();
  const navigate = useNavigate();

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
    // Clear error when user starts typing
    if (error) clearError();
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);

    try {
      const success = await login({
        email: formData.email,
        password: formData.password
      });

      if (success) {
        navigate('/interview/setup'); // Redirect to interview setup after successful login
      }
    } catch (err) {
      console.error('Login error:', err);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen">
      {/* Hero Section with Mountains Background */}
      <div className="relative min-h-screen">
        {/* Background Image */}
        <div
          className="absolute inset-0 z-0"
          style={{
            backgroundImage: "url(/mountains.png)",
            backgroundSize: "cover",
            backgroundPosition: "center",
            backgroundRepeat: "no-repeat",
          }}
        />

        {/* Gradient Overlay - transitions to white at bottom */}
        <div
          className="absolute inset-0 z-0"
          style={{
            background:
              "linear-gradient(to bottom, rgba(255,255,255,0) 0%, rgba(255,255,255,0) 60%, rgba(255,255,255,0.8) 85%, rgba(255,255,255,1) 100%)",
          }}
        />

        <Header />
        
        {/* Login Form */}
        <div className="relative z-10 flex items-center justify-center min-h-screen pt-24 pb-8">
          <div className="w-full max-w-md px-4">
            {/* Glassmorphic Login Card */}
            <div className="bg-white/10 backdrop-blur-md rounded-3xl p-8 shadow-lg" style={{ boxShadow: '0 10px 25px rgba(228, 242, 35, 0.2)' }}>
              {/* Header */}
              <div className="text-center mb-8">
                <h1 className="text-3xl font-bold text-black mb-2">Welcome Back</h1>
                <p className="text-black/80">Sign in to your account</p>
              </div>

              {/* Error Message */}
              {error && (
                <div className="mb-4 p-3 bg-red-100 border border-red-400 text-red-700 rounded-lg">
                  {error}
                </div>
              )}

              {/* Login Form */}
              <form onSubmit={handleSubmit} className="space-y-6">
                {/* Email Field */}
                <div>
                  <label htmlFor="email" className="block text-sm font-semibold text-black mb-2">
                    Email Address
                  </label>
                  <input
                    type="email"
                    id="email"
                    name="email"
                    value={formData.email}
                    onChange={handleChange}
                    required
                    className="w-full px-4 py-3 bg-white/20 backdrop-blur-sm rounded-xl text-black placeholder-black/60 focus:outline-none transition-all duration-300"
                    onFocus={(e) => {
                      e.currentTarget.style.borderColor = '#e4f223';
                      e.currentTarget.style.boxShadow = '0 0 0 2px rgba(228, 242, 35, 0.2)';
                    }}
                    onBlur={(e) => {
                      e.currentTarget.style.borderColor = 'transparent';
                      e.currentTarget.style.boxShadow = 'none';
                    }}
                    placeholder="Enter your email"
                  />
                </div>

                {/* Password Field */}
                <div>
                  <label htmlFor="password" className="block text-sm font-semibold text-black mb-2">
                    Password
                  </label>
                  <div className="relative">
                    <input
                      type={showPassword ? 'text' : 'password'}
                      id="password"
                      name="password"
                      value={formData.password}
                      onChange={handleChange}
                      required
                      className="w-full pr-12 px-4 py-3 bg-white/20 backdrop-blur-sm rounded-xl text-black placeholder-black/60 focus:outline-none transition-all duration-300"
                      onFocus={(e) => {
                        e.currentTarget.style.borderColor = '#e4f223';
                        e.currentTarget.style.boxShadow = '0 0 0 2px rgba(228, 242, 35, 0.2)';
                      }}
                      onBlur={(e) => {
                        e.currentTarget.style.borderColor = 'transparent';
                        e.currentTarget.style.boxShadow = 'none';
                      }}
                      placeholder="Enter your password"
                    />
                    <button
                      type="button"
                      aria-label={showPassword ? 'Hide password' : 'Show password'}
                      onClick={() => setShowPassword(!showPassword)}
                      className="absolute inset-y-0 right-3 flex items-center text-black/70 hover:text-black"
                    >
                      {showPassword ? (
                        <EyeOff className="w-5 h-5" />
                      ) : (
                        <Eye className="w-5 h-5" />
                      )}
                    </button>
                  </div>
                </div>

                {/* Remember Me & Forgot Password */}
                <div className="flex items-center justify-between">
                  <label className="flex items-center">
                    <input
                      type="checkbox"
                      className="w-4 h-4 bg-white/20 rounded focus:ring-2"
                      style={{ accentColor: '#e4f223' }}
                    />
                    <span className="ml-2 text-sm text-black">Remember me</span>
                  </label>
                  <Link
                    to="/forgot-password"
                    className="text-sm font-medium transition-colors duration-300"
                    style={{ color: '#1f2937' }}
                    onMouseEnter={(e) => e.currentTarget.style.color = '#e4f223'}
                    onMouseLeave={(e) => e.currentTarget.style.color = '#1f2937'}
                  >
                    Forgot password?
                  </Link>
                </div>

                {/* Login Button */}
                <button
                  type="submit"
                  disabled={isSubmitting}
                  className="w-full text-black font-bold py-3 px-4 rounded-xl transition-all duration-300 hover:scale-105 focus:outline-none disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100"
                  style={{ backgroundColor: '#e4f223' }}
                  onMouseEnter={(e) => !e.currentTarget.disabled && (e.currentTarget.style.backgroundColor = '#d4e213')}
                  onMouseLeave={(e) => !e.currentTarget.disabled && (e.currentTarget.style.backgroundColor = '#e4f223')}
                >
                  {isSubmitting ? (
                    <div className="flex items-center justify-center">
                      <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-black" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                      </svg>
                      Signing in...
                    </div>
                  ) : (
                    'Sign In'
                  )}
                </button>

              {/* Social logins removed as requested */}
              </form>

              {/* Sign Up Link */}
              <div className="mt-8 text-center">
                <p className="text-black/80">
                  Don't have an account?{' '}
                  <Link
                    to="/signup"
                    className="font-semibold transition-colors duration-300"
                    style={{ color: '#1f2937' }}
                    onMouseEnter={(e) => e.currentTarget.style.color = '#e4f223'}
                    onMouseLeave={(e) => e.currentTarget.style.color = '#1f2937'}
                  >
                    Sign up here
                  </Link>
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
