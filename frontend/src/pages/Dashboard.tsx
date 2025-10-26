import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import Header from '../components/Header';

interface Interview {
  id: string;
  role: string;
  company: string;
  date: string;
  focus: string;
  difficulty: string;
  duration: number;
  score: number;
  questions: number;
  overall_score?: {
    overall_score: number;
    grade: string;
    cv_score: number;
    communication_score: number;
  };
  cv_analysis?: any;
  transcript_analysis?: any;
  ai_insights?: {
    feedback: string;
  };
}

interface DashboardStats {
  totalInterviews: number;
  averageScore: number;
  practiceTime: number; // in minutes
  improvement: number; // percentage improvement
}

interface InterviewDetail {
  questions: Array<{
    question: string;
    answer: string;
    score?: number;
  }>;
  feedback: string;
}

export default function Dashboard() {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [interviews, setInterviews] = useState<Interview[]>([]);
  const [stats, setStats] = useState<DashboardStats>({
    totalInterviews: 0,
    averageScore: 0,
    practiceTime: 0,
    improvement: 0
  });
  const [selectedInterview, setSelectedInterview] = useState<Interview | null>(null);
  const [interviewDetail, setInterviewDetail] = useState<InterviewDetail | null>(null);
  const [showModal, setShowModal] = useState(false);

  // Fetch user's interview data
  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      const token = localStorage.getItem('hirely_token');
      if (!token) {
        navigate('/login');
        return;
      }

      // Fetch user's interviews
      const response = await fetch('http://localhost:8000/api/v1/users/me/interviews', {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (response.ok) {
        const data = await response.json();
        
        // Map backend data to frontend format
        const mappedInterviews = (data.interviews || []).map((i: any) => ({
          id: i.id,
          role: i.position_title || 'Unknown Role',
          company: i.company_name || 'Unknown Company',
          date: i.created_at,
          focus: i.interview_type || 'mixed',
          difficulty: 'intermediate', // Default since backend doesn't have this
          duration: i.duration_minutes || 0,
          score: 0, // Will be calculated from analysis if available
          questions: i.questions?.length || 0,
          overall_score: i.overall_score,
          cv_analysis: i.cv_analysis,
          transcript_analysis: i.transcript_analysis,
          ai_insights: i.ai_insights
        }));
        
        setInterviews(mappedInterviews);
        
        // Calculate stats
        const totalInterviews = mappedInterviews.length;
        const scores = mappedInterviews.map((i: Interview) => i.score).filter(Boolean);
        const averageScore = scores.length > 0 ? Math.round(scores.reduce((a: number, b: number) => a + b, 0) / scores.length) : 0;
        const totalDuration = mappedInterviews.reduce((sum: number, i: Interview) => sum + (i.duration || 0), 0);
        
        // Calculate improvement (compare last 2 interviews)
        let improvement = 0;
        if (scores.length >= 2) {
          const recent = scores.slice(-2);
          improvement = Math.round(((recent[1] - recent[0]) / recent[0]) * 100);
        }

        setStats({
          totalInterviews,
          averageScore,
          practiceTime: Math.round(totalDuration / 60), // convert to hours
          improvement
        });
      }
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleInterviewClick = async (interview: Interview) => {
    setSelectedInterview(interview);
    setShowModal(true);
    
    // Fetch detailed interview data
    try {
      const token = localStorage.getItem('hirely_token');
      const response = await fetch(`http://localhost:8000/api/v1/interview-analysis/results/${interview.id}`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (response.ok) {
        const data = await response.json();
        // Extract questions and answers from transcript analysis
        const questions = extractQuestionsAndAnswers(data.transcript_analysis);
        setInterviewDetail({
          questions,
          feedback: data.ai_insights?.feedback || 'No feedback available'
        });
      }
    } catch (error) {
      console.error('Error fetching interview details:', error);
      setInterviewDetail({
        questions: [],
        feedback: 'Error loading interview details'
      });
    }
  };

  const extractQuestionsAndAnswers = (transcriptAnalysis: any) => {
    // This is a placeholder - you'll need to implement based on your actual data structure
    // For now, return mock data
    return [
      {
        question: "Explain the difference between REST and GraphQL",
        answer: "REST is a stateless architectural style that uses HTTP methods...",
        score: 85
      },
      {
        question: "How would you optimize a slow database query?",
        answer: "I would first analyze the query execution plan...",
        score: 90
      }
    ];
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { 
      month: 'short', 
      day: 'numeric',
      year: 'numeric'
    });
  };

  const getDifficultyColor = (difficulty: string) => {
    if (!difficulty) return 'bg-gray-100 text-gray-800';
    switch (difficulty.toLowerCase()) {
      case 'beginner': return 'bg-green-100 text-green-800';
      case 'intermediate': return 'bg-yellow-100 text-yellow-800';
      case 'advanced': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getFocusColor = (focus: string) => {
    if (!focus) return 'bg-gray-100 text-gray-800';
    switch (focus.toLowerCase()) {
      case 'technical': return 'bg-blue-100 text-blue-800';
      case 'behavioral': return 'bg-purple-100 text-purple-800';
      case 'system_design': 
      case 'system-design': return 'bg-orange-100 text-orange-800';
      case 'mixed': return 'bg-indigo-100 text-indigo-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-lg font-semibold">Loading dashboard...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Header />
      
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-24 pb-8">
        {/* Header Section */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Interview Dashboard</h1>
          <p className="text-gray-600 text-lg">Track your progress and start new mock interviews.</p>
        </div>

        {/* KPI Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 hover:shadow-md transition-shadow">
            <div>
              <p className="text-sm font-medium text-gray-600 mb-1">Total Interviews</p>
              <p className="text-2xl font-bold text-gray-900">{stats.totalInterviews}</p>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 hover:shadow-md transition-shadow">
            <div>
              <p className="text-sm font-medium text-gray-600 mb-1">Average Score</p>
              <p className="text-2xl font-bold text-gray-900">{stats.averageScore}%</p>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 hover:shadow-md transition-shadow">
            <div>
              <p className="text-sm font-medium text-gray-600 mb-1">Practice Time</p>
              <p className="text-2xl font-bold text-gray-900">{stats.practiceTime}h</p>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 hover:shadow-md transition-shadow">
            <div>
              <p className="text-sm font-medium text-gray-600 mb-1">Improvement</p>
              <p className="text-2xl font-bold text-gray-900">+{stats.improvement}%</p>
            </div>
          </div>
        </div>

        {/* New Interview Button */}
        <div className="mb-8">
          <button
            onClick={() => navigate('/interview/setup')}
            className="bg-black text-white px-6 py-3 rounded-lg font-semibold hover:bg-gray-800 transition-colors shadow-sm hover:shadow-md"
          >
            New Interview
          </button>
        </div>

        {/* Interview History */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200">
          <div className="px-6 py-4 border-b border-gray-200">
            <h2 className="text-lg font-semibold text-gray-900">Interview History</h2>
          </div>
          
          {interviews.length === 0 ? (
            <div className="px-6 py-16 text-center">
              <div className="w-20 h-20 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-6">
                <svg className="w-10 h-10 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-3">No interviews yet</h3>
              <p className="text-gray-600 mb-6 max-w-md mx-auto">Start your first mock interview to see your progress here. Track your improvement over time.</p>
              <button
                onClick={() => navigate('/interview/setup')}
                className="bg-black text-white px-8 py-3 rounded-lg font-semibold hover:bg-gray-800 transition-colors shadow-sm hover:shadow-md"
              >
                Start First Interview
              </button>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Role</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Date</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Focus</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Difficulty</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Duration</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Score</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Questions</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">View</th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {interviews.map((interview) => (
                    <tr key={interview.id} className="hover:bg-gray-50 transition-colors">
                      <td className="px-6 py-4">
                        <div className="min-w-0">
                          <div className="text-sm font-medium text-gray-900 truncate">{interview.role}</div>
                          <div className="text-sm text-gray-500 truncate">{interview.company}</div>
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        <div className="flex items-center text-sm text-gray-900 min-w-0">
                          <svg className="w-4 h-4 text-gray-400 mr-2 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                          </svg>
                          <span className="truncate">{formatDate(interview.date)}</span>
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getFocusColor(interview.focus)}`}>
                          {interview.focus}
                        </span>
                      </td>
                      <td className="px-6 py-4">
                        <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getDifficultyColor(interview.difficulty)}`}>
                          {interview.difficulty}
                        </span>
                      </td>
                      <td className="px-6 py-4">
                        <div className="flex items-center text-sm text-gray-900 min-w-0">
                          <svg className="w-4 h-4 text-gray-400 mr-2 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                          </svg>
                          <span className="truncate">{interview.duration} min</span>
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        <div className="flex items-center text-sm text-gray-900 min-w-0">
                          <svg className="w-4 h-4 text-gray-400 mr-2 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                          </svg>
                          <span className="truncate">{interview.score}%</span>
                        </div>
                      </td>
                      <td className="px-6 py-4 text-sm text-gray-900">
                        {interview.questions}
                      </td>
                      <td className="px-6 py-4">
                        <button
                          onClick={() => handleInterviewClick(interview)}
                          className="text-indigo-600 hover:text-indigo-900 flex items-center gap-1 text-sm font-medium transition-colors"
                        >
                          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                          </svg>
                          View
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>

      {/* Interview Detail Modal */}
      {showModal && selectedInterview && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg max-w-4xl w-full max-h-[90vh] overflow-y-auto">
            <div className="px-6 py-4 border-b border-gray-200 flex items-center justify-between">
              <h2 className="text-xl font-semibold text-gray-900">{selectedInterview.role}</h2>
              <button
                onClick={() => setShowModal(false)}
                className="text-gray-400 hover:text-gray-600"
              >
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
            
            <div className="px-6 py-4">
              <div className="mb-6">
                <div className="flex items-center gap-4 mb-4">
                  <div className="flex items-center text-sm text-gray-600">
                    <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                    </svg>
                    {formatDate(selectedInterview.date)}
                  </div>
                  <div className="flex items-center text-sm text-gray-600">
                    <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    {selectedInterview.duration} minutes
                  </div>
                  <div className="flex items-center text-sm text-gray-600">
                    <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
                    </svg>
                    {selectedInterview.difficulty}
                  </div>
                  <div className="flex items-center text-sm text-gray-600">
                    <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    {selectedInterview.focus}
                  </div>
                </div>
                
                <div className="bg-gray-50 rounded-lg p-4 mb-6">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm font-medium text-gray-700">Overall Score</span>
                    <span className="text-2xl font-bold text-gray-900">{selectedInterview.score}%</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div 
                      className="bg-green-500 h-2 rounded-full" 
                      style={{ width: `${selectedInterview.score}%` }}
                    ></div>
                  </div>
                  <p className="text-sm text-gray-600 mt-2">Good</p>
                </div>

                <div className="grid grid-cols-3 gap-4 mb-6">
                  <div className="bg-white border border-gray-200 rounded-lg p-4 text-center">
                    <div className="text-2xl font-bold text-gray-900">{selectedInterview.questions}</div>
                    <div className="text-sm text-gray-600">Questions Answered</div>
                  </div>
                  <div className="bg-white border border-gray-200 rounded-lg p-4 text-center">
                    <div className="text-2xl font-bold text-gray-900">{selectedInterview.score}%</div>
                    <div className="text-sm text-gray-600">Average Score</div>
                  </div>
                  <div className="bg-white border border-gray-200 rounded-lg p-4 text-center">
                    <div className="text-2xl font-bold text-gray-900">{Math.round(selectedInterview.duration / selectedInterview.questions)} min</div>
                    <div className="text-sm text-gray-600">Time per Question</div>
                  </div>
                </div>
              </div>

              {/* Questions & Answers */}
              <div className="mb-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Questions & Feedback</h3>
                {interviewDetail?.questions.map((qa, index) => (
                  <div key={index} className="mb-6 border border-gray-200 rounded-lg p-4">
                    <div className="mb-3">
                      <h4 className="font-medium text-gray-900 mb-2">Question {index + 1}</h4>
                      <p className="text-gray-700">{qa.question}</p>
                    </div>
                    <div className="mb-3">
                      <h4 className="font-medium text-gray-900 mb-2">Your Answer</h4>
                      <p className="text-gray-700">{qa.answer}</p>
                    </div>
                    {qa.score && (
                      <div className="flex items-center gap-2">
                        <span className="text-sm font-medium text-gray-600">Score:</span>
                        <span className="text-sm font-bold text-gray-900">{qa.score}%</span>
                      </div>
                    )}
                  </div>
                ))}
              </div>

              {/* AI Feedback */}
              {interviewDetail?.feedback && (
                <div className="border-t border-gray-200 pt-6">
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">AI Feedback</h3>
                  <div className="bg-blue-50 rounded-lg p-4">
                    <p className="text-gray-700">{interviewDetail.feedback}</p>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
