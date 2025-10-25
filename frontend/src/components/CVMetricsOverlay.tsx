/**
 * CV Metrics Overlay Component
 * Displays real-time behavioral metrics on camera feed
 */

import type { CVMetrics } from '../services/CVTrackingService';

interface CVMetricsOverlayProps {
  metrics: CVMetrics | null;
  show: boolean;
}

export default function CVMetricsOverlay({ metrics, show }: CVMetricsOverlayProps) {
  if (!show) {
    return null;
  }

  // Show "Waiting for camera" if no metrics yet
  if (!metrics) {
    return (
      <div className="absolute top-4 right-4 bg-black/70 backdrop-blur-sm p-4 rounded-lg text-white text-sm font-mono space-y-2 min-w-[280px] shadow-xl border border-white/10">
        <div className="flex items-center gap-2 border-b border-white/20 pb-2 mb-2">
          <div className="w-2 h-2 bg-yellow-500 rounded-full animate-pulse"></div>
          <span className="font-semibold">Initializing CV...</span>
        </div>
        <div className="text-gray-400 text-xs">
          Waiting for camera feed...
        </div>
      </div>
    );
  }

  const getAttentionColor = (score: number): string => {
    if (score >= 0.7) return 'text-green-400';
    if (score >= 0.4) return 'text-yellow-400';
    return 'text-red-400';
  };

  const getStressColor = (level: string): string => {
    if (level === 'normal') return 'text-green-400';
    if (level === 'moderate_stress') return 'text-yellow-400';
    if (level === 'high_stress') return 'text-red-400';
    return 'text-gray-400';
  };

  const formatPosture = (status: string): string => {
    return status.split('_').map(word => 
      word.charAt(0).toUpperCase() + word.slice(1)
    ).join(' ');
  };

  return (
    <div className="absolute top-4 right-4 bg-black/70 backdrop-blur-sm p-4 rounded-lg text-white text-sm font-mono space-y-2 min-w-[280px] shadow-xl border border-white/10">
      {/* Header */}
      <div className="flex items-center gap-2 border-b border-white/20 pb-2 mb-2">
        <div className={`w-2 h-2 rounded-full animate-pulse ${metrics.face_detected === false ? 'bg-red-500' : 'bg-green-500'}`}></div>
        <span className="font-semibold">Live Analysis</span>
      </div>

      {/* Warning if no face detected */}
      {metrics.face_detected === false && (
        <div className="bg-red-500/20 border border-red-500/50 p-2 rounded text-xs text-red-300">
          ⚠️ No face detected! Please:<br/>
          • Look at the camera<br/>
          • Ensure good lighting<br/>
          • Move closer to camera
        </div>
      )}

      {/* Attention Score - Most Important */}
      <div className="bg-white/5 p-2 rounded">
        <div className="flex justify-between items-center">
          <span className="text-gray-300">Attention:</span>
          <span className={`font-bold text-lg ${getAttentionColor(metrics.attention_score)}`}>
            {(metrics.attention_score * 100).toFixed(0)}%
          </span>
        </div>
        <div className="w-full bg-gray-700 h-1.5 rounded-full mt-1">
          <div 
            className={`h-1.5 rounded-full transition-all ${
              metrics.attention_score >= 0.7 ? 'bg-green-400' :
              metrics.attention_score >= 0.4 ? 'bg-yellow-400' : 'bg-red-400'
            }`}
            style={{ width: `${metrics.attention_score * 100}%` }}
          ></div>
        </div>
      </div>

      {/* Expression */}
      <div className="flex justify-between">
        <span className="text-gray-300">Expression:</span>
        <span className="font-semibold text-blue-300">
          {formatPosture(metrics.expression)}
        </span>
      </div>

      {/* Eye Contact */}
      <div className="flex justify-between items-center">
        <span className="text-gray-300">Eye Contact:</span>
        <span className={metrics.is_looking_at_camera ? 'text-green-400' : 'text-orange-400'}>
          {metrics.is_looking_at_camera ? '✓ Good' : '○ Looking Away'}
        </span>
      </div>

      {/* Posture */}
      <div className="flex justify-between">
        <span className="text-gray-300">Posture:</span>
        <span className={metrics.is_slouching ? 'text-orange-400' : 'text-green-400'}>
          {formatPosture(metrics.posture_status)}
        </span>
      </div>

      {/* Stress Level */}
      <div className="flex justify-between">
        <span className="text-gray-300">Stress:</span>
        <span className={getStressColor(metrics.stress_level)}>
          {metrics.stress_level.replace('_', ' ')}
        </span>
      </div>

      {/* Engagement Status */}
      <div className="flex justify-between items-center">
        <span className="text-gray-300">Status:</span>
        <span className={
          metrics.is_engaged ? 'text-green-400' :
          metrics.is_distracted ? 'text-red-400' : 'text-gray-400'
        }>
          {metrics.is_engaged ? '✓ Engaged' :
           metrics.is_distracted ? '! Distracted' : '- Neutral'}
        </span>
      </div>

      {/* Warnings */}
      {(metrics.face_touching || metrics.hand_fidgeting || metrics.excessive_gesturing) && (
        <div className="border-t border-yellow-500/30 pt-2 mt-2 space-y-1">
          <div className="text-yellow-400 text-xs font-semibold">⚠ Suggestions:</div>
          {metrics.face_touching && (
            <div className="text-yellow-300 text-xs">• Avoid touching face</div>
          )}
          {metrics.hand_fidgeting && (
            <div className="text-yellow-300 text-xs">• Keep hands still</div>
          )}
          {metrics.excessive_gesturing && (
            <div className="text-yellow-300 text-xs">• Reduce hand movements</div>
          )}
        </div>
      )}
    </div>
  );
}
