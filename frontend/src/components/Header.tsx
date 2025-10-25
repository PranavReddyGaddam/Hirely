import { useState, useRef, useEffect } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import { User, LogOut, Settings } from 'lucide-react';

export default function Header() {
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [isProfileDropdownOpen, setIsProfileDropdownOpen] = useState(false);
  const location = useLocation();
  const navigate = useNavigate();
  const { logout, isAuthenticated, user } = useAuth();
  const isHomePage = location.pathname === '/';
  const dropdownRef = useRef<HTMLDivElement>(null);

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
            <Link to="/" className={`text-2xl font-bold ${isHomePage ? 'text-white' : 'text-slate-900'}`}>
              Hirely
            </Link>
          </div>

          {/* Desktop Navigation - Centered */}
          <div className="flex-grow flex justify-center">
            <div className="hidden md:flex items-center space-x-8">
              <Link to="/" className={`${isHomePage ? 'text-white/90 hover:text-white' : 'text-slate-600 hover:text-slate-900'} transition-colors`}>
                Home
              </Link>
              <Link to={isAuthenticated ? "/interview/setup" : "/login"} className={`${isHomePage ? 'text-white/90 hover:text-white' : 'text-slate-600 hover:text-slate-900'} transition-colors`}>
                Demo
              </Link>
              <Link to="/about" className={`${isHomePage ? 'text-white/90 hover:text-white' : 'text-slate-600 hover:text-slate-900'} transition-colors`}>
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
                  className={`${isHomePage 
                    ? 'bg-white/20 text-white hover:bg-white/30 border-white/30' 
                    : 'bg-slate-100 text-slate-700 hover:bg-slate-200 border-slate-300'
                  } p-2 rounded-lg border transition-colors`}
                >
                  <User size={20} />
                </button>
                
                {/* Profile Dropdown */}
                {isProfileDropdownOpen && (
                  <div className={`absolute right-0 mt-2 w-48 rounded-lg shadow-lg border ${
                    isHomePage 
                      ? 'bg-white/95 backdrop-blur-sm border-white/30' 
                      : 'bg-white border-slate-200'
                  }`}>
                    <div className="py-1">
                      {/* User Info */}
                      <div className={`px-4 py-2 border-b ${
                        isHomePage ? 'border-white/20' : 'border-slate-200'
                      }`}>
                        <p className={`text-sm font-medium ${
                          isHomePage ? 'text-slate-900' : 'text-slate-900'
                        }`}>
                          {user?.full_name || 'User'}
                        </p>
                      </div>
                      
                      {/* Profile Option */}
                      <button
                        onClick={handleProfileClick}
                        className={`w-full text-left px-4 py-2 text-sm hover:bg-slate-50 flex items-center space-x-2 ${
                          isHomePage ? 'text-slate-900 hover:bg-white/50' : 'text-slate-700'
                        }`}
                      >
                        <Settings size={16} />
                        <span>Profile & Analytics</span>
                      </button>
                      
                      {/* Logout Option */}
                      <button
                        onClick={handleLogout}
                        className={`w-full text-left px-4 py-2 text-sm hover:bg-slate-50 flex items-center space-x-2 ${
                          isHomePage ? 'text-slate-900 hover:bg-white/50' : 'text-slate-700'
                        }`}
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
                className={`${isHomePage 
                  ? 'bg-white/20 text-white hover:bg-white/30 border-white/30' 
                  : 'bg-slate-100 text-slate-700 hover:bg-slate-200 border-slate-300'
                } px-4 py-2 rounded-lg border transition-colors`}
              >
                Sign Up
              </Link>
            )}
          </div>


          {/* Mobile menu button */}
          <button
            onClick={() => setIsMenuOpen(!isMenuOpen)}
            className={`md:hidden p-2 ${isHomePage ? 'text-white' : 'text-slate-900'}`}
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
            <Link to="/" className={`block ${isHomePage ? 'text-white/90 hover:text-white' : 'text-slate-600 hover:text-slate-900'}`} onClick={() => setIsMenuOpen(false)}>
              Home
            </Link>
            <Link to={isAuthenticated ? "/interview/setup" : "/login"} className={`block ${isHomePage ? 'text-white/90 hover:text-white' : 'text-slate-600 hover:text-slate-900'}`} onClick={() => setIsMenuOpen(false)}>
              Demo
            </Link>
            <Link to="/about" className={`block ${isHomePage ? 'text-white/90 hover:text-white' : 'text-slate-600 hover:text-slate-900'}`} onClick={() => setIsMenuOpen(false)}>
              How it works
            </Link>
            
            {/* Mobile Authentication Section */}
            {isAuthenticated ? (
              <div className="pt-4 border-t border-white/20 space-y-2">
                <button
                  onClick={handleProfileClick}
                  className={`${isHomePage 
                    ? 'bg-white/20 text-white hover:bg-white/30 border-white/30' 
                    : 'bg-slate-100 text-slate-700 hover:bg-slate-200 border-slate-300'
                  } px-4 py-2 rounded-lg border transition-colors text-sm font-medium w-full flex items-center justify-center space-x-2`}
                >
                  <Settings size={16} />
                  <span>Profile & Analytics</span>
                </button>
                <button
                  onClick={handleLogout}
                  className={`${isHomePage 
                    ? 'bg-white/20 text-white hover:bg-white/30 border-white/30' 
                    : 'bg-slate-100 text-slate-700 hover:bg-slate-200 border-slate-300'
                  } px-4 py-2 rounded-lg border transition-colors text-sm font-medium w-full flex items-center justify-center space-x-2`}
                >
                  <LogOut size={16} />
                  <span>Logout</span>
                </button>
              </div>
            ) : (
              <div className="pt-4 border-t border-white/20">
                <Link 
                  to="/signup" 
                  className={`${isHomePage 
                    ? 'bg-white/20 text-white hover:bg-white/30 border-white/30' 
                    : 'bg-slate-100 text-slate-700 hover:bg-slate-200 border-slate-300'
                  } px-4 py-2 rounded-lg border transition-colors text-sm font-medium block text-center`}
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

