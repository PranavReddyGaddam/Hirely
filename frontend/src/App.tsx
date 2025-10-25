import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Header from "./components/Header";
import Footer from "./components/Footer";
import Demo from "./pages/Demo";
import About from "./pages/About"; // About page for video analysis showcase
import Login from "./pages/Login";
import ForgotPassword from "./pages/ForgotPassword";
import Signup from "./pages/Signup";
import InterviewSetup from "./pages/InterviewSetup";
import InterviewSession from "./pages/InterviewSession";
import InterviewReport from "./components/InterviewReport";
import Profile from "./pages/Profile";
import VoiceCall from "./pages/VoiceCall";
import { useAuth } from "./hooks/useAuth";
import { AuthProvider } from "./contexts/AuthContext";
import { NotificationProvider } from "./contexts/NotificationContext";

// ProtectedRoute component
function ProtectedRoute({ children }: { children: React.ReactElement }) {
  const { isAuthenticated, isLoading } = useAuth();

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-lg font-semibold">Loading...</div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return children;
}

function HomePage() {
  const { isAuthenticated } = useAuth();
  
  const companies = [
    { name: "Google", logo: "Google-logo.png" },
    { name: "Apple", logo: "Apple-logo.png" },
    { name: "Microsoft", logo: "Microsoft-logo.png" },
    { name: "Meta", logo: "meta-logo.png" },
    { name: "NVIDIA", logo: "nvidia-logo.png" },
    { name: "Salesforce", logo: "Salesforce-logo.png" },
    { name: "Adobe", logo: "Adobe-logo.png" },
    { name: "OpenAI", logo: "openai-logo.png" },
    { name: "Anthropic", logo: "anthropic-logo.png" },
    { name: "Amazon", logo: "Amazon-logo.png" },
  ];

  return (
    <div className="min-h-screen">
      {/* Header Navigation */}
      <Header />

      {/* Hero Section with Blue Gradient Background */}
      <div className="relative min-h-screen flex flex-col justify-between overflow-hidden">
        {/* Background Image */}
        <div
          className="absolute inset-0 z-0"
          style={{
            backgroundImage: "url(/Blue_Gradient.webp)",
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

        {/* Content Container */}
        <div className="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 w-full flex-grow flex items-center">
          <div className="grid lg:grid-cols-2 gap-12 items-center w-full">
            {/* Left Content */}
            <div className="pt-20 pb-12 lg:pb-0">
              {/* Main Heading */}
              <h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold text-white mb-6 tracking-normal">
                Own the Interview,
                <br />
                Every Time
              </h1>

              {/* Subtitle */}
              <p className="text-lg sm:text-xl text-white/80 mb-8 max-w-xl">
                Practice real interview scenarios, get instant feedback.
                <br />
                Track your progress as you improve every day.
              </p>

              {/* CTA Buttons */}
              <div className="flex flex-col sm:flex-row gap-4 mb-6">
                <a 
                  href={isAuthenticated ? "/interview/setup" : "/login"}
                  className="px-8 py-4 text-slate-900 rounded-lg font-semibold transition-all shadow-lg hover:shadow-xl transform hover:-translate-y-0.5 text-center"
                  style={{ backgroundColor: '#e4f223' }}
                  onMouseEnter={(e) => e.currentTarget.style.backgroundColor = '#d4e213'}
                  onMouseLeave={(e) => e.currentTarget.style.backgroundColor = '#e4f223'}
                >
                  Try Hirely
                </a>
                <a 
                  href="/about"
                  className="px-8 py-4 bg-white/10 backdrop-blur-sm text-white border-2 border-white/30 rounded-lg font-semibold hover:bg-white/20 transition-all text-center"
                >
                  How it works
                </a>
              </div>
            </div>

            {/* Right Content - Video Demo */}
            <div className="hidden lg:block relative h-[600px]">
              <div className="absolute inset-0 flex items-center justify-center">
                {/* Video Demo - Clean Video Only */}
                <div className="relative w-[600px] h-[400px]">
                  <video
                    className="w-full h-full object-contain rounded-2xl"
                    autoPlay
                    loop
                    muted
                    playsInline
                  >
                    <source src="/Interview Clip 2.mp4" type="video/mp4" />
                    Your browser does not support the video tag.
                  </video>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Social Proof Section - At Bottom of Viewport */}
        <div className="relative z-10 pb-8 w-full">
          <div className="w-full">
            <p className="text-center text-slate-700 mb-4 text-sm font-medium px-4">
              Practice for roles at top companies — from startups to tech giants.
            </p>

            {/* Scrolling Logo Carousel - Truly Infinite */}
            <div className="relative overflow-hidden w-full">
              <div className="flex animate-scroll items-center will-change-transform">
                {/* First set - visible initially */}
                {companies.map((company, i) => (
                  <div
                    key={`set-1-${i}`}
                    className="flex-shrink-0 w-32 h-12 mx-4 flex items-center justify-center"
                  >
                    <img
                      src={`/logos/${company.logo}`}
                      alt={company.name}
                      className="h-8 w-auto object-contain grayscale opacity-40 hover:grayscale-0 hover:opacity-100 transition-all duration-300"
                      onError={(e) => {
                        // Fallback to text if image doesn't load
                        e.currentTarget.style.display = "none";
                        if (e.currentTarget.nextSibling) {
                          (
                            e.currentTarget.nextSibling as HTMLElement
                          ).style.display = "block";
                        }
                      }}
                    />
                    <span className="text-slate-400 font-semibold text-sm hidden">
                      {company.name}
                    </span>
                  </div>
                ))}
                {/* Second set - creates seamless loop */}
                {companies.map((company, i) => (
                  <div
                    key={`set-2-${i}`}
                    className="flex-shrink-0 w-32 h-12 mx-4 flex items-center justify-center"
                  >
                    <img
                      src={`/logos/${company.logo}`}
                      alt={company.name}
                      className="h-8 w-auto object-contain grayscale opacity-40 hover:grayscale-0 hover:opacity-100 transition-all duration-300"
                      onError={(e) => {
                        // Fallback to text if image doesn't load
                        e.currentTarget.style.display = "none";
                        if (e.currentTarget.nextSibling) {
                          (
                            e.currentTarget.nextSibling as HTMLElement
                          ).style.display = "block";
                        }
                      }}
                    />
                    <span className="text-slate-400 font-semibold text-sm hidden">
                      {company.name}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Timeline Section - Promise & Progression */}
      <div className="bg-white py-24">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
          {/* Header */}
          <div className="text-center mb-16">
            <p className="text-slate-500 text-sm font-medium mb-4">
              AI interview prep shouldn't take months to master.
            </p>
            <h2 className="text-4xl sm:text-5xl font-bold text-slate-900 mb-6">
              Here's what you can achieve with Hirely in just 30 days.
            </h2>
            <a 
              href="/demo" 
              className="inline-flex items-center text-slate-900 font-semibold hover:text-slate-700 transition-all duration-300 underline hover:-translate-y-1"
            >
              Start practicing today →
            </a>
          </div>

          {/* Timeline */}
          <div className="relative">
            {/* Timeline Labels - Above the line */}
            <div className="flex justify-between items-center mb-4">
              <span className="text-sm font-medium text-slate-500 bg-slate-100 px-3 py-1 rounded-full">
                Today
              </span>
              <span className="text-sm font-medium text-slate-500 bg-slate-100 px-3 py-1 rounded-full">
                Day 5
              </span>
              <span className="text-sm font-medium text-slate-500 bg-slate-100 px-3 py-1 rounded-full">
                Day 30
              </span>
            </div>
            
            {/* Timeline Bar */}
            <div className="relative h-0.5 bg-slate-200 mb-16">
              {/* Timeline Markers */}
              <div className="absolute top-0 left-0 w-4 h-4 bg-slate-200 rounded-full -translate-y-1.5"></div>
              <div className="absolute top-0 left-1/2 w-4 h-4 bg-slate-200 rounded-full -translate-x-2 -translate-y-1.5"></div>
              <div className="absolute top-0 right-0 w-4 h-4 bg-slate-900 rounded-full -translate-y-1.5"></div>
            </div>

            {/* Content Cards */}
            <div className="grid md:grid-cols-3 gap-8">
              {/* Card 1 - Today */}
              <div className="bg-white border border-slate-200 rounded-lg p-8 shadow-sm hover:shadow-md transition-shadow">
                <h3 className="text-base font-bold text-slate-900 mb-6">Get started.</h3>
                <ul className="space-y-3">
                  <li className="flex items-start">
                    <span className="text-slate-900 font-bold mr-3">✓</span>
                    <span className="text-slate-600 text-sm">Complete first AI interview in 5 minutes</span>
                  </li>
                  <li className="flex items-start">
                    <span className="text-slate-900 font-bold mr-3">✓</span>
                    <span className="text-slate-600 text-sm">Get instant feedback on answers</span>
                  </li>
                  <li className="flex items-start">
                    <span className="text-slate-900 font-bold mr-3">✓</span>
                    <span className="text-slate-600 text-sm">Set up practice schedule in 1 minute</span>
                  </li>
                </ul>
              </div>

              {/* Card 2 - Day 5 */}
              <div className="bg-white border border-slate-200 rounded-lg p-8 shadow-sm hover:shadow-md transition-shadow">
                <h3 className="text-base font-bold text-slate-900 mb-6">Get comfortable.</h3>
                <ul className="space-y-3">
                  <li className="flex items-start">
                    <span className="text-slate-900 font-bold mr-3">✓</span>
                    <span className="text-slate-600 text-sm">Master 50+ interview questions</span>
                  </li>
                  <li className="flex items-start">
                    <span className="text-slate-900 font-bold mr-3">✓</span>
                    <span className="text-slate-600 text-sm">Improve confidence and delivery</span>
                  </li>
                  <li className="flex items-start">
                    <span className="text-slate-900 font-bold mr-3">✓</span>
                    <span className="text-slate-600 text-sm">Track progress with detailed analytics</span>
                  </li>
                </ul>
              </div>

              {/* Card 3 - Day 30 */}
              <div className="bg-white border border-slate-200 rounded-lg p-8 shadow-sm hover:shadow-md transition-shadow">
                <h3 className="text-base font-bold text-slate-900 mb-6">Ask why you didn't start sooner.</h3>
                <ul className="space-y-3">
                  <li className="flex items-start">
                    <span className="text-slate-900 font-bold mr-3">✓</span>
                    <span className="text-slate-600 text-sm">100% confidence boost</span>
                  </li>
                  <li className="flex items-start">
                    <span className="text-slate-900 font-bold mr-3">✓</span>
                    <span className="text-slate-600 text-sm">Interview skills 5x more polished</span>
                  </li>
                  <li className="flex items-start">
                    <span className="text-slate-900 font-bold mr-3">✓</span>
                    <span className="text-slate-600 text-sm">Land offers 3x faster</span>
                  </li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      </div>

      <Footer />
    </div>
  );
}

function App() {
  return (
    <AuthProvider>
      <NotificationProvider>
        <Router>
          <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/demo" element={<Demo />} />
          <Route path="/about" element={<About />} />
          <Route path="/login" element={<Login />} />
          <Route path="/forgot-password" element={<ForgotPassword />} />
          <Route path="/signup" element={<Signup />} />
          <Route 
            path="/interview/setup" 
            element={
              <ProtectedRoute>
                <InterviewSetup />
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/interview/:interviewId" 
            element={
              <ProtectedRoute>
                <InterviewSession />
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/interview/:interviewId/report" 
            element={
              <ProtectedRoute>
                <InterviewReport />
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/profile" 
            element={
              <ProtectedRoute>
                <Profile />
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/voice-call" 
            element={
              <ProtectedRoute>
                <VoiceCall />
              </ProtectedRoute>
            } 
          />
        </Routes>
        </Router>
      </NotificationProvider>
    </AuthProvider>
  );
}

export default App;
