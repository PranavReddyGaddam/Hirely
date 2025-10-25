import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import Header from '../components/Header';
import Footer from '../components/Footer';
import { useAuth } from '../hooks/useAuth';

export default function Demo() {
  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [userAnswer, setUserAnswer] = useState('');
  const [showFeedback, setShowFeedback] = useState(false);
  const { isAuthenticated, isLoading } = useAuth();
  const navigate = useNavigate();

  // Redirect to login if not authenticated
  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      navigate('/login');
    }
  }, [isAuthenticated, isLoading, navigate]);

  // Show loading while checking authentication
  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-lg font-semibold">Loading...</div>
      </div>
    );
  }

  // Don't render anything if not authenticated (will redirect)
  if (!isAuthenticated) {
    return null;
  }

  const questions = [
    {
      question: "Tell me about yourself and why you're interested in this role.",
      category: "Introduction",
      timeLimit: 120
    },
    {
      question: "Describe a challenging project you worked on and how you overcame obstacles.",
      category: "Behavioral",
      timeLimit: 180
    },
    {
      question: "How do you stay updated with the latest technologies in your field?",
      category: "Technical",
      timeLimit: 90
    }
  ];

  const feedback = {
    score: 85,
    strengths: [
      "Clear communication style",
      "Good use of specific examples",
      "Confident delivery"
    ],
    improvements: [
      "Could elaborate more on technical details",
      "Consider adding quantifiable results"
    ],
    overall: "Strong performance with room for growth in technical depth."
  };

  const handleNextQuestion = () => {
    if (currentQuestion < questions.length - 1) {
      setCurrentQuestion(currentQuestion + 1);
      setUserAnswer('');
      setShowFeedback(false);
    } else {
      setShowFeedback(true);
    }
  };

  const handleStartDemo = () => {
    setCurrentQuestion(0);
    setUserAnswer('');
    setShowFeedback(false);
  };

  if (showFeedback) {
    return (
      <div className="min-h-screen relative">
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
        <div className="relative z-10 pt-32 pb-12">
          <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="text-center mb-12">
              <h1 className="text-4xl font-bold text-slate-900 mb-4">
                Interview Complete! 🎉
              </h1>
              <p className="text-xl text-slate-700">
                Here's your performance summary
              </p>
            </div>

            <div className="bg-white/10 backdrop-blur-md border border-white/20 rounded-2xl shadow-2xl p-8 mb-8">
              <div className="text-center mb-8">
                <div className="text-6xl font-bold mb-2" style={{ color: '#e4f223' }}>
                  {feedback.score}%
                </div>
                <p className="text-slate-700">Overall Score</p>
              </div>

              <div className="grid md:grid-cols-2 gap-8">
                <div>
                  <h3 className="text-xl font-semibold text-slate-900 mb-4 flex items-center">
                    <span className="text-green-500 mr-2">✓</span>
                    Strengths
                  </h3>
                  <ul className="space-y-2">
                    {feedback.strengths.map((strength, index) => (
                      <li key={index} className="text-slate-700 flex items-start">
                        <span className="text-green-500 mr-2 mt-1">•</span>
                        {strength}
                      </li>
                    ))}
                  </ul>
                </div>

                <div>
                  <h3 className="text-xl font-semibold text-slate-900 mb-4 flex items-center">
                    <span className="text-orange-500 mr-2">⚡</span>
                    Areas for Improvement
                  </h3>
                  <ul className="space-y-2">
                    {feedback.improvements.map((improvement, index) => (
                      <li key={index} className="text-slate-700 flex items-start">
                        <span className="text-orange-500 mr-2 mt-1">•</span>
                        {improvement}
                      </li>
                    ))}
                  </ul>
                </div>
              </div>

              <div className="mt-8 p-6 bg-white/20 border border-slate-300 rounded-lg">
                <h3 className="text-lg font-semibold text-slate-900 mb-2">
                  Overall Feedback
                </h3>
                <p className="text-slate-700">{feedback.overall}</p>
              </div>
            </div>

            <div className="text-center">
              <button
                onClick={handleStartDemo}
                className="px-8 py-4 text-slate-900 rounded-lg font-semibold transition-colors mr-4"
                style={{ backgroundColor: '#e4f223' }}
                onMouseEnter={(e) => e.currentTarget.style.backgroundColor = '#d4e213'}
                onMouseLeave={(e) => e.currentTarget.style.backgroundColor = '#e4f223'}
              >
                Try Again
              </button>
              <button
                onClick={() => window.location.href = '/'}
                className="px-8 py-4 bg-slate-900 text-white rounded-lg font-semibold hover:bg-slate-800 transition-colors"
              >
                Back to Home
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen relative">
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
      <div className="relative z-10 pt-32 pb-12">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h1 className="text-4xl font-bold text-slate-900 mb-4">
              AI Interview Demo
            </h1>
            <p className="text-xl text-slate-700">
              Question {currentQuestion + 1} of {questions.length}
            </p>
          </div>

          <div className="bg-white/10 backdrop-blur-md border border-white/20 rounded-2xl shadow-2xl p-8 mb-8">
            <div className="mb-6">
              <div className="flex justify-between items-center mb-4">
                <span 
                  className="px-3 py-1 rounded-full text-sm font-medium border"
                  style={{ 
                    backgroundColor: 'rgba(228, 242, 35, 0.2)', 
                    color: '#e4f223',
                    borderColor: 'rgba(228, 242, 35, 0.3)'
                  }}
                >
                  {questions[currentQuestion].category}
                </span>
                <span className="text-slate-600 text-sm">
                  {questions[currentQuestion].timeLimit}s time limit
                </span>
              </div>
              
              <h2 className="text-2xl font-semibold text-slate-900 mb-6">
                {questions[currentQuestion].question}
              </h2>
            </div>

            <div className="mb-6">
              <label className="block text-sm font-medium text-slate-700 mb-2">
                Your Answer
              </label>
              <textarea
                value={userAnswer}
                onChange={(e) => setUserAnswer(e.target.value)}
                placeholder="Type your answer here..."
                className="w-full h-32 px-4 py-3 bg-white/20 border border-slate-300 rounded-lg resize-none text-slate-900 placeholder-slate-500"
                style={{ 
                  '--tw-ring-color': '#e4f223',
                  '--tw-border-color': '#e4f223'
                }}
                onFocus={(e) => {
                  e.currentTarget.style.borderColor = '#e4f223';
                  e.currentTarget.style.boxShadow = '0 0 0 2px rgba(228, 242, 35, 0.2)';
                }}
                onBlur={(e) => {
                  e.currentTarget.style.borderColor = '#d1d5db';
                  e.currentTarget.style.boxShadow = 'none';
                }}
              />
            </div>

            <div className="flex justify-between items-center">
              <div className="text-sm text-slate-600">
                {userAnswer.length} characters
              </div>
              <button
                onClick={handleNextQuestion}
                disabled={!userAnswer.trim()}
                className="px-6 py-3 text-slate-900 rounded-lg font-semibold transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                style={{ backgroundColor: '#e4f223' }}
                onMouseEnter={(e) => !e.currentTarget.disabled && (e.currentTarget.style.backgroundColor = '#d4e213')}
                onMouseLeave={(e) => !e.currentTarget.disabled && (e.currentTarget.style.backgroundColor = '#e4f223')}
              >
                {currentQuestion < questions.length - 1 ? 'Next Question' : 'Finish Interview'}
              </button>
            </div>
          </div>

          <div className="text-center">
            <button
              onClick={() => window.location.href = '/'}
              className="text-slate-700 hover:text-slate-900 transition-colors"
            >
              ← Back to Home
            </button>
          </div>
        </div>
      </div>

      <Footer />
    </div>
  );
}
