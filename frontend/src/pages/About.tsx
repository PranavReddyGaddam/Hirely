import Header from '../components/Header';
import Footer from '../components/Footer';
import { SmoothPageTransition } from '../components/SkeletonLoader';

export default function About() {


  return (
    <SmoothPageTransition>
      <div className="min-h-screen">
      {/* Hero Section with Mountains Background */}
      <div className="relative min-h-screen">
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
        <div className="relative z-10 pt-24 pb-8">
          <div className="w-full px-4 sm:px-6 lg:px-8">
            {/* Custom Bento Grid */}
            <div className="w-full">
              <div className="max-w-7xl mx-auto">
                <div className="grid grid-cols-4 grid-rows-3 gap-4 h-[80vh]">
                  {/* Card 1 - AI-Powered Analysis (Top-left) */}
                  <div className="col-span-1 row-span-1 bg-white/10 backdrop-blur-md rounded-2xl p-6 flex flex-col justify-between hover:scale-105 hover:shadow-lg transition-all duration-300" style={{ border: '2px solid #e4f223', boxShadow: '0 10px 25px rgba(228, 242, 35, 0.3)' }}>
                    <div className="flex items-center gap-2">
                      <span className="text-black text-sm font-semibold px-3 py-1 rounded-full" style={{ backgroundColor: '#e4f223' }}>01</span>
                    </div>
                    <div>
                      <h3 className="text-black text-lg font-semibold mb-1">AI-Powered Analysis</h3>
                      <h4 className="text-black text-xl font-bold mb-2">Real-time Insights</h4>
                      <p className="text-black text-sm">Advanced computer vision analyzes your interview performance with precision</p>
                    </div>
                  </div>

                  {/* Card 2 - Smart Dashboard (Top-middle) */}
                  <div className="col-span-1 row-span-1 bg-white/10 backdrop-blur-md rounded-2xl p-6 flex flex-col justify-between hover:scale-105 hover:shadow-lg transition-all duration-300" style={{ border: '2px solid #e4f223', boxShadow: '0 10px 25px rgba(228, 242, 35, 0.3)' }}>
                    <div className="flex items-center gap-2">
                      <span className="text-black text-sm font-semibold px-3 py-1 rounded-full" style={{ backgroundColor: '#e4f223' }}>02</span>
                    </div>
                    <div>
                      <h3 className="text-black text-lg font-semibold mb-1">Smart Dashboard</h3>
                      <h4 className="text-black text-xl font-bold mb-2">Progress Tracking</h4>
                      <p className="text-black text-sm">Visualize your improvement journey with detailed analytics and trends</p>
                    </div>
                  </div>

                  {/* Card 3 - Advanced AI Engine (Top-right, spans 2 cols, 2 rows) */}
                  <div className="col-span-2 row-span-2 bg-white/30 backdrop-blur-md rounded-2xl p-6 flex flex-col justify-between hover:scale-105 hover:shadow-lg transition-all duration-300" style={{ border: '2px solid #e4f223', boxShadow: '0 10px 25px rgba(228, 242, 35, 0.3)' }}>
                    <div className="flex items-center gap-2">
                      <span className="text-black text-sm font-semibold px-3 py-1 rounded-full" style={{ backgroundColor: '#e4f223' }}>03</span>
                    </div>
                    <div>
                      <h3 className="text-black text-2xl font-bold mb-2">Advanced AI Engine</h3>
                      <h4 className="text-black text-3xl font-bold mb-4">Next-Gen Technology</h4>
                      <p className="text-black text-base leading-relaxed">Revolutionary machine learning algorithms that understand context, emotion, and communication patterns to provide unprecedented interview insights</p>
                    </div>
                  </div>

                  {/* Card 4 - Real-time Feedback (Middle-left, spans 1 col, 2 rows) */}
                  <div className="col-span-1 row-span-2 bg-white/10 backdrop-blur-md rounded-2xl p-6 flex flex-col justify-between hover:scale-105 hover:shadow-lg transition-all duration-300" style={{ border: '2px solid #e4f223', boxShadow: '0 10px 25px rgba(228, 242, 35, 0.3)' }}>
                    <div className="flex items-center gap-2">
                      <span className="text-black text-sm font-semibold px-3 py-1 rounded-full" style={{ backgroundColor: '#e4f223' }}>04</span>
                    </div>
                    <div>
                      <h3 className="text-black text-xl font-bold mb-2">Real-time Feedback</h3>
                      <h4 className="text-black text-2xl font-bold mb-4">Instant Analysis</h4>
                      <p className="text-black text-sm leading-relaxed">Get immediate, actionable feedback on your speaking pace, body language, and confidence levels as you practice</p>
                    </div>
                  </div>

                  {/* Card 5 - Smart Analytics (Middle-right) */}
                  <div className="col-span-1 row-span-1 bg-white/10 backdrop-blur-md rounded-2xl p-6 flex flex-col justify-between hover:scale-105 hover:shadow-lg transition-all duration-300" style={{ border: '2px solid #e4f223', boxShadow: '0 10px 25px rgba(228, 242, 35, 0.3)' }}>
                    <div className="flex items-center gap-2">
                      <span className="text-black text-sm font-semibold px-3 py-1 rounded-full" style={{ backgroundColor: '#e4f223' }}>05</span>
                    </div>
                    <div>
                      <h3 className="text-black text-lg font-semibold mb-1">Smart Analytics</h3>
                      <h4 className="text-black text-xl font-bold mb-2">Deep Insights</h4>
                      <p className="text-black text-sm">Comprehensive performance metrics and improvement recommendations</p>
                    </div>
                  </div>

                  {/* Card 6 - Filler Word Detection (Bottom-middle) */}
                  <div className="col-span-1 row-span-1 bg-white/10 backdrop-blur-md rounded-2xl p-6 flex flex-col justify-between hover:scale-105 hover:shadow-lg transition-all duration-300" style={{ border: '2px solid #e4f223', boxShadow: '0 10px 25px rgba(228, 242, 35, 0.3)' }}>
                    <div className="flex items-center gap-2">
                      <span className="text-black text-sm font-semibold px-3 py-1 rounded-full" style={{ backgroundColor: '#e4f223' }}>06</span>
                    </div>
                    <div>
                      <h3 className="text-black text-lg font-semibold mb-1">Filler Word Detection</h3>
                      <h4 className="text-black text-xl font-bold mb-2">Speech Analysis</h4>
                      <p className="text-black text-sm">Identify and eliminate "um", "uh", "like" with precise timestamps</p>
                    </div>
                  </div>

                  {/* Card 7 - Complete Interview Suite (Bottom-right, spans 2 columns) */}
                  <div className="col-span-2 row-span-1 bg-white/10 backdrop-blur-md rounded-2xl p-6 flex flex-col justify-between hover:scale-105 hover:shadow-lg transition-all duration-300" style={{ border: '2px solid #e4f223', boxShadow: '0 10px 25px rgba(228, 242, 35, 0.3)' }}>
                    <div className="flex items-center gap-2">
                      <span className="text-black text-sm font-semibold px-3 py-1 rounded-full" style={{ backgroundColor: '#e4f223' }}>07</span>
                    </div>
                    <div>
                      <h3 className="text-black text-xl font-bold mb-1">Complete Interview Suite</h3>
                      <h4 className="text-black text-2xl font-bold mb-2">All-in-One Platform</h4>
                      <p className="text-black text-sm">Record, analyze, improve, and track your interview skills with our comprehensive AI-powered platform</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>


      <Footer />
    </div>
    </SmoothPageTransition>
  );
}
