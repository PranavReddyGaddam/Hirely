import { useState, useRef, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import { User, LogOut, Settings } from 'lucide-react';

interface HeaderProps {
  variant?: 'dark' | 'light';
}

export default function Header({ variant = 'dark' }: HeaderProps) {
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [isProfileDropdownOpen, setIsProfileDropdownOpen] = useState(false);
  const navigate = useNavigate();
  const { logout, isAuthenticated, user } = useAuth();
  const dropdownRef = useRef<HTMLDivElement>(null);
  
  // Color classes based on variant
  const logoColor = variant === 'light' ? 'text-white' : 'text-slate-900';
  const linkColor = variant === 'light' ? 'text-white/90 hover:text-white' : 'text-slate-600 hover:text-slate-900';
  const mobileButtonColor = variant === 'light' ? 'text-white' : 'text-slate-900';

  const handleLogout = async () => {
    await logout();
    navigate('/');
    setIsMenuOpen(false);
    setIsProfileDropdownOpen(false);
  };

  const handleProfileClick = () => {
    navigate('/profile');
    setIsProfileDropdownOpen(false);
  };

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsProfileDropdownOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, []);

  return (
    <header className="absolute top-0 left-0 right-0 z-50">
      <nav className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between py-6">
          {/* Logo */}
          <div className="flex-shrink-0">
            <Link to="/" className={`text-2xl font-bold ${logoColor}`}>
              Hirely
            </Link>
          </div>

          {/* Desktop Navigation - Centered */}
          <div className="flex-grow flex justify-center">
            <div className="hidden md:flex items-center space-x-8">
              <Link to={isAuthenticated ? "/dashboard" : "/"} className={`${linkColor} transition-colors`}>
                {isAuthenticated ? 'Dashboard' : 'Home'}
              </Link>
              <Link to={isAuthenticated ? "/interview/setup" : "/login"} className={`${linkColor} transition-colors`}>
                {isAuthenticated ? 'New Interview' : 'Demo'}
              </Link>
              <Link to="/about" className={`${linkColor} transition-colors`}>
                How it works
              </Link>
            </div>
          </div>

          {/* Authentication Section - Far Right Corner */}
          <div className="flex-shrink-0 hidden md:flex items-center">
            {isAuthenticated ? (
              <div className="relative" ref={dropdownRef}>
                <button
                  onClick={() => setIsProfileDropdownOpen(!isProfileDropdownOpen)}
                  className="bg-slate-100 text-slate-700 hover:bg-slate-200 border-slate-300 p-2 rounded-lg border transition-colors"
                >
                  <User size={20} />
                </button>
                
                {/* Profile Dropdown */}
                {isProfileDropdownOpen && (
                  <div className="absolute right-0 mt-2 w-48 rounded-lg shadow-lg border bg-white border-slate-200">
                    <div className="py-1">
                      {/* User Info */}
                      <div className="px-4 py-2 border-b border-slate-200">
                        <p className="text-sm font-medium text-slate-900">
                          {user?.full_name || 'User'}
                        </p>
                      </div>
                      
                      {/* Dashboard Option */}
                      <button
                        onClick={() => {
                          navigate('/dashboard');
                          setIsProfileDropdownOpen(false);
                        }}
                        className="w-full text-left px-4 py-2 text-sm hover:bg-slate-50 flex items-center space-x-2 text-slate-700"
                      >
                        <User size={16} />
                        <span>Dashboard</span>
                      </button>
                      
                      {/* Profile Option */}
                      <button
                        onClick={handleProfileClick}
                        className="w-full text-left px-4 py-2 text-sm hover:bg-slate-50 flex items-center space-x-2 text-slate-700"
                      >
                        <Settings size={16} />
                        <span>Profile & Analytics</span>
                      </button>
                      
                      {/* Logout Option */}
                      <button
                        onClick={handleLogout}
                        className="w-full text-left px-4 py-2 text-sm hover:bg-slate-50 flex items-center space-x-2 text-slate-700"
                      >
                        <LogOut size={16} />
                        <span>Logout</span>
                      </button>
                    </div>
                  </div>
                )}
              </div>
            ) : (
              <Link 
                to="/signup" 
                className="bg-slate-100 text-slate-700 hover:bg-slate-200 border-slate-300 px-4 py-2 rounded-lg border transition-colors"
              >
                Sign Up
              </Link>
            )}
          </div>


          {/* Mobile menu button */}
          <button
            onClick={() => setIsMenuOpen(!isMenuOpen)}
            className={`md:hidden p-2 ${mobileButtonColor}`}
          >
            <svg
              className="w-6 h-6"
              fill="none"
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth="2"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              {isMenuOpen ? (
                <path d="M6 18L18 6M6 6l12 12" />
              ) : (
                <path d="M4 6h16M4 12h16M4 18h16" />
              )}
            </svg>
          </button>
        </div>

        {/* Mobile Navigation */}
        {isMenuOpen && (
          <div className="md:hidden py-4 space-y-4">
            <Link to={isAuthenticated ? "/dashboard" : "/"} className={`block ${linkColor}`} onClick={() => setIsMenuOpen(false)}>
              {isAuthenticated ? 'Dashboard' : 'Home'}
            </Link>
            <Link to={isAuthenticated ? "/interview/setup" : "/login"} className={`block ${linkColor}`} onClick={() => setIsMenuOpen(false)}>
              {isAuthenticated ? 'New Interview' : 'Demo'}
            </Link>
            <Link to="/about" className={`block ${linkColor}`} onClick={() => setIsMenuOpen(false)}>
              How it works
            </Link>
            
            {/* Mobile Authentication Section */}
            {isAuthenticated ? (
              <div className="pt-4 border-t border-slate-200 space-y-2">
                <button
                  onClick={handleProfileClick}
                  className="bg-slate-100 text-slate-700 hover:bg-slate-200 border-slate-300 px-4 py-2 rounded-lg border transition-colors text-sm font-medium w-full flex items-center justify-center space-x-2"
                >
                  <Settings size={16} />
                  <span>Profile & Analytics</span>
                </button>
                <button
                  onClick={handleLogout}
                  className="bg-slate-100 text-slate-700 hover:bg-slate-200 border-slate-300 px-4 py-2 rounded-lg border transition-colors text-sm font-medium w-full flex items-center justify-center space-x-2"
                >
                  <LogOut size={16} />
                  <span>Logout</span>
                </button>
              </div>
            ) : (
              <div className="pt-4 border-t border-slate-200">
                <Link 
                  to="/signup" 
                  className="bg-slate-100 text-slate-700 hover:bg-slate-200 border-slate-300 px-4 py-2 rounded-lg border transition-colors text-sm font-medium block text-center"
                  onClick={() => setIsMenuOpen(false)}
                >
                  Sign Up
                </Link>
              </div>
            )}
          </div>
        )}
      </nav>
    </header>
  );
}

