import React, { useState } from 'react';
import { Eye, EyeOff } from 'lucide-react';
import Header from '../components/Header';
import { useAuth } from '../hooks/useAuth';
import { useNavigate, Link } from 'react-router-dom';

export default function Signup() {
  const [formData, setFormData] = useState({
    full_name: '',
    email: '',
    password: '',
    confirmPassword: ''
  });
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirm, setShowConfirm] = useState(false);
  
  const { signup, error, clearError } = useAuth();
  const navigate = useNavigate();

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
    if (error) clearError();
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);

    if (formData.password !== formData.confirmPassword) {
      alert('Passwords do not match');
      setIsSubmitting(false);
      return;
    }
    if (formData.password.length < 6) {
      alert('Password must be at least 6 characters long');
      setIsSubmitting(false);
      return;
    }

    try {
      const success = await signup({
        email: formData.email,
        password: formData.password,
        full_name: formData.full_name
      });
      if (success) {
        navigate('/login'); // Redirect to login after successful signup
      }
    } catch (err) {
      console.error('Signup error:', err);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen">
      <div className="relative min-h-screen">
        <div
          className="absolute inset-0 z-0"
          style={{
            backgroundImage: "url(/mountains.png)",
            backgroundSize: "cover",
            backgroundPosition: "center",
            backgroundRepeat: "no-repeat",
          }}
        />

        <div
          className="absolute inset-0 z-0"
          style={{
            background:
              "linear-gradient(to bottom, rgba(255,255,255,0) 0%, rgba(255,255,255,0) 60%, rgba(255,255,255,0.8) 85%, rgba(255,255,255,1) 100%)",
          }}
        />

        <Header />

        <div className="relative z-10 flex items-center justify-center min-h-screen pt-24 pb-8">
          <div className="w-full max-w-md px-4">
            <div className="bg-white/10 backdrop-blur-md rounded-3xl p-8 shadow-lg" style={{ boxShadow: '0 10px 25px rgba(228, 242, 35, 0.2)' }}>
              <div className="text-center mb-8">
                <h1 className="text-3xl font-bold text-black mb-2">Create Account</h1>
                <p className="text-black/80">Sign up to get started</p>
              </div>

              {error && (
                <div className="mb-4 p-3 bg-red-100 border border-red-400 text-red-700 rounded-lg">
                  {error}
                </div>
              )}

              <form onSubmit={handleSubmit} className="space-y-6">
                <div>
                  <label htmlFor="full_name" className="block text-sm font-semibold text-black mb-2">
                    Full Name
                  </label>
                  <input
                    id="full_name"
                    name="full_name"
                    type="text"
                    required
                    className="w-full px-4 py-3 bg-white/20 backdrop-blur-sm rounded-xl text-black placeholder-black/60 focus:outline-none transition-all duration-300"
                    placeholder="Enter your full name"
                    onFocus={(e) => {
                      e.currentTarget.style.borderColor = '#e4f223';
                      e.currentTarget.style.boxShadow = '0 0 0 2px rgba(228, 242, 35, 0.2)';
                    }}
                    onBlur={(e) => {
                      e.currentTarget.style.borderColor = 'transparent';
                      e.currentTarget.style.boxShadow = 'none';
                    }}
                    value={formData.full_name}
                    onChange={handleChange}
                  />
                </div>

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
                    placeholder="Enter your email"
                    onFocus={(e) => {
                      e.currentTarget.style.borderColor = '#e4f223';
                      e.currentTarget.style.boxShadow = '0 0 0 2px rgba(228, 242, 35, 0.2)';
                    }}
                    onBlur={(e) => {
                      e.currentTarget.style.borderColor = 'transparent';
                      e.currentTarget.style.boxShadow = 'none';
                    }}
                  />
                </div>

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
                      placeholder="Enter your password"
                      onFocus={(e) => {
                        e.currentTarget.style.borderColor = '#e4f223';
                        e.currentTarget.style.boxShadow = '0 0 0 2px rgba(228, 242, 35, 0.2)';
                      }}
                      onBlur={(e) => {
                        e.currentTarget.style.borderColor = 'transparent';
                        e.currentTarget.style.boxShadow = 'none';
                      }}
                    />
                    <button
                      type="button"
                      aria-label={showPassword ? 'Hide password' : 'Show password'}
                      onClick={() => setShowPassword(!showPassword)}
                      className="absolute inset-y-0 right-3 flex items-center text-black/70 hover:text-black"
                    >
                      {showPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                    </button>
                  </div>
                </div>

                <div>
                  <label htmlFor="confirmPassword" className="block text-sm font-semibold text-black mb-2">
                    Confirm Password
                  </label>
                  <div className="relative">
                    <input
                      type={showConfirm ? 'text' : 'password'}
                      id="confirmPassword"
                      name="confirmPassword"
                      value={formData.confirmPassword}
                      onChange={handleChange}
                      required
                      className="w-full pr-12 px-4 py-3 bg-white/20 backdrop-blur-sm rounded-xl text-black placeholder-black/60 focus:outline-none transition-all duration-300"
                      placeholder="Confirm your password"
                      onFocus={(e) => {
                        e.currentTarget.style.borderColor = '#e4f223';
                        e.currentTarget.style.boxShadow = '0 0 0 2px rgba(228, 242, 35, 0.2)';
                      }}
                      onBlur={(e) => {
                        e.currentTarget.style.borderColor = 'transparent';
                        e.currentTarget.style.boxShadow = 'none';
                      }}
                    />
                    <button
                      type="button"
                      aria-label={showConfirm ? 'Hide password' : 'Show password'}
                      onClick={() => setShowConfirm(!showConfirm)}
                      className="absolute inset-y-0 right-3 flex items-center text-black/70 hover:text-black"
                    >
                      {showConfirm ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                    </button>
                  </div>
                </div>

                <button
                  type="submit"
                  disabled={isSubmitting}
                  className="w-full text-black font-bold py-3 px-4 rounded-xl transition-all duration-300 hover:scale-105 focus:outline-none disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100"
                  style={{ backgroundColor: '#e4f223' }}
                  onMouseEnter={(e) => !e.currentTarget.disabled && (e.currentTarget.style.backgroundColor = '#d4e213')}
                  onMouseLeave={(e) => !e.currentTarget.disabled && (e.currentTarget.style.backgroundColor = '#e4f223')}
                >
                  {isSubmitting ? 'Creating account...' : 'Create Account'}
                </button>

                <div className="text-center">
                  <p className="text-black/80">
                    Already have an account?{' '}
                    <Link 
                      to="/login" 
                      className="font-semibold transition-colors duration-300"
                      style={{ color: '#1f2937' }}
                      onMouseEnter={(e) => e.currentTarget.style.color = '#e4f223'}
                      onMouseLeave={(e) => e.currentTarget.style.color = '#1f2937'}
                    >
                      Sign in here
                    </Link>
                  </p>
                </div>
              </form>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
