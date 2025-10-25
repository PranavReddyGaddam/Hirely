import React, { useState } from 'react';
import Header from '../components/Header';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import { PageLoadingWrapper } from '../components/SkeletonLoader';

export default function InterviewSetup() {
  const { isAuthenticated } = useAuth();
  const navigate = useNavigate();
  
  // All hooks must be called before any conditional returns
  const [form, setForm] = useState({
    company_name: '',
    position_title: '',
    job_link: '',
    job_description: '',
    question_count: 5,
    interview_type: 'mixed',
    focus_areas: [] as string[],
    difficulty_level: 'medium'
  });
  const [submitting, setSubmitting] = useState(false);

  // Redirect to login if not authenticated
  if (!isAuthenticated) {
    navigate('/login');
    return null;
  }

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setForm(prev => ({ ...prev, [name]: value }));
  };

  const handleCheckboxChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, checked } = e.target;
    setForm(prev => ({
      ...prev,
      focus_areas: checked 
        ? [...prev.focus_areas, name]
        : prev.focus_areas.filter(area => area !== name)
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    
    try {
      const response = await fetch('http://localhost:8000/api/v1/interviews/setup', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('hirely_token')}`,
        },
        body: JSON.stringify(form),
      });

      if (response.ok) {
        const interview = await response.json();
        // Save interview type to localStorage for fallback
        localStorage.setItem(`interview_${interview.id}_type`, form.interview_type);
        console.log('Saved interview type to localStorage:', form.interview_type);
        // Navigate to the interview session with the generated questions
        navigate(`/interview/${interview.id}`);
      } else {
        const error = await response.json();
        alert(`Error creating interview: ${error.detail || 'Unknown error'}`);
      }
    } catch (err) {
      console.error('Error creating interview:', err);
      alert('Network error. Please try again.');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <PageLoadingWrapper isLoading={submitting}>
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
          <div className="w-full max-w-2xl px-4">
            <div className="bg-white/10 backdrop-blur-md rounded-3xl p-8 shadow-lg" style={{ boxShadow: '0 10px 25px rgba(228, 242, 35, 0.2)' }}>
              <div className="text-center mb-8">
                <h1 className="text-3xl font-bold text-black mb-2">Interview Setup</h1>
                <p className="text-black/80">Enter job details to tailor your mock interview</p>
              </div>

              <form onSubmit={handleSubmit} className="space-y-6">
                <div className="grid md:grid-cols-2 gap-6">
                  <div>
                    <label htmlFor="company_name" className="block text-sm font-semibold text-black mb-2">
                      Company Name
                    </label>
                    <input
                      id="company_name"
                      name="company_name"
                      type="text"
                      value={form.company_name}
                      onChange={handleChange}
                      className="w-full px-4 py-3 bg-white/20 backdrop-blur-sm rounded-xl text-black placeholder-black/60 focus:outline-none transition-all duration-300"
                      onFocus={(e) => {
                        e.currentTarget.style.borderColor = '#e4f223';
                        e.currentTarget.style.boxShadow = '0 0 0 2px rgba(228, 242, 35, 0.2)';
                      }}
                      onBlur={(e) => {
                        e.currentTarget.style.borderColor = 'transparent';
                        e.currentTarget.style.boxShadow = 'none';
                      }}
                      placeholder="e.g., OpenAI"
                    />
                  </div>
                  <div>
                    <label htmlFor="position_title" className="block text-sm font-semibold text-black mb-2">
                      Position Title
                    </label>
                    <input
                      id="position_title"
                      name="position_title"
                      type="text"
                      value={form.position_title}
                      onChange={handleChange}
                      className="w-full px-4 py-3 bg-white/20 backdrop-blur-sm rounded-xl text-black placeholder-black/60 focus:outline-none transition-all duration-300"
                      onFocus={(e) => {
                        e.currentTarget.style.borderColor = '#e4f223';
                        e.currentTarget.style.boxShadow = '0 0 0 2px rgba(228, 242, 35, 0.2)';
                      }}
                      onBlur={(e) => {
                        e.currentTarget.style.borderColor = 'transparent';
                        e.currentTarget.style.boxShadow = 'none';
                      }}
                      placeholder="e.g., ML Engineer"
                    />
                  </div>
                </div>

                <div>
                  <label htmlFor="job_link" className="block text-sm font-semibold text-black mb-2">
                    Job Posting Link (optional)
                  </label>
                  <input
                    id="job_link"
                    name="job_link"
                    type="url"
                    value={form.job_link}
                    onChange={handleChange}
                    className="w-full px-4 py-3 bg-white/20 backdrop-blur-sm border border-white/30 rounded-xl text-black placeholder-black/60 focus:outline-none focus:ring-2 focus:ring-lime-500 focus:border-lime-500 transition-all duration-300"
                    placeholder="https://company.com/jobs/..."
                  />
                </div>

                <div>
                  <label htmlFor="job_description" className="block text-sm font-semibold text-black mb-2">
                    Job Description / Notes
                  </label>
                  <textarea
                    id="job_description"
                    name="job_description"
                    value={form.job_description}
                    onChange={handleChange}
                    className="w-full h-32 px-4 py-3 bg-white/20 rounded-xl text-black placeholder-black/60 focus:outline-none resize-none"
                    onFocus={(e) => {
                      e.currentTarget.style.borderColor = '#e4f223';
                      e.currentTarget.style.boxShadow = '0 0 0 2px rgba(228, 242, 35, 0.2)';
                    }}
                    onBlur={(e) => {
                      e.currentTarget.style.borderColor = 'transparent';
                      e.currentTarget.style.boxShadow = 'none';
                    }}
                    placeholder="Paste the JD or any notes you'd like the AI to consider"
                  />
                </div>

                {/* Interview Customization Section */}
                <div className="border-t border-white/20 pt-6">
                  <h3 className="text-lg font-semibold text-black mb-4">Interview Customization</h3>
                  
                  <div className="grid md:grid-cols-2 gap-6">
                    <div>
                      <label htmlFor="question_count" className="block text-sm font-semibold text-black mb-2">
                        Number of Questions
                      </label>
                      <select
                        id="question_count"
                        name="question_count"
                        value={form.question_count}
                        onChange={handleChange}
                        className="w-full px-4 py-3 bg-white/20 backdrop-blur-sm rounded-xl text-black focus:outline-none transition-all duration-300"
                        onFocus={(e) => {
                          e.currentTarget.style.borderColor = '#e4f223';
                          e.currentTarget.style.boxShadow = '0 0 0 2px rgba(228, 242, 35, 0.2)';
                        }}
                        onBlur={(e) => {
                          e.currentTarget.style.borderColor = 'transparent';
                          e.currentTarget.style.boxShadow = 'none';
                        }}
                      >
                        <option value={1}>1 Question (Quick Practice)</option>
                        <option value={3}>3 Questions</option>
                        <option value={5}>5 Questions</option>
                        <option value={7}>7 Questions</option>
                        <option value={10}>10 Questions</option>
                      </select>
                    </div>

                    <div>
                      <label htmlFor="interview_type" className="block text-sm font-semibold text-black mb-2">
                        Interview Type
                      </label>
                      <select
                        id="interview_type"
                        name="interview_type"
                        value={form.interview_type}
                        onChange={handleChange}
                        className="w-full px-4 py-3 bg-white/20 backdrop-blur-sm rounded-xl text-black focus:outline-none transition-all duration-300"
                        onFocus={(e) => {
                          e.currentTarget.style.borderColor = '#e4f223';
                          e.currentTarget.style.boxShadow = '0 0 0 2px rgba(228, 242, 35, 0.2)';
                        }}
                        onBlur={(e) => {
                          e.currentTarget.style.borderColor = 'transparent';
                          e.currentTarget.style.boxShadow = 'none';
                        }}
                      >
                        <option value="mixed">Mixed (Behavioral + Technical)</option>
                        <option value="behavioral">Behavioral Only</option>
                        <option value="technical">Technical Only</option>
                        <option value="system_design">System Design</option>
                        <option value="mock_interview">Mock Interview</option>
                      </select>
                    </div>
                  </div>

                  <div className="mt-4">
                    <label htmlFor="difficulty_level" className="block text-sm font-semibold text-black mb-2">
                      Difficulty Level
                    </label>
                    <select
                      id="difficulty_level"
                      name="difficulty_level"
                      value={form.difficulty_level}
                      onChange={handleChange}
                      className="w-full px-4 py-3 bg-white/20 backdrop-blur-sm border border-white/30 rounded-xl text-black focus:outline-none focus:ring-2 focus:ring-lime-500 focus:border-lime-500 transition-all duration-300"
                    >
                      <option value="easy">Easy</option>
                      <option value="medium">Medium</option>
                      <option value="hard">Hard</option>
                    </select>
                  </div>

                  <div className="mt-4">
                    <label className="block text-sm font-semibold text-black mb-3">
                      Focus Areas (Select all that apply)
                    </label>
                    <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                      {[
                        'communication',
                        'problem_solving',
                        'leadership',
                        'technical_skills',
                        'teamwork',
                        'adaptability',
                        'creativity',
                        'analytical_thinking'
                      ].map((area) => (
                        <label key={area} className="flex items-center space-x-2 cursor-pointer">
                          <input
                            type="checkbox"
                            name={area}
                            checked={form.focus_areas.includes(area)}
                            onChange={handleCheckboxChange}
                            className="w-4 h-4 bg-white/20 rounded focus:ring-2"
                            style={{ accentColor: '#e4f223' }}
                          />
                          <span className="text-sm text-black capitalize">
                            {area.replace('_', ' ')}
                          </span>
                        </label>
                      ))}
                    </div>
                  </div>
                </div>

                <div className="flex justify-end gap-3">
                  <button
                    type="button"
                    onClick={() => navigate('/')}
                    className="px-6 py-3 bg-white/20 text-black rounded-xl font-semibold hover:bg-white/30 transition-colors"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    disabled={submitting}
                    className="px-6 py-3 text-black rounded-xl font-semibold transition-colors disabled:opacity-50"
                    style={{ backgroundColor: '#e4f223' }}
                    onMouseEnter={(e) => !e.currentTarget.disabled && (e.currentTarget.style.backgroundColor = '#d4e213')}
                    onMouseLeave={(e) => !e.currentTarget.disabled && (e.currentTarget.style.backgroundColor = '#e4f223')}
                  >
                    {submitting ? 'Creating...' : 'Create Interview'}
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      </div>
      </div>
    </PageLoadingWrapper>
  );
}
