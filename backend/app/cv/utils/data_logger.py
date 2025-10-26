"""
Data logging and export functionality
"""

import json
import csv
import pandas as pd
from datetime import datetime
from typing import Dict, List, Any
from pathlib import Path
import numpy as np


class DataLogger:
    """Handles real-time data collection and export"""
    
    def __init__(self, buffer_size: int = 36000):
        self.buffer_size = buffer_size
        self.data_buffer: List[Dict[str, Any]] = []
        self.session_start_time = None
        self.session_id = None
        self.frame_count = 0
        
    def start_session(self):
        """Initialize new logging session"""
        self.session_start_time = datetime.now()
        self.session_id = self.session_start_time.strftime("%Y%m%d_%H%M%S")
        self.data_buffer = []
        self.frame_count = 0
        print(f"[DataLogger] Session started: {self.session_id}")
        
    def log_frame_data(self, data: Dict[str, Any]):
        """Log data for current frame"""
        self.frame_count += 1
        
        # Add timestamp and frame number
        data['timestamp'] = datetime.now().isoformat()
        data['frame_number'] = self.frame_count
        data['elapsed_seconds'] = (datetime.now() - self.session_start_time).total_seconds()
        
        # Add to buffer
        self.data_buffer.append(data)
        
        # Prevent buffer overflow
        if len(self.data_buffer) > self.buffer_size:
            self.data_buffer.pop(0)
    
    def get_current_stats(self) -> Dict[str, Any]:
        """Get current session statistics"""
        if not self.data_buffer:
            return {}
        
        df = pd.DataFrame(self.data_buffer)
        
        stats = {
            'total_frames': len(self.data_buffer),
            'duration_seconds': df['elapsed_seconds'].max() if 'elapsed_seconds' in df else 0,
        }
        
        # Expression statistics
        if 'expression' in df:
            expression_counts = df['expression'].value_counts()
            total = len(df)
            stats['expressions'] = {
                expr: {
                    'count': int(count),
                    'percentage': round((count / total) * 100, 2)
                }
                for expr, count in expression_counts.items()
            }
        
        # Posture statistics
        if 'posture_status' in df:
            posture_counts = df['posture_status'].value_counts()
            total = len(df)
            stats['postures'] = {
                posture: {
                    'count': int(count),
                    'percentage': round((count / total) * 100, 2)
                }
                for posture, count in posture_counts.items()
            }
        
        # Attention statistics
        if 'attention_score' in df:
            stats['avg_attention_score'] = round(df['attention_score'].mean(), 2)
            stats['attention_below_50_percent'] = round(
                (df['attention_score'] < 0.5).sum() / total * 100, 2
            )
        
        # Alert statistics
        alert_columns = [col for col in df.columns if 'alert' in col.lower()]
        if alert_columns:
            try:
                alert_sum = df[alert_columns].sum().sum()
                stats['total_alerts'] = int(alert_sum) if pd.notna(alert_sum) else 0
            except:
                stats['total_alerts'] = 0
        else:
            stats['total_alerts'] = 0
        
        return stats
    
    def export_to_csv(self, output_dir: str = "exports") -> str:
        """Export data to CSV file"""
        if not self.data_buffer:
            print("[DataLogger] No data to export")
            return ""
        
        # Create exports directory
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        # Generate filename
        filename = f"{output_dir}/session_{self.session_id}.csv"
        
        # Convert to DataFrame and save
        df = pd.DataFrame(self.data_buffer)
        df.to_csv(filename, index=False)
        
        print(f"[DataLogger] Data exported to CSV: {filename}")
        return filename
    
    def export_to_json(self, output_dir: str = "exports") -> str:
        """Export data to JSON file"""
        if not self.data_buffer:
            print("[DataLogger] No data to export")
            return ""
        
        # Create exports directory
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        # Generate filename
        filename = f"{output_dir}/session_{self.session_id}.json"
        
        # Prepare data structure
        export_data = {
            'session_id': self.session_id,
            'session_start': self.session_start_time.isoformat(),
            'total_frames': len(self.data_buffer),
            'statistics': self.get_current_stats(),
            'data': self.data_buffer
        }
        
        # Save to JSON
        with open(filename, 'w') as f:
            json.dump(export_data, f, indent=2, default=str)
        
        print(f"[DataLogger] Data exported to JSON: {filename}")
        return filename
    
    def export_summary_report(self, output_dir: str = "exports") -> str:
        """Export human-readable summary report"""
        if not self.data_buffer:
            print("[DataLogger] No data to export")
            return ""
        
        # Create exports directory
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        # Generate filename
        filename = f"{output_dir}/summary_{self.session_id}.txt"
        
        # Get statistics
        stats = self.get_current_stats()
        
        # Create report
        report_lines = []
        report_lines.append("=" * 60)
        report_lines.append("INTERVIEW EXPRESSION & POSTURE ANALYSIS REPORT")
        report_lines.append("=" * 60)
        report_lines.append(f"\nSession ID: {self.session_id}")
        report_lines.append(f"Session Start: {self.session_start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        report_lines.append(f"Duration: {stats.get('duration_seconds', 0):.1f} seconds")
        report_lines.append(f"Total Frames Analyzed: {stats.get('total_frames', 0)}")
        
        # Expression breakdown
        if 'expressions' in stats:
            report_lines.append("\n" + "-" * 60)
            report_lines.append("FACIAL EXPRESSIONS")
            report_lines.append("-" * 60)
            for expr, data in sorted(stats['expressions'].items(), 
                                   key=lambda x: x[1]['percentage'], 
                                   reverse=True):
                report_lines.append(f"  {expr.upper():20s}: {data['percentage']:6.2f}% ({data['count']} frames)")
        
        # Posture breakdown
        if 'postures' in stats:
            report_lines.append("\n" + "-" * 60)
            report_lines.append("BODY POSTURES")
            report_lines.append("-" * 60)
            for posture, data in sorted(stats['postures'].items(), 
                                      key=lambda x: x[1]['percentage'], 
                                      reverse=True):
                report_lines.append(f"  {posture.upper():20s}: {data['percentage']:6.2f}% ({data['count']} frames)")
        
        # Attention metrics
        report_lines.append("\n" + "-" * 60)
        report_lines.append("ATTENTION METRICS")
        report_lines.append("-" * 60)
        report_lines.append(f"  Average Attention Score: {stats.get('avg_attention_score', 0):.2f}")
        report_lines.append(f"  Low Attention (<50%): {stats.get('attention_below_50_percent', 0):.2f}%")
        
        # Alerts
        if 'total_alerts' in stats:
            report_lines.append("\n" + "-" * 60)
            report_lines.append("ALERTS")
            report_lines.append("-" * 60)
            report_lines.append(f"  Total Alerts Triggered: {stats['total_alerts']}")
        
        # Overall assessment
        report_lines.append("\n" + "=" * 60)
        report_lines.append("OVERALL ASSESSMENT")
        report_lines.append("=" * 60)
        
        avg_attention = stats.get('avg_attention_score', 0)
        if avg_attention >= 0.8:
            assessment = "EXCELLENT - Maintained high engagement and professional demeanor"
        elif avg_attention >= 0.6:
            assessment = "GOOD - Generally attentive with room for improvement"
        elif avg_attention >= 0.4:
            assessment = "FAIR - Noticeable attention lapses, consider posture and focus"
        else:
            assessment = "NEEDS IMPROVEMENT - Significant issues with attention and posture"
        
        report_lines.append(f"\n{assessment}\n")
        report_lines.append("=" * 60)
        
        # Write to file
        with open(filename, 'w') as f:
            f.write('\n'.join(report_lines))
        
        print(f"[DataLogger] Summary report exported: {filename}")
        return filename
    
    def export_interview_analysis(self, output_dir: str = "exports") -> str:
        """Export clean interview analysis JSON with actionable metrics"""
        if not self.data_buffer:
            print("[DataLogger] No data to export")
            return None
        
        # Calculate aggregate metrics
        df = pd.DataFrame(self.data_buffer)
        
        # EMOTIONS - Expression distribution and consistency
        emotion_counts = df['expression'].value_counts().to_dict()
        total_frames = len(df)
        
        emotions = {
            "expression_distribution": {
                "calm": emotion_counts.get('calm', 0) / total_frames * 100,
                "genuine_smile": emotion_counts.get('genuine_smile', 0) / total_frames * 100,
                "tense": emotion_counts.get('tense', 0) / total_frames * 100,
                "frowning": emotion_counts.get('frowning', 0) / total_frames * 100,
                "surprised": emotion_counts.get('surprised', 0) / total_frames * 100,
                "sad": emotion_counts.get('sad', 0) / total_frames * 100
            },
            "dominant_emotion": df['expression'].mode()[0] if len(df) > 0 else 'calm',
            "emotional_stability": {
                "avg_confidence": float(df['expression_confidence'].mean()),
                "confidence_consistency": float(df['expression_confidence'].std()),
                "score": "stable" if df['expression_confidence'].std() < 0.15 else "unstable"
            },
            "smile_analysis": {
                "avg_smile_intensity": float(df['smile_intensity'].mean()),
                "genuine_smile_percentage": emotion_counts.get('genuine_smile', 0) / total_frames * 100,
                "recommendation": "increase_positive_expressions" if emotion_counts.get('genuine_smile', 0) / total_frames < 0.3 else "maintain"
            }
        }
        
        # FACIAL METRICS - Eye contact and blink patterns
        facial_metrics = {
            "eye_contact": {
                "avg_eye_openness_left": float(df['ear_left'].mean()),
                "avg_eye_openness_right": float(df['ear_right'].mean()),
                "avg_eye_openness_both": float(df['ear_avg'].mean()),
                "symmetry": "balanced" if abs(df['ear_left'].mean() - df['ear_right'].mean()) < 0.05 else "unbalanced"
            },
            "blink_pattern": {
                "total_blinks": int(df['blink_count'].max()),
                "avg_blink_rate_per_minute": float(df['blink_rate'].mean()),
                "normal_range": "15-20 bpm",
                "status": self._classify_blink_rate(df['blink_rate'].mean())
            },
            "mouth_activity": {
                "avg_mouth_openness": float(df['mar'].mean()),
                "talking_indicator": "active" if df['mar'].mean() > 0.15 else "minimal"
            }
        }
        
        # HEAD POSE - Gaze direction and engagement (with safety checks)
        head_pose = {
            "gaze_direction": {
                "avg_yaw_degrees": float(df['head_yaw'].mean()) if 'head_yaw' in df.columns else 0.0,
                "avg_pitch_degrees": float(df['head_pitch'].mean()) if 'head_pitch' in df.columns else 0.0,
                "avg_roll_degrees": float(df['head_roll'].mean()) if 'head_roll' in df.columns else 0.0,
                "direction_distribution": df['head_direction'].value_counts().to_dict() if 'head_direction' in df.columns else {'center': total_frames}
            },
            "camera_focus": {
                "looking_at_camera_percentage": float(df['is_looking_at_camera'].sum() / total_frames * 100) if 'is_looking_at_camera' in df.columns else 50.0,
                "avg_deviation_from_center": float(np.sqrt(df['head_yaw']**2 + df['head_pitch']**2).mean()) if 'head_yaw' in df.columns and 'head_pitch' in df.columns else 0.0,
                "recommendation": "improve_eye_contact" if 'is_looking_at_camera' in df.columns and df['is_looking_at_camera'].sum() / total_frames < 0.7 else "maintain"
            },
            "head_stability": {
                "yaw_variability": float(df['head_yaw'].std()) if 'head_yaw' in df.columns else 0.0,
                "pitch_variability": float(df['head_pitch'].std()) if 'head_pitch' in df.columns else 0.0,
                "score": "stable" if 'head_yaw' in df.columns and df['head_yaw'].std() < 10 else "unknown"
            }
        }
        
        # POSTURES - Body language and positioning
        posture_counts = df['posture_status'].value_counts().to_dict()
        postures = {
            "posture_distribution": {
                "upright_relaxed": posture_counts.get('upright_relaxed', 0) / total_frames * 100,
                "engaged_forward_lean": posture_counts.get('engaged_forward_lean', 0) / total_frames * 100,
                "slouching": posture_counts.get('slouching', 0) / total_frames * 100,
                "leaning_back": posture_counts.get('leaning_back', 0) / total_frames * 100,
                "facing_away": posture_counts.get('facing_away', 0) / total_frames * 100,
                "poor_alignment": posture_counts.get('poor_alignment', 0) / total_frames * 100
            },
            "dominant_posture": df['posture_status'].mode()[0] if len(df) > 0 else 'upright_relaxed',
            "body_angles": {
                "avg_neck_angle_degrees": float(df['neck_angle'].mean()),
                "avg_torso_angle_degrees": float(df['torso_angle'].mean()),
                "ideal_neck_range": "10-30 degrees",
                "ideal_torso_range": "5-20 degrees"
            },
            "posture_quality": {
                "good_posture_percentage": float(posture_counts.get('upright_relaxed', 0) + posture_counts.get('engaged_forward_lean', 0)) / total_frames * 100,
                "needs_improvement": posture_counts.get('slouching', 0) / total_frames > 0.3,
                "recommendation": "improve_posture" if (posture_counts.get('slouching', 0) + posture_counts.get('leaning_back', 0)) / total_frames > 0.3 else "maintain"
            }
        }
        
        # GESTURES - Hand movements and nervous behaviors
        gestures = {
            "face_touching": {
                "total_occurrences": int(df['face_touch_count'].max()),
                "percentage_of_time": float(df['face_touching'].sum() / total_frames * 100),
                "status": "problematic" if df['face_touching'].sum() / total_frames > 0.1 else "acceptable",
                "recommendation": "reduce_face_touching" if df['face_touching'].sum() / total_frames > 0.1 else "maintain"
            },
            "hand_fidgeting": {
                "percentage_of_time": float(df['hand_fidgeting'].sum() / total_frames * 100),
                "status": "problematic" if df['hand_fidgeting'].sum() / total_frames > 0.2 else "acceptable",
                "recommendation": "reduce_fidgeting" if df['hand_fidgeting'].sum() / total_frames > 0.2 else "maintain"
            },
            "excessive_gesturing": {
                "percentage_of_time": float(df['excessive_gesturing'].sum() / total_frames * 100),
                "status": "problematic" if df['excessive_gesturing'].sum() / total_frames > 0.15 else "acceptable"
            },
            "overall_gesture_quality": {
                "controlled_percentage": float((1 - (df['face_touching'].sum() + df['hand_fidgeting'].sum() + df['excessive_gesturing'].sum()) / (3 * total_frames)) * 100),
                "score": "good" if (df['face_touching'].sum() + df['hand_fidgeting'].sum()) / (2 * total_frames) < 0.15 else "needs_improvement"
            }
        }
        
        # STRESS - Physiological and behavioral indicators
        stress_distribution = df['stress_level'].value_counts().to_dict()
        stress = {
            "stress_distribution": {
                "normal": stress_distribution.get('normal', 0) / total_frames * 100,
                "moderate_stress": stress_distribution.get('moderate_stress', 0) / total_frames * 100,
                "high_stress": stress_distribution.get('high_stress', 0) / total_frames * 100,
                "drowsy": stress_distribution.get('drowsy', 0) / total_frames * 100
            },
            "dominant_stress_level": df['stress_level'].mode()[0] if len(df) > 0 else 'normal',
            "stress_indicators": {
                "avg_blink_rate": float(df['blink_rate'].mean()),
                "rapid_blinking_percentage": float((df['blink_rate'] > 30).sum() / total_frames * 100),
                "fidgeting_percentage": float(df['hand_fidgeting'].sum() / total_frames * 100)
            },
            "stress_management": {
                "calm_percentage": float(stress_distribution.get('normal', 0) / total_frames * 100),
                "needs_relaxation": stress_distribution.get('high_stress', 0) / total_frames > 0.2,
                "recommendation": "practice_breathing" if stress_distribution.get('high_stress', 0) / total_frames > 0.2 else "maintain"
            }
        }
        
        # ATTENTION - Engagement and focus metrics
        attention = {
            "overall_engagement": {
                "avg_attention_score": float(df['attention_score'].mean()),
                "max_attention_score": float(df['attention_score'].max()),
                "min_attention_score": float(df['attention_score'].min()),
                "consistency": float(df['attention_score'].std())
            },
            "engagement_breakdown": {
                "engaged_percentage": float(df['is_engaged'].sum() / total_frames * 100) if 'is_engaged' in df.columns else 50.0,
                "distracted_percentage": float(df['is_distracted'].sum() / total_frames * 100) if 'is_distracted' in df.columns else 0.0,
                "neutral_percentage": float((total_frames - df['is_engaged'].sum() - df['is_distracted'].sum()) / total_frames * 100) if 'is_engaged' in df.columns and 'is_distracted' in df.columns else 50.0
            },
            "focus_quality": {
                "camera_focus_percentage": float(df['is_looking_at_camera'].sum() / total_frames * 100) if 'is_looking_at_camera' in df.columns else 50.0,
                "attention_lapses": int((df['is_distracted'] == True).sum()) if 'is_distracted' in df.columns else 0,
                "recommendation": "improve_focus" if 'is_engaged' in df.columns and df['is_engaged'].sum() / total_frames < 0.6 else "maintain"
            },
            "alert_summary": {
                "total_alerts": int(df['alert_count'].sum()) if 'alert_count' in df.columns else 0,
                "avg_alerts_per_minute": float(df['alert_count'].sum() / (df['elapsed_seconds'].max() / 60)) if 'alert_count' in df.columns and df['elapsed_seconds'].max() > 0 else 0.0
            }
        }
        
        # Compile final analysis
        analysis = {
            "session_info": {
                "session_id": self.session_id,
                "start_time": self.session_start_time.isoformat(),
                "duration_seconds": float(df['elapsed_seconds'].max()),
                "total_frames_analyzed": int(total_frames),
                "avg_fps": float(total_frames / df['elapsed_seconds'].max())
            },
            "emotions": emotions,
            "facial_metrics": facial_metrics,
            "head_pose": head_pose,
            "postures": postures,
            "gestures": gestures,
            "stress": stress,
            "attention": attention,
            "overall_interview_score": {
                "attention_score": float(df['attention_score'].mean()),
                "posture_score": float((posture_counts.get('upright_relaxed', 0) + posture_counts.get('engaged_forward_lean', 0)) / total_frames),
                "expression_score": float(1 - stress_distribution.get('high_stress', 0) / total_frames),
                "gesture_score": float(1 - (df['face_touching'].sum() + df['hand_fidgeting'].sum()) / (2 * total_frames)),
                "overall_score": round((
                    df['attention_score'].mean() * 0.30 +  # 30% weight - engagement and focus
                    ((posture_counts.get('upright_relaxed', 0) + posture_counts.get('engaged_forward_lean', 0)) / total_frames) * 0.25 +  # 25% - body language
                    (1 - stress_distribution.get('high_stress', 0) / total_frames) * 0.25 +  # 25% - emotional control
                    (1 - (df['face_touching'].sum() + df['hand_fidgeting'].sum()) / (2 * total_frames)) * 0.20  # 20% - gesture control
                ) * 100)  # Convert to 0-100 scale and round to integer
            },
        }
        
        # Export to JSON
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        filename = f"{output_dir}/interview_analysis_{self.session_id}.json"
        
        with open(filename, 'w') as f:
            json.dump(analysis, f, indent=2)
        
        print(f"[DataLogger] Interview analysis exported: {filename}")
        return filename
    
    def _classify_blink_rate(self, blink_rate: float) -> str:
        """Classify blink rate"""
        if blink_rate < 10:
            return "drowsy"
        elif blink_rate < 15:
            return "low_normal"
        elif blink_rate <= 20:
            return "optimal"
        elif blink_rate <= 30:
            return "elevated"
        else:
            return "stressed"
    
    def _generate_recommendations(self, df, emotion_counts, posture_counts, stress_distribution, total_frames) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []
        
        # Eye contact
        if df['is_looking_at_camera'].sum() / total_frames < 0.7:
            recommendations.append("Maintain eye contact with camera for at least 70% of the interview")
        
        # Posture
        if (posture_counts.get('slouching', 0) + posture_counts.get('leaning_back', 0)) / total_frames > 0.3:
            recommendations.append("Sit upright with slight forward lean to show engagement")
        
        # Expressions
        if emotion_counts.get('genuine_smile', 0) / total_frames < 0.2:
            recommendations.append("Smile more naturally when discussing positive topics")
        
        # Stress
        if stress_distribution.get('high_stress', 0) / total_frames > 0.2:
            recommendations.append("Practice breathing exercises to manage interview stress")
        
        # Fidgeting
        if df['face_touching'].sum() / total_frames > 0.1:
            recommendations.append("Reduce face touching - keep hands visible and still")
        
        if df['hand_fidgeting'].sum() / total_frames > 0.2:
            recommendations.append("Control hand movements - use purposeful gestures only")
        
        # Overall engagement
        if df['is_engaged'].sum() / total_frames < 0.6:
            recommendations.append("Increase overall engagement - lean forward, make eye contact, show interest")
        
        if not recommendations:
            recommendations.append("Excellent interview performance! Maintain current behaviors.")
        
        return recommendations
    
    def export_all(self, output_dir: str = "exports") -> Dict[str, str]:
        """Export interview analysis and session JSON only"""
        return {
            'interview_analysis': self.export_interview_analysis(output_dir),
            'session_json': self.export_to_json(output_dir)
        }
    
    def clear_buffer(self):
        """Clear data buffer"""
        self.data_buffer = []
        print("[DataLogger] Buffer cleared")
