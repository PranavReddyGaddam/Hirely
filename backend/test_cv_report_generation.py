#!/usr/bin/env python3
"""
Test CV Report Generation with Groq LLM
Reads analysis_report.json and generates user-friendly feedback
"""

import sys
import os
sys.path.insert(0, '.')

import json
import asyncio
from pathlib import Path
from app.services.groq_service import GroqService
from app.utils.logger import get_logger

logger = get_logger(__name__)


def load_analysis_report(report_path: str = "analysis_report.json") -> dict:
    """Load the CV analysis report"""
    try:
        with open(report_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"❌ Error: Could not find {report_path}")
        print(f"   Make sure you've run CV analysis first!")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"❌ Error: Invalid JSON in {report_path}")
        sys.exit(1)


def build_analysis_prompt(analysis: dict) -> str:
    """Build comprehensive prompt for Groq from analysis data"""
    
    video_info = analysis.get('video_info', {})
    cv_data = analysis.get('cv_analysis', {})
    
    overall_score = cv_data.get('overall_interview_score', {})
    emotions = cv_data.get('emotions', {})
    facial = cv_data.get('facial_metrics', {})
    head_pose = cv_data.get('head_pose', {})
    postures = cv_data.get('postures', {})
    gestures = cv_data.get('gestures', {})
    stress = cv_data.get('stress', {})
    attention = cv_data.get('attention', {})
    
    prompt = f"""You are an expert interview coach analyzing a candidate's video interview performance.

**VIDEO INFORMATION:**
- Duration: {video_info.get('duration_seconds', 0):.1f} seconds
- Frames Analyzed: {video_info.get('frames_analyzed', 0)}

**OVERALL PERFORMANCE:**
- Overall Score: {overall_score.get('overall_score', 0):.1f}/100
- Attention Score: {overall_score.get('attention_score', 0) * 100:.1f}%
- Expression Score: {overall_score.get('expression_score', 0) * 100:.1f}%
- Gesture Control: {overall_score.get('gesture_score', 0) * 100:.1f}%
- Posture Score: {overall_score.get('posture_score', 0) * 100:.1f}%

**EMOTIONAL EXPRESSION:**
- Dominant Emotion: {emotions.get('dominant_emotion', 'unknown')}
- Emotion Distribution:
  * Calm: {emotions.get('expression_distribution', {}).get('calm', 0):.1f}%
  * Genuine Smile: {emotions.get('expression_distribution', {}).get('genuine_smile', 0):.1f}%
  * Tense: {emotions.get('expression_distribution', {}).get('tense', 0):.1f}%
  * Sad: {emotions.get('expression_distribution', {}).get('sad', 0):.1f}%
- Emotional Stability: {emotions.get('emotional_stability', {}).get('score', 'unknown')}
- Average Smile Intensity: {emotions.get('smile_analysis', {}).get('avg_smile_intensity', 0):.2f}

**EYE CONTACT & FACIAL METRICS:**
- Average Eye Openness: {facial.get('eye_contact', {}).get('avg_eye_openness_both', 0):.2f}
- Eye Symmetry: {facial.get('eye_contact', {}).get('symmetry', 'unknown')}
- Total Blinks: {facial.get('blink_pattern', {}).get('total_blinks', 0)}
- Blink Rate: {facial.get('blink_pattern', {}).get('avg_blink_rate_per_minute', 0):.1f} bpm (normal: 15-20)
- Blink Status: {facial.get('blink_pattern', {}).get('status', 'unknown')}
- Mouth Activity: {facial.get('mouth_activity', {}).get('talking_indicator', 'unknown')}

**HEAD POSITION & GAZE:**
- Looking at Camera: {head_pose.get('camera_focus', {}).get('looking_at_camera_percentage', 0):.1f}%
- Average Head Position:
  * Yaw (left-right): {head_pose.get('gaze_direction', {}).get('avg_yaw_degrees', 0):.1f}°
  * Pitch (up-down): {head_pose.get('gaze_direction', {}).get('avg_pitch_degrees', 0):.1f}°
  * Roll (tilt): {head_pose.get('gaze_direction', {}).get('avg_roll_degrees', 0):.1f}°
- Head Stability: {head_pose.get('head_stability', {}).get('score', 'unknown')}

**POSTURE & BODY LANGUAGE:**
- Dominant Posture: {postures.get('dominant_posture', 'unknown')}
- Good Posture: {postures.get('posture_quality', {}).get('good_posture_percentage', 0):.1f}%
- Average Neck Angle: {postures.get('body_angles', {}).get('avg_neck_angle_degrees', 0):.1f}° (ideal: 10-30°)
- Average Torso Angle: {postures.get('body_angles', {}).get('avg_torso_angle_degrees', 0):.1f}° (ideal: 5-20°)

**GESTURES & NERVOUS BEHAVIORS:**
- Face Touching: {gestures.get('face_touching', {}).get('percentage_of_time', 0):.1f}% (occurrences: {gestures.get('face_touching', {}).get('total_occurrences', 0)})
- Hand Fidgeting: {gestures.get('hand_fidgeting', {}).get('percentage_of_time', 0):.1f}%
- Excessive Gesturing: {gestures.get('excessive_gesturing', {}).get('percentage_of_time', 0):.1f}%
- Controlled Gestures: {gestures.get('overall_gesture_quality', {}).get('controlled_percentage', 0):.1f}%
- Gesture Quality: {gestures.get('overall_gesture_quality', {}).get('score', 'unknown')}

**STRESS INDICATORS:**
- Dominant Stress Level: {stress.get('dominant_stress_level', 'unknown')}
- Average Blink Rate: {stress.get('stress_indicators', {}).get('avg_blink_rate', 0):.1f} bpm
- Rapid Blinking: {stress.get('stress_indicators', {}).get('rapid_blinking_percentage', 0):.1f}%
- Fidgeting: {stress.get('stress_indicators', {}).get('fidgeting_percentage', 0):.1f}%

**ATTENTION & ENGAGEMENT:**
- Average Attention Score: {attention.get('overall_engagement', {}).get('avg_attention_score', 0):.2f}
- Engaged Time: {attention.get('engagement_breakdown', {}).get('engaged_percentage', 0):.1f}%
- Distracted Time: {attention.get('engagement_breakdown', {}).get('distracted_percentage', 0):.1f}%
- Neutral Time: {attention.get('engagement_breakdown', {}).get('neutral_percentage', 0):.1f}%
- Camera Focus: {attention.get('focus_quality', {}).get('camera_focus_percentage', 0):.1f}%
- Attention Lapses: {attention.get('focus_quality', {}).get('attention_lapses', 0)}

---

Based on this comprehensive behavioral analysis, please provide a detailed, constructive interview performance report with:

1. **Executive Summary** (2-3 sentences)
   - Overall impression of the candidate's interview presence
   - Key takeaway about their performance

2. **Top 3 Strengths**
   - Identify specific strong points with data references
   - Explain why each strength is valuable in interviews
   - Example format: "Excellent eye contact (85% camera focus) - demonstrates confidence and engagement"

3. **Top 3 Areas for Improvement**
   - Point out specific weaknesses with data
   - Explain the impact of each issue
   - Provide actionable advice to improve

4. **Specific Recommendations** (5-7 actionable tips)
   - Concrete steps the candidate can take to improve
   - Prioritized by impact
   - Practical and immediately applicable

5. **Overall Assessment**
   - Letter grade (A+ to F) with justification
   - Future outlook if improvements are made

Please be constructive, encouraging, and specific. Reference the actual metrics in your feedback.
Format your response in clear sections with markdown formatting."""

    return prompt


async def generate_feedback_report(analysis: dict) -> dict:
    """Generate user-friendly feedback using Groq LLM"""
    
    print("🤖 Initializing Groq LLM service...")
    groq_service = GroqService()
    
    if not groq_service.client:
        print("❌ Error: Groq client not available!")
        print("   Please check your GROQ_API_KEY in .env file")
        return None
    
    print("✅ Groq service initialized")
    print()
    print("📝 Building analysis prompt...")
    prompt = build_analysis_prompt(analysis)
    
    print(f"   Prompt length: {len(prompt)} characters")
    print()
    print("🔄 Sending to Groq GPT OSS 120B...")
    
    try:
        response = groq_service.client.chat.completions.create(
            model="openai/gpt-oss-120b",  # Using GPT OSS 120B model
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert interview coach providing constructive, data-driven feedback to help candidates improve their interview skills."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.7,
            max_tokens=2500,
            top_p=0.9
        )
        
        feedback_text = response.choices[0].message.content
        
        print("✅ Feedback generated successfully!")
        print()
        
        return {
            "success": True,
            "feedback": feedback_text,
            "model": "openai/gpt-oss-120b",
            "tokens_used": {
                "prompt": response.usage.prompt_tokens,
                "completion": response.usage.completion_tokens,
                "total": response.usage.total_tokens
            }
        }
        
    except Exception as e:
        logger.error(f"Error generating feedback with Groq: {e}", exc_info=True)
        print(f"❌ Error: {e}")
        return None


def save_feedback_report(feedback_data: dict, output_path: str = "interview_feedback_report.json"):
    """Save the complete feedback report"""
    
    with open(output_path, 'w') as f:
        json.dump(feedback_data, f, indent=2)
    
    print(f"💾 Complete report saved to: {output_path}")


def display_feedback(feedback_text: str):
    """Display the feedback in a formatted way"""
    
    print()
    print("="*80)
    print("📋 INTERVIEW PERFORMANCE FEEDBACK")
    print("="*80)
    print()
    print(feedback_text)
    print()
    print("="*80)


async def main():
    """Main test function"""
    
    print()
    print("🎥 CV Analysis Report → LLM Feedback Generator")
    print("="*80)
    print()
    
    # Load the analysis report
    print("📂 Loading analysis report...")
    analysis = load_analysis_report("analysis_report.json")
    print(f"✅ Loaded analysis for video: {analysis['video_info']['filename']}")
    print(f"   Duration: {analysis['video_info']['duration_seconds']:.1f}s")
    print(f"   Frames analyzed: {analysis['video_info']['frames_analyzed']}")
    print(f"   Overall score: {analysis['cv_analysis']['overall_interview_score']['overall_score']:.0f}/100")
    print()
    
    # Generate feedback
    feedback_data = await generate_feedback_report(analysis)
    
    if not feedback_data:
        print("❌ Failed to generate feedback")
        sys.exit(1)
    
    # Display the feedback
    display_feedback(feedback_data['feedback'])
    
    # Show token usage
    print(f"📊 Token Usage:")
    print(f"   Prompt tokens: {feedback_data['tokens_used']['prompt']}")
    print(f"   Completion tokens: {feedback_data['tokens_used']['completion']}")
    print(f"   Total tokens: {feedback_data['tokens_used']['total']}")
    print()
    
    # Save complete report
    complete_report = {
        "analysis": analysis,
        "llm_feedback": feedback_data
    }
    save_feedback_report(complete_report, "interview_feedback_report.json")
    
    print()
    print("✅ Test complete!")
    print()
    print("📁 Generated files:")
    print("   - analysis_report.json (CV metrics)")
    print("   - interview_feedback_report.json (CV metrics + LLM feedback)")
    print()
    print("🎯 You can now use this feedback to show users their interview performance!")


if __name__ == "__main__":
    asyncio.run(main())

