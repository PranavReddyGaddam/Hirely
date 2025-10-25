import React, { useState } from 'react';
import Header from '../components/Header';
import { useAuth } from '../hooks/useAuth';

export default function ForgotPassword() {
  const [email, setEmail] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [sent, setSent] = useState(false);
  const { requestPasswordReset, error, clearError } = useAuth();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    const ok = await requestPasswordReset(email);
    if (ok) setSent(true);
    setIsSubmitting(false);
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
            <div className="bg-white/10 backdrop-blur-md rounded-3xl border-2 border-lime-500 p-8 shadow-lg shadow-lime-500/20">
              <div className="text-center mb-8">
                <h1 className="text-3xl font-bold text-black mb-2">Forgot Password</h1>
                <p className="text-black/80">Enter your email to receive a reset link</p>
              </div>

              {sent ? (
                <div className="mb-4 p-3 bg-green-100 border border-green-400 text-green-700 rounded-lg">
                  If an account exists for {email}, a reset link has been sent.
                </div>
              ) : null}

              {error && (
                <div className="mb-4 p-3 bg-red-100 border border-red-400 text-red-700 rounded-lg">
                  {error}
                </div>
              )}

              <form onSubmit={handleSubmit} className="space-y-6">
                <div>
                  <label htmlFor="email" className="block text-sm font-semibold text-black mb-2">
                    Email Address
                  </label>
                  <input
                    type="email"
                    id="email"
                    name="email"
                    value={email}
                    onChange={(e) => { setEmail(e.target.value); if (error) clearError(); }}
                    required
                    className="w-full px-4 py-3 bg-white/20 backdrop-blur-sm border border-white/30 rounded-xl text-black placeholder-black/60 focus:outline-none focus:ring-2 focus:ring-lime-500 focus:border-lime-500 transition-all duration-300"
                    placeholder="Enter your email"
                  />
                </div>

                <button
                  type="submit"
                  disabled={isSubmitting}
                  className="w-full bg-lime-500 hover:bg-lime-600 text-black font-bold py-3 px-4 rounded-xl transition-all duration-300 hover:scale-105 hover:shadow-lg hover:shadow-lime-500/30 focus:outline-none focus:ring-2 focus:ring-lime-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100"
                >
                  {isSubmitting ? 'Sending...' : 'Send reset link'}
                </button>
            </form>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
