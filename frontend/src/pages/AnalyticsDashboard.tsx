import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import Header from '../components/Header';

interface AnalysisData {
  interview_id: string;
  status: string;
  overall_score?: {
    overall_score: number;
    grade: string;
    cv_score: number;
    communication_score: number;
    rating: string;
  };
  cv_analysis?: any;
  transcript_analysis?: any;
  enhanced_metrics?: {
    cv_detailed?: any;
    communication_detailed?: any;
    comparison_to_benchmarks?: any;
    improvement_roadmap?: Array<{
      priority: string;
      category: string;
      issue: string;
      current: string;
      target: string;
      impact: string;
      action: string;
    }>;
  };
  ai_insights?: {
    feedback: string;
    error?: string;
    error_type?: string;
    success?: boolean;
    model?: string;
  };
  error?: string;
}

export default function AnalyticsDashboard() {
  const { interviewId } = useParams<{ interviewId: string }>();
  const navigate = useNavigate();
  
  const [loading, setLoading] = useState(true);
  const [progress, setProgress] = useState(0);
  const [statusMessage, setStatusMessage] = useState('Starting analysis...');
  const [analysisData, setAnalysisData] = useState<AnalysisData | null>(null);
  const [error, setError] = useState<string | null>(null);

  // Poll for analysis status
  useEffect(() => {
    if (!interviewId) return;

    const pollInterval = setInterval(async () => {
      try {
        const token = localStorage.getItem('hirely_token');
        if (!token) {
          setError('Authentication required');
          setLoading(false);
          clearInterval(pollInterval);
          return;
        }

        // Check status
        const statusResponse = await fetch(
          `http://localhost:8000/api/v1/interview-analysis/status/${interviewId}`,
          {
            headers: {
              'Authorization': `Bearer ${token}`,
              'Content-Type': 'application/json'
            }
          }
        );

        if (statusResponse.ok) {
          const statusData = await statusResponse.json();
          setProgress(statusData.progress || 0);
          setStatusMessage(statusData.message || 'Processing...');

          // If completed, fetch results
          if (statusData.status === 'completed') {
            const resultsResponse = await fetch(
              `http://localhost:8000/api/v1/interview-analysis/results/${interviewId}`,
              {
                headers: {
                  'Authorization': `Bearer ${token}`,
                  'Content-Type': 'application/json'
                }
              }
            );

            if (resultsResponse.ok) {
              const results = await resultsResponse.json();
              setAnalysisData(results);
              setLoading(false);
              clearInterval(pollInterval);
            }
          } else if (statusData.status === 'failed') {
            setError(statusData.message || 'Analysis failed');
            setLoading(false);
            clearInterval(pollInterval);
          }
        }
      } catch (err) {
        console.error('Error polling analysis status:', err);
      }
    }, 2000); // Poll every 2 seconds

    return () => clearInterval(pollInterval);
  }, [interviewId]);

  if (loading) {
    return (
      <div className="min-h-screen relative overflow-hidden" style={{
        backgroundImage: 'url(/mountains.png)',
        backgroundSize: 'cover',
        backgroundPosition: 'center',
        backgroundAttachment: 'fixed'
      }}>
        <div className="absolute inset-0 bg-black/40 backdrop-blur-sm"></div>
        <Header variant="light" />
        <div className="relative z-10 flex items-center justify-center min-h-[80vh]">
          <div className="bg-white/10 backdrop-blur-xl border border-white/20 rounded-3xl shadow-2xl p-12 max-w-md mx-auto px-8">
            {/* Animated Spinner */}
            <div className="relative w-32 h-32 mx-auto mb-8">
              <div className="absolute inset-0 border-8 border-gray-300 rounded-full"></div>
              <div 
                className="absolute inset-0 border-8 border-blue-500 rounded-full border-t-transparent animate-spin"
              ></div>
              <div className="absolute inset-0 flex items-center justify-center">
                <span className="text-2xl font-bold text-gray-900">{progress}%</span>
              </div>
            </div>

            <h2 className="text-3xl font-bold text-gray-900 mb-3 text-center">
              Analyzing Your Interview
            </h2>
            <p className="text-gray-800 mb-6 text-center">{statusMessage}</p>

            {/* Progress Bar */}
            <div className="w-full bg-gray-200/50 rounded-full h-3 mb-4">
              <div 
                className="bg-gradient-to-r from-blue-400 to-blue-600 h-3 rounded-full transition-all duration-500"
                style={{ width: `${progress}%` }}
              ></div>
            </div>

            <div className="space-y-2 text-sm text-gray-800">
              <p>Video uploaded to secure storage</p>
              <p className={progress > 30 ? 'text-gray-900 font-medium' : 'text-gray-600'}>
                Analyzing visual behavior (facial expressions, posture, eye contact)
              </p>
              <p className={progress > 60 ? 'text-gray-900 font-medium' : 'text-gray-600'}>
                Analyzing communication (filler words, pace, vocabulary)
              </p>
              <p className={progress > 90 ? 'text-gray-900 font-medium' : 'text-gray-600'}>
                Generating AI-powered insights
              </p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen relative overflow-hidden" style={{
        backgroundImage: 'url(/mountains.png)',
        backgroundSize: 'cover',
        backgroundPosition: 'center',
        backgroundAttachment: 'fixed'
      }}>
        <div className="absolute inset-0 bg-black/40 backdrop-blur-sm"></div>
        <Header variant="light" />
        <div className="flex items-center justify-center min-h-[80vh]">
          <div className="text-center max-w-md mx-auto px-4">
            <h2 className="text-2xl font-bold text-red-600 mb-3">Analysis Error</h2>
            <p className="text-gray-800 mb-6">{error}</p>
            <button
              onClick={() => navigate('/profile')}
              className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
            >
              Back to Profile
            </button>
          </div>
        </div>
      </div>
    );
  }

  if (!analysisData) {
    return (
      <div className="min-h-screen bg-gray-50">
        <Header />
        <div className="flex items-center justify-center min-h-[80vh]">
          <div className="text-center">
            <p className="text-gray-800">No analysis data available</p>
          </div>
        </div>
      </div>
    );
  }

  const { overall_score, cv_analysis, transcript_analysis, ai_insights } = analysisData;

  return (
    <div className="min-h-screen relative overflow-hidden" style={{
      backgroundImage: 'url(/mountains.png)',
      backgroundSize: 'cover',
      backgroundPosition: 'center',
      backgroundAttachment: 'fixed'
    }}>
      <div className="absolute inset-0 bg-black/30 backdrop-blur-sm"></div>
      
      <div className="relative z-10">
        <Header variant="light" />
        
        <div className="max-w-7xl mx-auto px-4 pt-24 pb-8">
          {/* Header Section */}
          <div className="text-center mb-8">
            <h1 className="text-4xl font-bold text-gray-900 mb-2">
              Interview Analysis Report
            </h1>
            <p className="text-gray-800">Comprehensive performance breakdown</p>
          </div>

          {/* Overall Score Card */}
        {overall_score && (
          <div className="bg-white/20 backdrop-blur-xl border border-white/30 rounded-3xl shadow-2xl p-8 mb-8 text-gray-800">
            <div className="flex items-center justify-between flex-wrap gap-4">
              <div>
                <h2 className="text-2xl font-bold mb-2">Overall Performance</h2>
                <p className="text-gray-600">Combined CV and Communication Analysis</p>
              </div>
              <div className="text-center">
                <div className="text-6xl font-bold mb-2">{overall_score.overall_score}</div>
                <div className="text-2xl font-semibold bg-white/30 rounded-full px-6 py-2 text-gray-800">
                  Grade: {overall_score.grade}
                </div>
              </div>
            </div>
            
            <div className="grid md:grid-cols-2 gap-4 mt-6">
              <div className="bg-white/30 backdrop-blur rounded-xl p-4">
                <div className="text-sm text-gray-600 mb-1">Visual Behavior Score</div>
                <div className="text-3xl font-bold text-gray-800">{overall_score.cv_score}/100</div>
              </div>
              <div className="bg-white/30 backdrop-blur rounded-xl p-4">
                <div className="text-sm text-gray-600 mb-1">Communication Score</div>
                <div className="text-3xl font-bold text-gray-800">{overall_score.communication_score}/100</div>
              </div>
            </div>
          </div>
        )}

        <div className="grid lg:grid-cols-2 gap-6 mb-8">
          {/* CV Analysis Section */}
          {cv_analysis && (
            <div className="bg-white/20 backdrop-blur-xl border border-white/30 rounded-3xl shadow-2xl p-6">
              <h3 className="text-2xl font-bold text-gray-800 mb-6">
                Visual Behavior Analysis
              </h3>

              {/* Emotions */}
              {cv_analysis.emotions && (
                <div className="mb-6">
                  <h4 className="text-lg font-semibold text-gray-800 mb-3">Emotional State</h4>
                  <div className="space-y-2">
                    <div className="flex justify-between text-sm text-gray-700">
                      <span>Dominant Emotion:</span>
                      <span className="font-semibold capitalize">{cv_analysis.emotions.dominant_emotion}</span>
                    </div>
                    <div className="flex justify-between text-sm text-gray-700">
                      <span>Emotional Stability:</span>
                      <span className="font-semibold capitalize">{cv_analysis.emotions.emotional_stability?.score}</span>
                    </div>
                    {cv_analysis.emotions.expression_distribution && (
                      <div className="mt-3">
                        {Object.entries(cv_analysis.emotions.expression_distribution).map(([emotion, percentage]: [string, any]) => (
                          <div key={emotion} className="mb-2">
                            <div className="flex justify-between text-xs text-gray-600 mb-1">
                              <span className="capitalize">{emotion.replace('_', ' ')}</span>
                              <span>{percentage.toFixed(1)}%</span>
                            </div>
                            <div className="w-full bg-white/40 rounded-full h-2">
                              <div 
                                className="bg-blue-500 h-2 rounded-full"
                                style={{ width: `${percentage}%` }}
                              ></div>
                            </div>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                </div>
              )}

              {/* Eye Contact */}
              {cv_analysis.eye_contact && (
                <div className="mb-6">
                  <h4 className="text-lg font-semibold text-gray-800 mb-3">Eye Contact</h4>
                  <div className="space-y-2">
                    <div className="flex justify-between text-sm text-gray-700">
                      <span>Looking at Camera:</span>
                      <span className="font-semibold">{cv_analysis.eye_contact.looking_at_camera_percentage?.toFixed(1) || 0}%</span>
                    </div>
                    <div className="w-full bg-white/40 rounded-full h-3">
                      <div 
                        className="bg-green-500 h-3 rounded-full"
                        style={{ width: `${cv_analysis.eye_contact.looking_at_camera_percentage || 0}%` }}
                      ></div>
                    </div>
                  </div>
                </div>
              )}

              {/* Posture */}
              {cv_analysis.posture && (
                <div className="mb-6">
                  <h4 className="text-lg font-semibold text-gray-800 mb-3">Posture</h4>
                  <div className="space-y-2">
                    <div className="flex justify-between text-sm text-gray-700">
                      <span>Good Posture:</span>
                      <span className="font-semibold">{cv_analysis.posture.good_posture_percentage?.toFixed(1) || 0}%</span>
                    </div>
                    <div className="w-full bg-white/40 rounded-full h-3">
                      <div 
                        className="bg-blue-500 h-3 rounded-full"
                        style={{ width: `${cv_analysis.posture.good_posture_percentage || 0}%` }}
                      ></div>
                    </div>
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Transcript Analysis Section */}
          {transcript_analysis && (
            <div className="bg-white/20 backdrop-blur-xl border border-white/30 rounded-3xl shadow-2xl p-6">
              <h3 className="text-2xl font-bold text-gray-800 mb-6">
                Communication Analysis
              </h3>

              {/* Filler Words */}
              {transcript_analysis.filler_word_analysis && (
                <div className="mb-6">
                  <h4 className="text-lg font-semibold text-gray-800 mb-3">Filler Words</h4>
                  <div className="space-y-3">
                    <div className="grid grid-cols-2 gap-4">
                      <div className="bg-white/40 rounded-lg p-3">
                        <div className="text-xs text-gray-600 mb-1">Total Filler Words</div>
                        <div className="text-2xl font-bold text-gray-800">
                          {transcript_analysis.filler_word_analysis.total_filler_words}
                        </div>
                      </div>
                      <div className="bg-white/40 rounded-lg p-3">
                        <div className="text-xs text-gray-600 mb-1">Filler Percentage</div>
                        <div className="text-2xl font-bold text-gray-800">
                          {transcript_analysis.filler_word_analysis.filler_percentage}%
                        </div>
                      </div>
                    </div>
                    <div className="text-sm">
                      <span className="text-gray-600">Most used:</span>
                      <span className="ml-2 font-semibold text-blue-600">
                        "{transcript_analysis.filler_word_analysis.most_used_filler}" 
                        ({transcript_analysis.filler_word_analysis.most_used_count}x)
                      </span>
                    </div>
                    <div className={`text-sm px-3 py-2 rounded-lg ${
                      transcript_analysis.filler_word_analysis.rating === 'excellent' ? 'bg-green-100/80 text-green-800' :
                      transcript_analysis.filler_word_analysis.rating === 'good' ? 'bg-blue-100/80 text-blue-800' :
                      transcript_analysis.filler_word_analysis.rating === 'fair' ? 'bg-yellow-100/80 text-yellow-800' :
                      'bg-red-100/80 text-red-800'
                    }`}>
                      {transcript_analysis.filler_word_analysis.feedback}
                    </div>
                  </div>
                </div>
              )}

              {/* Vocabulary Diversity */}
              {transcript_analysis.word_diversity && (
                <div className="mb-6">
                  <h4 className="text-lg font-semibold text-gray-800 mb-3">Vocabulary</h4>
                  <div className="space-y-2">
                    <div className="flex justify-between text-sm text-gray-700">
                      <span>Unique Words:</span>
                      <span className="font-semibold">
                        {transcript_analysis.word_diversity.unique_words} / {transcript_analysis.word_diversity.total_words}
                      </span>
                    </div>
                    <div className="flex justify-between text-sm text-gray-700">
                      <span>Diversity Score:</span>
                      <span className="font-semibold">
                        {(transcript_analysis.word_diversity.diversity_ratio * 100).toFixed(1)}%
                      </span>
                    </div>
                    <div className="w-full bg-white/40 rounded-full h-3">
                      <div 
                        className="bg-blue-500 h-3 rounded-full"
                        style={{ width: `${transcript_analysis.word_diversity.diversity_ratio * 100}%` }}
                      ></div>
                    </div>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>

        {/* AI Insights Section */}
        {ai_insights && (
          <div className="bg-white/20 backdrop-blur-xl border border-white/30 rounded-3xl shadow-2xl p-8 mb-8">
            <h3 className="text-2xl font-bold text-gray-800 mb-6">
              AI-Powered Insights
            </h3>
            
            {ai_insights.error && !ai_insights.success ? (
              <div className="bg-red-50/80 border border-red-200 rounded-xl p-6 mb-4">
                <div className="flex items-start gap-3">
                  <div className="text-red-500 text-xl">⚠️</div>
                  <div className="flex-1">
                    <h4 className="font-semibold text-red-800 mb-2">AI Insights Unavailable</h4>
                    <p className="text-red-700 text-sm mb-3">{ai_insights.error}</p>
                    {ai_insights.error_type && (
                      <p className="text-xs text-red-600 mb-2">Error Type: {ai_insights.error_type}</p>
                    )}
                    <div className="text-xs text-red-600">
                      <p className="font-semibold mb-1">Troubleshooting tips:</p>
                      <ul className="list-disc list-inside space-y-1">
                        <li>The server administrator should check the backend logs</li>
                        <li>Verify Groq API key is configured correctly</li>
                        <li>Try refreshing the page or contact support</li>
                      </ul>
                    </div>
                  </div>
                </div>
              </div>
            ) : null}
            
            <div className="prose max-w-none text-gray-700 whitespace-pre-wrap">
              {ai_insights.feedback}
            </div>
            
            {ai_insights.model && (
              <div className="mt-4 text-xs text-gray-600 flex items-center gap-2">
                <span>🤖</span>
                <span>Generated by: {ai_insights.model}</span>
              </div>
            )}
          </div>
        )}

        {/* Performance Metrics Chart */}
        {overall_score && (
          <div className="bg-white/20 backdrop-blur-xl border border-white/30 rounded-3xl shadow-2xl p-8 mb-8">
            <h3 className="text-2xl font-bold text-gray-800 mb-6">
              Performance Breakdown
            </h3>
            <div className="space-y-6">
              {/* Visual Behavior Score Bar */}
              <div>
                <div className="flex justify-between items-center mb-2">
                  <span className="text-sm font-semibold text-gray-800">Visual Behavior</span>
                  <span className="text-sm font-bold text-gray-900">{overall_score.cv_score}/100</span>
                </div>
                <div className="w-full bg-gray-200/50 rounded-full h-4 overflow-hidden">
                  <div 
                    className="bg-gradient-to-r from-blue-400 to-blue-600 h-4 rounded-full transition-all duration-1000 ease-out"
                    style={{ width: `${overall_score.cv_score}%` }}
                  ></div>
                </div>
              </div>

              {/* Communication Score Bar */}
              <div>
                <div className="flex justify-between items-center mb-2">
                  <span className="text-sm font-semibold text-gray-800">Communication</span>
                  <span className="text-sm font-bold text-gray-900">{overall_score.communication_score}/100</span>
                </div>
                <div className="w-full bg-gray-200/50 rounded-full h-4 overflow-hidden">
                  <div 
                    className="bg-gradient-to-r from-blue-400 to-blue-600 h-4 rounded-full transition-all duration-1000 ease-out"
                    style={{ width: `${overall_score.communication_score}%` }}
                  ></div>
                </div>
              </div>

              {/* Sub-metrics from CV Analysis */}
              {cv_analysis && (
                <>
                  {cv_analysis.attention?.overall_engagement?.avg_attention_score && (
                    <div>
                      <div className="flex justify-between items-center mb-2">
                        <span className="text-sm font-medium text-gray-700">Engagement</span>
                        <span className="text-sm font-bold text-gray-800">{Math.round(cv_analysis.attention.overall_engagement.avg_attention_score * 100)}/100</span>
                      </div>
                      <div className="w-full bg-gray-200/50 rounded-full h-3 overflow-hidden">
                        <div 
                          className="bg-gradient-to-r from-blue-400 to-blue-500 h-3 rounded-full transition-all duration-1000 ease-out"
                          style={{ width: `${cv_analysis.attention.overall_engagement.avg_attention_score * 100}%` }}
                        ></div>
                      </div>
                    </div>
                  )}

                  {cv_analysis.head_pose?.camera_focus?.looking_at_camera_percentage && (
                    <div>
                      <div className="flex justify-between items-center mb-2">
                        <span className="text-sm font-medium text-gray-700">Eye Contact</span>
                        <span className="text-sm font-bold text-gray-800">{Math.round(cv_analysis.head_pose.camera_focus.looking_at_camera_percentage)}/100</span>
                      </div>
                      <div className="w-full bg-gray-200/50 rounded-full h-3 overflow-hidden">
                        <div 
                          className="bg-gradient-to-r from-blue-400 to-blue-500 h-3 rounded-full transition-all duration-1000 ease-out"
                          style={{ width: `${cv_analysis.head_pose.camera_focus.looking_at_camera_percentage}%` }}
                        ></div>
                      </div>
                    </div>
                  )}
                </>
              )}

              {/* Sub-metrics from Transcript Analysis */}
              {transcript_analysis?.word_diversity && (
                <div>
                  <div className="flex justify-between items-center mb-2">
                    <span className="text-sm font-medium text-gray-700">Vocabulary Diversity</span>
                    <span className="text-sm font-bold text-gray-800">{Math.round(transcript_analysis.word_diversity.diversity_ratio * 100)}/100</span>
                  </div>
                  <div className="w-full bg-gray-200/50 rounded-full h-3 overflow-hidden">
                    <div 
                      className="bg-gradient-to-r from-blue-400 to-blue-500 h-3 rounded-full transition-all duration-1000 ease-out"
                      style={{ width: `${transcript_analysis.word_diversity.diversity_ratio * 100}%` }}
                    ></div>
                  </div>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Interview Transcript Section */}
        {transcript_analysis?.messages && transcript_analysis.messages.length > 0 && (
          <div className="bg-white/20 backdrop-blur-xl border border-white/30 rounded-3xl shadow-2xl p-8 mb-8">
            <div className="flex items-center gap-3 mb-6">
              <span className="text-3xl">💬</span>
              <h3 className="text-2xl font-bold text-gray-800">
                Interview Conversation Transcript
              </h3>
            </div>
            
            <div className="bg-white/40 rounded-2xl p-6 max-h-96 overflow-y-auto">
              <p className="text-sm text-gray-600 mb-4 italic">
                Full conversation retrieved from ElevenLabs Voice AI
              </p>
              
              <div className="space-y-4">
                {transcript_analysis.messages.map((message: any, index: number) => (
                  <div 
                    key={index} 
                    className={`flex ${message.speaker === 'user' ? 'justify-end' : 'justify-start'}`}
                  >
                    <div 
                      className={`max-w-[80%] rounded-2xl px-4 py-3 ${
                        message.speaker === 'user' 
                          ? 'bg-blue-500 text-white' 
                          : 'bg-gray-200 text-gray-800'
                      }`}
                    >
                      <div className="flex items-center gap-2 mb-1">
                        <span className="text-xs font-semibold opacity-75">
                          {message.speaker === 'user' ? '👤 You' : '🤖 AI Interviewer'}
                        </span>
                        {message.time_in_call_secs !== undefined && (
                          <span className="text-xs opacity-60">
                            {Math.floor(message.time_in_call_secs / 60)}:{String(message.time_in_call_secs % 60).padStart(2, '0')}
                          </span>
                        )}
                      </div>
                      <p className="text-sm leading-relaxed">{message.text}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
            
            {transcript_analysis.conversation_metadata && (
              <div className="mt-4 text-sm text-gray-600 flex items-center justify-between">
                <span>
                  📊 Total Duration: {Math.floor((transcript_analysis.conversation_metadata.call_duration_secs || 0) / 60)} minutes
                </span>
                <span>
                  💬 Messages: {transcript_analysis.messages.length}
                </span>
              </div>
            )}
          </div>
        )}

        {/* Enhanced Metrics & Improvement Roadmap */}
        {analysisData?.enhanced_metrics && (
          <div className="space-y-6 mb-8">
            {/* Improvement Roadmap - Priority Section */}
            {analysisData.enhanced_metrics.improvement_roadmap && analysisData.enhanced_metrics.improvement_roadmap.length > 0 && (
              <div className="bg-gradient-to-br from-orange-50/80 to-red-50/80 backdrop-blur-xl border border-orange-200/50 rounded-3xl shadow-2xl p-6">
                <div className="flex items-center gap-3 mb-6">
                  <span className="text-3xl">🎯</span>
                  <h3 className="text-2xl font-bold text-gray-800">Your Improvement Priorities</h3>
                </div>
                
                <div className="space-y-4">
                  {analysisData.enhanced_metrics.improvement_roadmap.map((item, index) => (
                    <div 
                      key={index}
                      className={`bg-white/60 backdrop-blur rounded-xl p-4 border-l-4 ${
                        item.priority === 'high' ? 'border-red-500' :
                        item.priority === 'medium' ? 'border-yellow-500' :
                        'border-blue-500'
                      }`}
                    >
                      <div className="flex items-start justify-between mb-2">
                        <div className="flex items-center gap-2">
                          <span className={`px-2 py-1 text-xs font-bold rounded ${
                            item.priority === 'high' ? 'bg-red-100 text-red-700' :
                            item.priority === 'medium' ? 'bg-yellow-100 text-yellow-700' :
                            'bg-blue-100 text-blue-700'
                          }`}>
                            {item.priority.toUpperCase()}
                          </span>
                          <span className="text-xs text-gray-500">{item.category}</span>
                        </div>
                        <div className="text-right">
                          <div className="text-sm font-semibold text-gray-700">{item.current}</div>
                          <div className="text-xs text-gray-500">→ Target: {item.target}</div>
                        </div>
                      </div>
                      
                      <h4 className="font-bold text-gray-800 mb-2">{item.issue}</h4>
                      
                      <div className="space-y-2">
                        <div className="flex items-start gap-2">
                          <span className="text-sm">💡</span>
                          <p className="text-sm text-gray-700">
                            <strong>Impact:</strong> {item.impact}
                          </p>
                        </div>
                        <div className="flex items-start gap-2">
                          <span className="text-sm">🎬</span>
                          <p className="text-sm text-gray-700">
                            <strong>Action:</strong> {item.action}
                          </p>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Comparison to Benchmarks */}
            {analysisData.enhanced_metrics.comparison_to_benchmarks && (
              <div className="bg-white/20 backdrop-blur-xl border border-white/30 rounded-3xl shadow-2xl p-6">
                <div className="flex items-center gap-3 mb-6">
                  <span className="text-3xl">📊</span>
                  <h3 className="text-2xl font-bold text-gray-800">How You Compare</h3>
                  <span className="text-sm text-gray-600 ml-auto">vs. Average Candidates</span>
                </div>
                
                <div className="grid md:grid-cols-2 gap-4">
                  {Object.entries(analysisData.enhanced_metrics.comparison_to_benchmarks).map(([metric, data]: [string, any]) => (
                    <div key={metric} className="bg-white/40 backdrop-blur rounded-xl p-4">
                      <h4 className="font-semibold text-gray-800 capitalize mb-3">{metric.replace(/_/g, ' ')}</h4>
                      
                      <div className="space-y-2">
                        <div className="flex justify-between items-center">
                          <span className="text-sm text-gray-600">Your Score:</span>
                          <span className="font-bold text-lg text-gray-800">
                            {typeof data.your_score === 'number' ? data.your_score.toFixed(1) : data.your_score}
                            {metric.includes('percentage') || metric.includes('filler') ? '%' : ''}
                          </span>
                        </div>
                        
                        <div className="flex justify-between items-center text-xs">
                          <span className="text-gray-500">Average:</span>
                          <span className="text-gray-600">{data.average}</span>
                        </div>
                        
                        <div className="flex justify-between items-center text-xs">
                          <span className="text-gray-500">Top 10%:</span>
                          <span className="text-gray-600">{data.top_10_percent}</span>
                        </div>
                        
                        <div className="mt-2 pt-2 border-t border-gray-200">
                          <span className={`text-sm font-semibold ${
                            data.status === 'above_average' || data.status === 'on_target' ? 'text-green-600' :
                            data.status === 'below_average' || data.status === 'needs_adjustment' ? 'text-orange-600' :
                            'text-gray-600'
                          }`}>
                            {data.status === 'above_average' && '✅ Above Average'}
                            {data.status === 'below_average' && '⚠️ Below Average'}
                            {data.status === 'on_target' && '✅ On Target'}
                            {data.status === 'needs_adjustment' && '⚠️ Needs Adjustment'}
                          </span>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Detailed Metrics */}
            <div className="grid lg:grid-cols-2 gap-6">
              {/* Enhanced CV Details */}
              {analysisData.enhanced_metrics.cv_detailed && (
                <div className="bg-white/20 backdrop-blur-xl border border-white/30 rounded-3xl shadow-2xl p-6">
                  <h3 className="text-xl font-bold text-gray-800 mb-4">📹 Visual Behavior Details</h3>
                  
                  <div className="space-y-4">
                    {/* Professional Presence */}
                    {analysisData.enhanced_metrics.cv_detailed.professional_presence && (
                      <div className="bg-white/40 backdrop-blur rounded-xl p-4">
                        <div className="flex justify-between items-center mb-2">
                          <h4 className="font-semibold text-gray-800">Professional Presence</h4>
                          <span className="text-2xl font-bold text-blue-600">
                            {analysisData.enhanced_metrics.cv_detailed.professional_presence.overall_score}/100
                          </span>
                        </div>
                        <div className="text-xs text-gray-600">
                          Rating: {analysisData.enhanced_metrics.cv_detailed.professional_presence.rating}
                        </div>
                      </div>
                    )}

                    {/* Eye Contact Details */}
                    {analysisData.enhanced_metrics.cv_detailed.eye_contact_detailed && (
                      <div className="bg-white/40 backdrop-blur rounded-xl p-3">
                        <h4 className="font-semibold text-sm text-gray-800 mb-2">👁️ Eye Contact Quality</h4>
                        <div className="space-y-1 text-xs">
                          <div className="flex justify-between">
                            <span className="text-gray-600">Direct Contact:</span>
                            <span className="font-semibold">{analysisData.enhanced_metrics.cv_detailed.eye_contact_detailed.direct_contact_percentage?.toFixed(1)}%</span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-gray-600">Quality:</span>
                            <span className="font-semibold">{analysisData.enhanced_metrics.cv_detailed.eye_contact_detailed.quality_rating}</span>
                          </div>
                          {analysisData.enhanced_metrics.cv_detailed.eye_contact_detailed.tip && (
                            <div className="mt-2 p-2 bg-blue-50 rounded text-xs text-gray-700">
                              💡 {analysisData.enhanced_metrics.cv_detailed.eye_contact_detailed.tip}
                            </div>
                          )}
                        </div>
                      </div>
                    )}

                    {/* Nervousness Indicators */}
                    {analysisData.enhanced_metrics.cv_detailed.nervousness_indicators && (
                      <div className="bg-white/40 backdrop-blur rounded-xl p-3">
                        <h4 className="font-semibold text-sm text-gray-800 mb-2">😌 Nervousness Level</h4>
                        <div className="space-y-1 text-xs">
                          <div className="flex justify-between">
                            <span className="text-gray-600">Hand Fidgeting:</span>
                            <span className="font-semibold">{analysisData.enhanced_metrics.cv_detailed.nervousness_indicators.hand_fidgeting_count} times</span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-gray-600">Assessment:</span>
                            <span className="font-semibold">{analysisData.enhanced_metrics.cv_detailed.nervousness_indicators.nervousness_rating}</span>
                          </div>
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              )}

              {/* Enhanced Communication Details */}
              {analysisData.enhanced_metrics.communication_detailed && (
                <div className="bg-white/20 backdrop-blur-xl border border-white/30 rounded-3xl shadow-2xl p-6">
                  <h3 className="text-xl font-bold text-gray-800 mb-4">🎤 Communication Details</h3>
                  
                  <div className="space-y-4">
                    {/* Speech Quality */}
                    {analysisData.enhanced_metrics.communication_detailed.speech_quality && (
                      <div className="bg-white/40 backdrop-blur rounded-xl p-4">
                        <h4 className="font-semibold text-gray-800 mb-2">Speech Quality</h4>
                        <div className="space-y-1 text-xs">
                          <div className="flex justify-between">
                            <span className="text-gray-600">Pace:</span>
                            <span className="font-semibold">{analysisData.enhanced_metrics.communication_detailed.speech_quality.speaking_pace_wpm} WPM</span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-gray-600">Rating:</span>
                            <span className="font-semibold">{analysisData.enhanced_metrics.communication_detailed.speech_quality.pace_rating}</span>
                          </div>
                          {analysisData.enhanced_metrics.communication_detailed.speech_quality.tip && (
                            <div className="mt-2 p-2 bg-green-50 rounded text-xs text-gray-700">
                              💡 {analysisData.enhanced_metrics.communication_detailed.speech_quality.tip}
                            </div>
                          )}
                        </div>
                      </div>
                    )}

                    {/* Filler Analysis */}
                    {analysisData.enhanced_metrics.communication_detailed.filler_analysis_detailed && (
                      <div className="bg-white/40 backdrop-blur rounded-xl p-3">
                        <h4 className="font-semibold text-sm text-gray-800 mb-2">🗣️ Filler Word Analysis</h4>
                        <div className="space-y-1 text-xs">
                          <div className="flex justify-between">
                            <span className="text-gray-600">Total:</span>
                            <span className="font-semibold">{analysisData.enhanced_metrics.communication_detailed.filler_analysis_detailed.total_count} ({analysisData.enhanced_metrics.communication_detailed.filler_analysis_detailed.percentage?.toFixed(1)}%)</span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-gray-600">Most Used:</span>
                            <span className="font-semibold">"{analysisData.enhanced_metrics.communication_detailed.filler_analysis_detailed.most_used}"</span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-gray-600">Impact:</span>
                            <span className="font-semibold text-xs">{analysisData.enhanced_metrics.communication_detailed.filler_analysis_detailed.confidence_impact}</span>
                          </div>
                        </div>
                      </div>
                    )}

                    {/* Vocabulary Details */}
                    {analysisData.enhanced_metrics.communication_detailed.vocabulary_detailed && (
                      <div className="bg-white/40 backdrop-blur rounded-xl p-3">
                        <h4 className="font-semibold text-sm text-gray-800 mb-2">📚 Vocabulary</h4>
                        <div className="space-y-1 text-xs">
                          <div className="flex justify-between">
                            <span className="text-gray-600">Diversity:</span>
                            <span className="font-semibold">{analysisData.enhanced_metrics.communication_detailed.vocabulary_detailed.diversity_percentage?.toFixed(1)}%</span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-gray-600">Rating:</span>
                            <span className="font-semibold">{analysisData.enhanced_metrics.communication_detailed.vocabulary_detailed.rating}</span>
                          </div>
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Action Buttons */}
        <div className="flex justify-center gap-4">
          <button
            onClick={() => navigate('/profile')}
            className="px-8 py-3 bg-white/30 backdrop-blur-md border border-white/40 text-gray-800 rounded-xl hover:bg-white/40 transition-all font-semibold shadow-lg"
          >
            Back to Profile
          </button>
          <button
            onClick={() => window.print()}
            className="px-8 py-3 bg-blue-500/80 backdrop-blur-md border border-blue-500/30 text-white rounded-xl hover:bg-blue-500 transition-all font-semibold shadow-lg"
          >
            Download Report (PDF)
          </button>
        </div>
      </div>
      </div>
    </div>
  );
}

