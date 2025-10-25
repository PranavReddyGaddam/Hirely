import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useAuthContext } from '../contexts/AuthContext';

interface InterviewReportProps {}

const InterviewReport: React.FC<InterviewReportProps> = () => {
  const { interviewId } = useParams<{ interviewId: string }>();
  const navigate = useNavigate();
  const { user } = useAuthContext();
  const [loading, setLoading] = useState(true);
  const [reportData, setReportData] = useState<any>(null);

  useEffect(() => {
    // TODO: Fetch interview report data from backend
    // For now, just show a placeholder
    setLoading(false);
  }, [interviewId]);

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading interview report...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-4xl mx-auto px-4 py-8">
        <div className="bg-white rounded-lg shadow-lg p-8">
          <div className="text-center mb-8">
            <h1 className="text-3xl font-bold text-gray-900 mb-2">
              Interview Report
            </h1>
            <p className="text-gray-600">
              Interview ID: {interviewId}
            </p>
          </div>

          <div className="space-y-6">
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
              <h2 className="text-xl font-semibold text-blue-900 mb-4">
                🎉 Interview Completed Successfully!
              </h2>
              <p className="text-blue-800">
                Congratulations! You have successfully completed your interview. 
                Your responses have been recorded and will be analyzed for feedback.
              </p>
            </div>

            <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6">
              <h3 className="text-lg font-semibold text-yellow-900 mb-2">
                📊 Analysis Coming Soon
              </h3>
              <p className="text-yellow-800">
                Your interview analysis and detailed feedback will be available shortly. 
                This will include performance insights, strengths, and areas for improvement.
              </p>
            </div>

            <div className="flex justify-center space-x-4">
              <button
                onClick={() => navigate('/interview/setup')}
                className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition-colors"
              >
                Start New Interview
              </button>
              <button
                onClick={() => navigate('/')}
                className="bg-gray-600 text-white px-6 py-3 rounded-lg hover:bg-gray-700 transition-colors"
              >
                Back to Home
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default InterviewReport;
