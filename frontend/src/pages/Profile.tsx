import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import Header from '../components/Header';
import { SmoothPageTransition } from '../components/SkeletonLoader';
import { 
  User, 
  Mail, 
  Calendar, 
  BarChart3, 
  TrendingUp, 
  Clock, 
  Target, 
  Award,
  Settings,
  Eye,
  EyeOff
} from 'lucide-react';

export default function Profile() {
  const { user, isAuthenticated, isLoading } = useAuth();
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState<'profile' | 'analytics' | 'settings'>('profile');
  const [showPasswordForm, setShowPasswordForm] = useState(false);
  const [passwordData, setPasswordData] = useState({
    currentPassword: '',
    newPassword: '',
    confirmPassword: ''
  });
  const [showPasswords, setShowPasswords] = useState({
    current: false,
    new: false,
    confirm: false
  });

  // Mock analytics data for hackathon demo
  const analyticsData = {
    totalInterviews: 12,
    averageScore: 87,
    improvementRate: 15,
    totalTimeSpent: 180, // minutes
    strengths: ['Communication', 'Problem Solving', 'Technical Knowledge'],
    areasForImprovement: ['Time Management', 'Confidence', 'Specific Examples'],
    recentInterviews: [
      { id: 1, date: '2025-10-22', score: 92, type: 'Behavioral', company: 'Tech Corp' },
      { id: 2, date: '2025-10-21', score: 85, type: 'Technical', company: 'StartupXYZ' },
      { id: 3, date: '2025-10-20', score: 88, type: 'Mixed', company: 'BigTech Inc' },
    ]
  };

  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      navigate('/login');
    }
  }, [isAuthenticated, isLoading, navigate]);

  const handlePasswordChange = async (e: React.FormEvent) => {
    e.preventDefault();
    
    // Validate passwords match
    if (passwordData.newPassword !== passwordData.confirmPassword) {
      alert('New passwords do not match!');
      return;
    }
    
    // Validate password length
    if (passwordData.newPassword.length < 6) {
      alert('New password must be at least 6 characters long!');
      return;
    }
    
    try {
      const token = localStorage.getItem('access_token');
      if (!token) {
        alert('Please log in again');
        navigate('/login');
        return;
      }
      
      const response = await fetch('/api/v1/auth/change-password', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          current_password: passwordData.currentPassword,
          new_password: passwordData.newPassword
        })
      });
      
      if (response.ok) {
        alert('Password changed successfully!');
        setShowPasswordForm(false);
        setPasswordData({ currentPassword: '', newPassword: '', confirmPassword: '' });
      } else {
        const errorData = await response.json();
        alert(`Failed to change password: ${errorData.detail || 'Unknown error'}`);
      }
    } catch (error) {
      console.error('Password change error:', error);
      alert('Failed to change password. Please try again.');
    }
  };

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-lg font-semibold">Loading...</div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return null;
  }

  return (
    <SmoothPageTransition>
      <div className="min-h-screen relative overflow-hidden">
      {/* Mountains Background */}
      <div className="absolute inset-0">
        <div 
          className="absolute inset-0 bg-cover bg-center bg-no-repeat"
          style={{
            backgroundImage: `url('/mountains.png')`
          }}
        ></div>
        <div className="absolute inset-0 bg-black/20"></div>
      </div>
      
      <Header />
      
      <div className="relative z-10 pt-20 pb-8">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          {/* Header */}
          <div className="bg-white/30 backdrop-blur-lg border border-white/40 rounded-2xl shadow-2xl p-6 mb-8">
            <div className="flex items-center space-x-4">
              <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center">
                <User size={32} className="text-blue-600" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-gray-900">
                  {user?.full_name || 'User Profile'}
                </h1>
                <p className="text-gray-600">{user?.email}</p>
                <p className="text-sm text-gray-500">Member since October 2025</p>
              </div>
            </div>
          </div>

          {/* Navigation Tabs */}
          <div className="bg-white/30 backdrop-blur-lg border border-white/40 rounded-2xl shadow-2xl mb-8">
            <div className="border-b border-gray-200">
              <nav className="flex space-x-8 px-6">
                <button
                  onClick={() => setActiveTab('profile')}
                  className={`py-4 px-1 border-b-2 font-medium text-sm ${
                    activeTab === 'profile'
                      ? 'border-blue-500 text-blue-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }`}
                >
                  <User size={20} className="inline mr-2" />
                  Profile
                </button>
                <button
                  onClick={() => setActiveTab('analytics')}
                  className={`py-4 px-1 border-b-2 font-medium text-sm ${
                    activeTab === 'analytics'
                      ? 'border-blue-500 text-blue-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }`}
                >
                  <BarChart3 size={20} className="inline mr-2" />
                  Analytics
                </button>
                <button
                  onClick={() => setActiveTab('settings')}
                  className={`py-4 px-1 border-b-2 font-medium text-sm ${
                    activeTab === 'settings'
                      ? 'border-blue-500 text-blue-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }`}
                >
                  <Settings size={20} className="inline mr-2" />
                  Settings
                </button>
              </nav>
            </div>
          </div>

          {/* Tab Content */}
          <div className="bg-white/30 backdrop-blur-lg border border-white/40 rounded-2xl shadow-2xl p-6">
            {activeTab === 'profile' && (
              <div className="space-y-6">
                <h2 className="text-xl font-semibold text-gray-900">Profile Information</h2>
                
                <div className="grid md:grid-cols-2 gap-6">
                  <div className="space-y-4">
                    <div className="flex items-center space-x-3">
                      <Mail size={20} className="text-gray-400" />
                      <div>
                        <p className="text-sm font-medium text-gray-900">Email</p>
                        <p className="text-sm text-gray-600">{user?.email}</p>
                      </div>
                    </div>
                    
                    <div className="flex items-center space-x-3">
                      <User size={20} className="text-gray-400" />
                      <div>
                        <p className="text-sm font-medium text-gray-900">Full Name</p>
                        <p className="text-sm text-gray-600">{user?.full_name || 'Not provided'}</p>
                      </div>
                    </div>
                    
                    <div className="flex items-center space-x-3">
                      <Calendar size={20} className="text-gray-400" />
                      <div>
                        <p className="text-sm font-medium text-gray-900">Member Since</p>
                        <p className="text-sm text-gray-600">October 2025</p>
                      </div>
                    </div>
                  </div>
                  
                  <div className="space-y-4">
                    <div className="flex items-center space-x-3">
                      <Target size={20} className="text-gray-400" />
                      <div>
                        <p className="text-sm font-medium text-gray-900">Interviews Completed</p>
                        <p className="text-sm text-gray-600">{analyticsData.totalInterviews}</p>
                      </div>
                    </div>
                    
                    <div className="flex items-center space-x-3">
                      <Award size={20} className="text-gray-400" />
                      <div>
                        <p className="text-sm font-medium text-gray-900">Average Score</p>
                        <p className="text-sm text-gray-600">{analyticsData.averageScore}%</p>
                      </div>
                    </div>
                    
                    <div className="flex items-center space-x-3">
                      <Clock size={20} className="text-gray-400" />
                      <div>
                        <p className="text-sm font-medium text-gray-900">Total Time Spent</p>
                        <p className="text-sm text-gray-600">{analyticsData.totalTimeSpent} minutes</p>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {activeTab === 'analytics' && (
              <div className="space-y-6">
                <h2 className="text-xl font-semibold text-gray-900">Interview Analytics</h2>
                
                {/* Key Metrics */}
                <div className="grid md:grid-cols-4 gap-6">
                  <div className="backdrop-blur-md p-4 rounded-2xl shadow-xl" style={{ backgroundColor: 'rgba(228, 242, 35, 0.3)', border: '1px solid rgba(228, 242, 35, 0.5)' }}>
                    <div className="flex items-center">
                      <BarChart3 size={24} style={{ color: '#e4f223' }} />
                      <div className="ml-3">
                        <p className="text-sm font-medium" style={{ color: '#e4f223' }}>Total Interviews</p>
                        <p className="text-2xl font-bold" style={{ color: '#e4f223' }}>{analyticsData.totalInterviews}</p>
                      </div>
                    </div>
                  </div>
                  
                  <div className="backdrop-blur-md p-4 rounded-2xl shadow-xl" style={{ backgroundColor: 'rgba(228, 242, 35, 0.3)', border: '1px solid rgba(228, 242, 35, 0.5)' }}>
                    <div className="flex items-center">
                      <Award size={24} style={{ color: '#e4f223' }} />
                      <div className="ml-3">
                        <p className="text-sm font-medium" style={{ color: '#e4f223' }}>Average Score</p>
                        <p className="text-2xl font-bold" style={{ color: '#e4f223' }}>{analyticsData.averageScore}%</p>
                      </div>
                    </div>
                  </div>
                  
                  <div className="backdrop-blur-md p-4 rounded-2xl shadow-xl" style={{ backgroundColor: 'rgba(228, 242, 35, 0.3)', border: '1px solid rgba(228, 242, 35, 0.5)' }}>
                    <div className="flex items-center">
                      <TrendingUp size={24} style={{ color: '#e4f223' }} />
                      <div className="ml-3">
                        <p className="text-sm font-medium" style={{ color: '#e4f223' }}>Improvement</p>
                        <p className="text-2xl font-bold" style={{ color: '#e4f223' }}>+{analyticsData.improvementRate}%</p>
                      </div>
                    </div>
                  </div>
                  
                  <div className="backdrop-blur-md p-4 rounded-2xl shadow-xl" style={{ backgroundColor: 'rgba(228, 242, 35, 0.3)', border: '1px solid rgba(228, 242, 35, 0.5)' }}>
                    <div className="flex items-center">
                      <Clock size={24} style={{ color: '#e4f223' }} />
                      <div className="ml-3">
                        <p className="text-sm font-medium" style={{ color: '#e4f223' }}>Time Spent</p>
                        <p className="text-2xl font-bold" style={{ color: '#e4f223' }}>{analyticsData.totalTimeSpent}m</p>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Strengths and Improvements */}
                <div className="grid md:grid-cols-2 gap-6">
                  <div className="bg-lime-500/30 backdrop-blur-md border border-lime-400/50 p-6 rounded-2xl shadow-xl">
                    <h3 className="text-lg font-semibold text-lime-900 mb-4">Strengths</h3>
                    <ul className="space-y-2">
                      {analyticsData.strengths.map((strength, index) => (
                        <li key={index} className="flex items-center text-lime-800">
                          <div className="w-2 h-2 bg-lime-500 rounded-full mr-3"></div>
                          {strength}
                        </li>
                      ))}
                    </ul>
                  </div>
                  
                  <div className="bg-lime-500/30 backdrop-blur-md border border-lime-400/50 p-6 rounded-2xl shadow-xl">
                    <h3 className="text-lg font-semibold text-lime-900 mb-4">Areas for Improvement</h3>
                    <ul className="space-y-2">
                      {analyticsData.areasForImprovement.map((area, index) => (
                        <li key={index} className="flex items-center text-lime-800">
                          <div className="w-2 h-2 bg-lime-500 rounded-full mr-3"></div>
                          {area}
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>

                {/* Recent Interviews */}
                <div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">Recent Interviews</h3>
                  <div className="overflow-x-auto">
                    <div className="bg-white/30 backdrop-blur-md border border-white/40 rounded-2xl shadow-xl overflow-hidden">
                      <table className="min-w-full divide-y divide-white/20">
                        <thead className="bg-white/30">
                          <tr>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">Date</th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">Type</th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">Company</th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">Score</th>
                          </tr>
                        </thead>
                        <tbody className="bg-white/10 divide-y divide-white/20">
                        {analyticsData.recentInterviews.map((interview) => (
                          <tr key={interview.id}>
                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{interview.date}</td>
                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{interview.type}</td>
                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{interview.company}</td>
                            <td className="px-6 py-4 whitespace-nowrap">
                              <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                                interview.score >= 90 ? 'bg-lime-100 text-lime-800' :
                                interview.score >= 80 ? 'bg-lime-100 text-lime-800' :
                                'bg-gray-100 text-gray-800'
                              }`}>
                                {interview.score}%
                              </span>
                            </td>
                          </tr>
                        ))}
                        </tbody>
                      </table>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {activeTab === 'settings' && (
              <div className="space-y-6">
                <h2 className="text-xl font-semibold text-gray-900">Account Settings</h2>
                
                <div className="space-y-6">
                  <div className="bg-white/30 backdrop-blur-md border border-white/40 rounded-2xl shadow-xl p-6">
                    <div className="flex items-center justify-between">
                      <div>
                        <h3 className="text-lg font-medium text-gray-900">Change Password</h3>
                        <p className="text-sm text-gray-600">Update your account password</p>
                      </div>
                      <button
                        onClick={() => setShowPasswordForm(!showPasswordForm)}
                        className="backdrop-blur-sm text-white px-4 py-2 rounded-xl transition-colors shadow-lg"
                        style={{ backgroundColor: 'rgba(228, 242, 35, 0.8)' }}
                        onMouseEnter={(e) => e.currentTarget.style.backgroundColor = 'rgba(212, 226, 19, 0.8)'}
                        onMouseLeave={(e) => e.currentTarget.style.backgroundColor = 'rgba(228, 242, 35, 0.8)'}
                      >
                        {showPasswordForm ? 'Cancel' : 'Change Password'}
                      </button>
                    </div>
                    
                    {showPasswordForm && (
                      <form onSubmit={handlePasswordChange} className="mt-6 space-y-4">
                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-2">
                            Current Password
                          </label>
                          <div className="relative">
                            <input
                              type={showPasswords.current ? 'text' : 'password'}
                              value={passwordData.currentPassword}
                              onChange={(e) => setPasswordData({...passwordData, currentPassword: e.target.value})}
                              className="w-full px-3 py-2 bg-white/40 backdrop-blur-md rounded-xl pr-10 text-gray-900 placeholder-gray-600"
                              onFocus={(e) => {
                                e.currentTarget.style.borderColor = '#e4f223';
                                e.currentTarget.style.boxShadow = '0 0 0 2px rgba(228, 242, 35, 0.2)';
                              }}
                              onBlur={(e) => {
                                e.currentTarget.style.borderColor = 'transparent';
                                e.currentTarget.style.boxShadow = 'none';
                              }}
                              required
                            />
                            <button
                              type="button"
                              onClick={() => setShowPasswords({...showPasswords, current: !showPasswords.current})}
                              className="absolute right-3 top-2.5 text-gray-400 hover:text-gray-600"
                            >
                              {showPasswords.current ? <EyeOff size={20} /> : <Eye size={20} />}
                            </button>
                          </div>
                        </div>
                        
                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-2">
                            New Password
                          </label>
                          <div className="relative">
                            <input
                              type={showPasswords.new ? 'text' : 'password'}
                              value={passwordData.newPassword}
                              onChange={(e) => setPasswordData({...passwordData, newPassword: e.target.value})}
                              className="w-full px-3 py-2 bg-white/40 backdrop-blur-md rounded-xl pr-10 text-gray-900 placeholder-gray-600"
                              onFocus={(e) => {
                                e.currentTarget.style.borderColor = '#e4f223';
                                e.currentTarget.style.boxShadow = '0 0 0 2px rgba(228, 242, 35, 0.2)';
                              }}
                              onBlur={(e) => {
                                e.currentTarget.style.borderColor = 'transparent';
                                e.currentTarget.style.boxShadow = 'none';
                              }}
                              required
                            />
                            <button
                              type="button"
                              onClick={() => setShowPasswords({...showPasswords, new: !showPasswords.new})}
                              className="absolute right-3 top-2.5 text-gray-400 hover:text-gray-600"
                            >
                              {showPasswords.new ? <EyeOff size={20} /> : <Eye size={20} />}
                            </button>
                          </div>
                        </div>
                        
                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-2">
                            Confirm New Password
                          </label>
                          <div className="relative">
                            <input
                              type={showPasswords.confirm ? 'text' : 'password'}
                              value={passwordData.confirmPassword}
                              onChange={(e) => setPasswordData({...passwordData, confirmPassword: e.target.value})}
                              className="w-full px-3 py-2 bg-white/40 backdrop-blur-md rounded-xl pr-10 text-gray-900 placeholder-gray-600"
                              onFocus={(e) => {
                                e.currentTarget.style.borderColor = '#e4f223';
                                e.currentTarget.style.boxShadow = '0 0 0 2px rgba(228, 242, 35, 0.2)';
                              }}
                              onBlur={(e) => {
                                e.currentTarget.style.borderColor = 'transparent';
                                e.currentTarget.style.boxShadow = 'none';
                              }}
                              required
                            />
                            <button
                              type="button"
                              onClick={() => setShowPasswords({...showPasswords, confirm: !showPasswords.confirm})}
                              className="absolute right-3 top-2.5 text-gray-400 hover:text-gray-600"
                            >
                              {showPasswords.confirm ? <EyeOff size={20} /> : <Eye size={20} />}
                            </button>
                          </div>
                        </div>
                        
                        <div className="flex space-x-4">
                          <button
                            type="submit"
                            className="backdrop-blur-sm text-white px-6 py-2 rounded-xl transition-colors shadow-lg"
                            style={{ backgroundColor: 'rgba(228, 242, 35, 0.8)' }}
                            onMouseEnter={(e) => e.currentTarget.style.backgroundColor = 'rgba(212, 226, 19, 0.8)'}
                            onMouseLeave={(e) => e.currentTarget.style.backgroundColor = 'rgba(228, 242, 35, 0.8)'}
                          >
                            Update Password
                          </button>
                          <button
                            type="button"
                            onClick={() => setShowPasswordForm(false)}
                            className="bg-gray-500/80 backdrop-blur-sm text-white px-6 py-2 rounded-xl hover:bg-gray-600/80 transition-colors shadow-lg"
                          >
                            Cancel
                          </button>
                        </div>
                      </form>
                    )}
                  </div>
                  
                  <div className="bg-white/30 backdrop-blur-md border border-white/40 rounded-2xl shadow-xl p-6">
                    <div className="flex items-center justify-between">
                      <div>
                        <h3 className="text-lg font-medium text-gray-900">Account Information</h3>
                        <p className="text-sm text-gray-600">Your account details and preferences</p>
                      </div>
                      <button className="bg-gray-600/80 backdrop-blur-sm text-white px-4 py-2 rounded-xl hover:bg-gray-700/80 transition-colors shadow-lg">
                        Edit Profile
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
    </SmoothPageTransition>
  );
}
