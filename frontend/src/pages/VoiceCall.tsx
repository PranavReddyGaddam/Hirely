import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';

const VoiceCall: React.FC = () => {
  const navigate = useNavigate();
  const [phoneNumber, setPhoneNumber] = useState('');
  const [loading, setLoading] = useState(false);
  const [callId, setCallId] = useState<string | null>(null);
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  const handleCreateCall = async () => {
    if (!phoneNumber) {
      setMessage({ type: 'error', text: 'Please enter a phone number' });
      return;
    }

    setLoading(true);
    setMessage(null);

    try {
      const token = localStorage.getItem('hirely_token');
      if (!token) {
        setMessage({ type: 'error', text: 'Please login first' });
        return;
      }

      const response = await fetch('/api/v1/voice/create-call', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({ phone_number: phoneNumber }),
      });

      const data = await response.json();

      if (response.ok) {
        setCallId(data.call_id);
        setMessage({ type: 'success', text: `Call initiated! Call ID: ${data.call_id}` });
      } else {
        setMessage({ type: 'error', text: data.detail || 'Failed to create call' });
      }
    } catch (error) {
      setMessage({ type: 'error', text: 'Failed to create call' });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 py-12 px-4">
      <div className="max-w-2xl mx-auto">
        <div className="bg-white rounded-2xl shadow-2xl p-8">
          <div className="flex justify-between items-start mb-8">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 mb-2">🎤 Voice Call Test</h1>
              <p className="text-gray-600">Test your VAPI voice assistant with a phone call</p>
            </div>
            <button
              onClick={() => {
                if (window.confirm('Are you sure you want to end this interview? Your progress will be saved.')) {
                  navigate('/interview/setup');
                }
              }}
              className="px-4 py-2 bg-red-500 text-white text-sm font-medium rounded-lg hover:bg-red-600 transition-colors"
            >
              End Interview
            </button>
          </div>

          {/* Phone Number Input */}
          <div className="mb-6">
            <label htmlFor="phone" className="block text-sm font-medium text-gray-700 mb-2">
              Phone Number
            </label>
            <input
              type="tel"
              id="phone"
              value={phoneNumber}
              onChange={(e) => setPhoneNumber(e.target.value)}
              placeholder="+14155552671"
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
            <p className="mt-2 text-sm text-gray-500">
              Enter your phone number (e.g., +14155552671)
            </p>
          </div>

          {/* Call Button */}
          <button
            onClick={handleCreateCall}
            disabled={loading || !phoneNumber}
            className="w-full bg-blue-600 text-white py-3 px-6 rounded-lg font-semibold hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
          >
            {loading ? 'Creating Call...' : '📞 Create Call'}
          </button>

          {/* Message Display */}
          {message && (
            <div
              className={`mt-6 p-4 rounded-lg ${
                message.type === 'success'
                  ? 'bg-green-50 text-green-800 border border-green-200'
                  : 'bg-red-50 text-red-800 border border-red-200'
              }`}
            >
              {message.text}
            </div>
          )}

          {/* Call ID Display */}
          {callId && (
            <div className="mt-6 p-4 bg-blue-50 rounded-lg border border-blue-200">
              <p className="text-sm font-medium text-blue-800 mb-2">Call Information:</p>
              <p className="text-sm text-blue-600 font-mono">{callId}</p>
            </div>
          )}

          {/* Instructions */}
          <div className="mt-8 p-6 bg-gray-50 rounded-lg border border-gray-200">
            <h3 className="font-semibold text-gray-900 mb-3">📋 Instructions:</h3>
            <ol className="list-decimal list-inside space-y-2 text-sm text-gray-700">
              <li>Enter your phone number in the format shown above</li>
              <li>Click "Create Call" to initiate the call</li>
              <li>Answer your phone when it rings</li>
              <li>The AI assistant will conduct a brief interview</li>
              <li>Follow the assistant's prompts during the call</li>
            </ol>
          </div>
        </div>
      </div>
    </div>
  );
};

export default VoiceCall;
