import React from 'react';

// Type definitions
interface SkeletonTextProps {
  lines?: number;
  className?: string;
}

interface SkeletonImageProps {
  height?: string;
  className?: string;
}

interface SkeletonButtonProps {
  width?: string;
  height?: string;
  className?: string;
}

interface SkeletonAvatarProps {
  size?: string;
  className?: string;
}

interface ShimmerCardProps {
  children: React.ReactNode;
  className?: string;
}

interface PulseCardProps {
  children: React.ReactNode;
  className?: string;
}

interface WaveCardProps {
  children: React.ReactNode;
  className?: string;
}

interface LoadingSpinnerProps {
  size?: string;
  className?: string;
}

interface ProgressBarProps {
  progress: number;
  className?: string;
}

interface PageLoadingWrapperProps {
  children: React.ReactNode;
  isLoading: boolean;
  className?: string;
}

interface SmoothPageTransitionProps {
  children: React.ReactNode;
  className?: string;
}

// Reusable Skeleton Components
export const SkeletonCard = () => (
  <div className="bg-white rounded-xl p-6 border border-slate-200 shadow-sm">
    <div className="animate-pulse">
      <div className="h-4 bg-slate-200 rounded w-3/4 mb-4"></div>
      <div className="h-3 bg-slate-200 rounded w-1/2 mb-2"></div>
      <div className="h-3 bg-slate-200 rounded w-2/3"></div>
    </div>
  </div>
);

export const SkeletonText = ({ lines = 3, className = "" }: SkeletonTextProps) => (
  <div className={`animate-pulse space-y-3 ${className}`}>
    {Array.from({ length: lines }).map((_, i) => (
      <div 
        key={i}
        className={`h-4 bg-slate-200 rounded ${
          i === lines - 1 ? 'w-4/6' : i === 0 ? 'w-full' : 'w-5/6'
        }`}
      ></div>
    ))}
  </div>
);

export const SkeletonImage = ({ height = "h-48", className = "" }: SkeletonImageProps) => (
  <div className={`animate-pulse ${className}`}>
    <div className={`${height} bg-slate-200 rounded-xl`}></div>
  </div>
);

export const SkeletonButton = ({ width = "w-32", height = "h-12", className = "" }: SkeletonButtonProps) => (
  <div className={`animate-pulse ${className}`}>
    <div className={`${height} ${width} bg-slate-200 rounded-lg`}></div>
  </div>
);

export const SkeletonAvatar = ({ size = "h-12 w-12", className = "" }: SkeletonAvatarProps) => (
  <div className={`animate-pulse ${className}`}>
    <div className={`${size} bg-slate-200 rounded-full`}></div>
  </div>
);

// Shimmer Effect Component
export const ShimmerCard = ({ children, className = "" }: ShimmerCardProps) => (
  <div className={`relative overflow-hidden bg-white rounded-xl p-6 border border-slate-200 shadow-sm ${className}`}>
    <div className="absolute inset-0 -translate-x-full animate-[shimmer_2s_infinite] bg-gradient-to-r from-transparent via-slate-200 to-transparent"></div>
    <div className="relative">
      {children}
    </div>
  </div>
);

// Pulse Animation Component
export const PulseCard = ({ children, className = "" }: PulseCardProps) => (
  <div className={`bg-white rounded-xl p-6 border border-slate-200 shadow-sm animate-pulse ${className}`}>
    {children}
  </div>
);

// Wave Animation Component
export const WaveCard = ({ children, className = "" }: WaveCardProps) => (
  <div className={`relative overflow-hidden bg-white rounded-xl p-6 border border-slate-200 shadow-sm ${className}`}>
    <div className="absolute inset-0 bg-gradient-to-r from-transparent via-slate-100 to-transparent animate-[wave_3s_ease-in-out_infinite]"></div>
    <div className="relative">
      {children}
    </div>
  </div>
);

// Loading Spinner
export const LoadingSpinner = ({ size = "h-6 w-6", className = "" }: LoadingSpinnerProps) => (
  <div className={`animate-spin rounded-full border-2 border-slate-200 border-t-blue-500 ${size} ${className}`}></div>
);

// Progress Bar
export const ProgressBar = ({ progress, className = "" }: ProgressBarProps) => (
  <div className={`w-full bg-slate-200 rounded-full h-2 overflow-hidden ${className}`}>
    <div 
      className="h-full bg-gradient-to-r from-blue-500 to-blue-600 rounded-full transition-all duration-300 ease-out"
      style={{ width: `${progress}%` }}
    ></div>
  </div>
);

// Page Loading Wrapper
export const PageLoadingWrapper = ({ children, isLoading, className = "" }: PageLoadingWrapperProps) => {
  if (isLoading) {
    return (
      <div className={`min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 flex items-center justify-center p-4 ${className}`}>
        <div className="max-w-4xl w-full">
          {/* Header Skeleton */}
          <div className="text-center mb-12">
            <div className="animate-pulse">
              <div className="h-8 bg-slate-200 rounded w-64 mx-auto mb-4"></div>
              <div className="h-4 bg-slate-200 rounded w-96 mx-auto"></div>
            </div>
          </div>

          {/* Content Skeleton Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
            <SkeletonCard />
            <ShimmerCard>
              <div className="h-4 bg-slate-200 rounded w-3/4 mb-4"></div>
              <div className="h-3 bg-slate-200 rounded w-1/2 mb-2"></div>
              <div className="h-3 bg-slate-200 rounded w-2/3"></div>
            </ShimmerCard>
            <PulseCard>
              <div className="flex items-center space-x-3 mb-4">
                <div className="h-8 w-8 bg-slate-200 rounded-full"></div>
                <div className="h-4 bg-slate-200 rounded w-1/3"></div>
              </div>
              <div className="space-y-2">
                <div className="h-3 bg-slate-200 rounded w-full"></div>
                <div className="h-3 bg-slate-200 rounded w-4/5"></div>
                <div className="h-3 bg-slate-200 rounded w-3/5"></div>
              </div>
            </PulseCard>
          </div>

          {/* Loading Animation */}
          <div className="text-center mt-12">
            <div className="inline-flex items-center space-x-2 text-slate-600">
              <LoadingSpinner />
              <span>Loading...</span>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return <>{children}</>;
};

// Smooth Page Transition
export const SmoothPageTransition = ({ children, className = "" }: SmoothPageTransitionProps) => {
  const [isVisible, setIsVisible] = React.useState(false);

  React.useEffect(() => {
    const timer = setTimeout(() => setIsVisible(true), 100);
    return () => clearTimeout(timer);
  }, []);

  return (
    <div className={`transition-all duration-300 ${isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-4'} ${className}`}>
      {children}
    </div>
  );
};
