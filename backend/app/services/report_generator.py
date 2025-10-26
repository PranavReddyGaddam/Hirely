"""
Report Generator Service
Creates comprehensive, formatted interview analysis reports
"""
from typing import Dict, Any, Optional
from datetime import datetime


class ReportGenerator:
    """Generates comprehensive interview reports"""
    
    def generate_pdf_report(
        self,
        interview_id: str,
        candidate_name: str,
        position: str,
        analysis_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate a comprehensive PDF-ready report.
        
        Args:
            interview_id: Interview identifier
            candidate_name: Candidate's name
            position: Position applied for
            analysis_data: Complete analysis results
            
        Returns:
            Dict with formatted report sections
        """
        
        overall_score = analysis_data.get('overall_score', {})
        cv_analysis = analysis_data.get('cv_analysis', {})
        transcript_analysis = analysis_data.get('transcript_analysis', {})
        ai_insights = analysis_data.get('ai_insights', {})
        
        report = {
            "report_id": f"REPORT_{interview_id}_{datetime.now().strftime('%Y%m%d')}",
            "generated_at": datetime.now().isoformat(),
            "candidate_info": {
                "name": candidate_name,
                "position": position,
                "interview_id": interview_id
            },
            "executive_summary": self._generate_executive_summary(overall_score, ai_insights),
            "performance_overview": self._generate_performance_overview(overall_score),
            "visual_behavior": self._format_cv_analysis(cv_analysis),
            "communication_skills": self._format_transcript_analysis(transcript_analysis),
            "ai_recommendations": self._format_ai_insights(ai_insights),
            "detailed_metrics": self._generate_detailed_metrics(cv_analysis, transcript_analysis),
            "action_items": self._extract_action_items(ai_insights)
        }
        
        return report
    
    def _generate_executive_summary(
        self,
        overall_score: Dict,
        ai_insights: Dict
    ) -> Dict[str, Any]:
        """Generate executive summary section"""
        
        score = overall_score.get('overall_score', 0)
        grade = overall_score.get('grade', 'N/A')
        
        # Extract first paragraph from AI insights as summary
        feedback = ai_insights.get('feedback', '')
        summary_text = feedback.split('\n\n')[0] if feedback else "Analysis complete."
        
        performance_level = "Excellent" if score >= 85 else "Good" if score >= 70 else "Fair" if score >= 60 else "Needs Improvement"
        
        return {
            "overall_score": score,
            "grade": grade,
            "performance_level": performance_level,
            "summary": summary_text,
            "recommendation": self._get_hiring_recommendation(score)
        }
    
    def _get_hiring_recommendation(self, score: float) -> str:
        """Get hiring recommendation based on score"""
        if score >= 85:
            return "Strong candidate - Highly recommended"
        elif score >= 75:
            return "Good candidate - Recommended"
        elif score >= 65:
            return "Fair candidate - Consider with reservations"
        else:
            return "Not recommended - Significant areas need improvement"
    
    def _generate_performance_overview(self, overall_score: Dict) -> Dict[str, Any]:
        """Generate performance overview with scores"""
        return {
            "overall_score": overall_score.get('overall_score', 0),
            "grade": overall_score.get('grade', 'N/A'),
            "cv_score": overall_score.get('cv_score', 0),
            "communication_score": overall_score.get('communication_score', 0),
            "rating": overall_score.get('rating', 'unknown'),
            "breakdown": {
                "visual_behavior": f"{overall_score.get('cv_score', 0)}/100",
                "communication": f"{overall_score.get('communication_score', 0)}/100"
            }
        }
    
    def _format_cv_analysis(self, cv_analysis: Dict) -> Dict[str, Any]:
        """Format CV analysis data"""
        if not cv_analysis:
            return {"status": "Not available"}
        
        return {
            "emotions": {
                "dominant": cv_analysis.get('emotions', {}).get('dominant_emotion', 'unknown'),
                "stability": cv_analysis.get('emotions', {}).get('emotional_stability', {}).get('score', 'unknown'),
                "distribution": cv_analysis.get('emotions', {}).get('expression_distribution', {})
            },
            "eye_contact": {
                "camera_focus": cv_analysis.get('eye_contact', {}).get('looking_at_camera_percentage', 0),
                "rating": "Good" if cv_analysis.get('eye_contact', {}).get('looking_at_camera_percentage', 0) >= 70 else "Needs improvement"
            },
            "posture": {
                "good_posture_percentage": cv_analysis.get('posture', {}).get('good_posture_percentage', 0),
                "rating": "Good" if cv_analysis.get('posture', {}).get('good_posture_percentage', 0) >= 70 else "Needs improvement"
            },
            "overall_cv_score": cv_analysis.get('overall_interview_score', {}).get('overall_score', 0)
        }
    
    def _format_transcript_analysis(self, transcript_analysis: Dict) -> Dict[str, Any]:
        """Format transcript analysis data"""
        if not transcript_analysis:
            return {"status": "Not available"}
        
        filler = transcript_analysis.get('filler_word_analysis', {})
        pace = transcript_analysis.get('speaking_pace', {})
        diversity = transcript_analysis.get('word_diversity', {})
        structure = transcript_analysis.get('sentence_structure', {})
        comm_score = transcript_analysis.get('communication_score', {})
        
        return {
            "filler_words": {
                "total": filler.get('total_filler_words', 0),
                "percentage": filler.get('filler_percentage', 0),
                "most_used": filler.get('most_used_filler', 'none'),
                "rating": filler.get('rating', 'unknown'),
                "feedback": filler.get('feedback', '')
            },
            "speaking_pace": {
                "words_per_minute": pace.get('words_per_minute', 0),
                "rating": pace.get('pace_rating', 'unknown'),
                "feedback": pace.get('pace_feedback', '')
            },
            "vocabulary": {
                "total_words": diversity.get('total_words', 0),
                "unique_words": diversity.get('unique_words', 0),
                "diversity_ratio": diversity.get('diversity_ratio', 0),
                "rating": diversity.get('rating', 'unknown')
            },
            "sentence_structure": {
                "avg_length": structure.get('avg_sentence_length', 0),
                "rating": structure.get('rating', 'unknown'),
                "feedback": structure.get('feedback', '')
            },
            "overall_communication_score": {
                "score": comm_score.get('score', 0),
                "grade": comm_score.get('grade', 'N/A'),
                "rating": comm_score.get('rating', 'unknown')
            }
        }
    
    def _format_ai_insights(self, ai_insights: Dict) -> Dict[str, Any]:
        """Format AI insights"""
        if not ai_insights:
            return {"status": "Not available"}
        
        feedback = ai_insights.get('feedback', '')
        
        # Try to parse sections from feedback
        sections = {
            "full_feedback": feedback,
            "model": ai_insights.get('model', 'unknown'),
            "strengths": self._extract_section(feedback, "strengths"),
            "improvements": self._extract_section(feedback, "improvement"),
            "recommendations": self._extract_section(feedback, "recommendation")
        }
        
        return sections
    
    def _extract_section(self, text: str, keyword: str) -> list:
        """Extract bullet points from a section"""
        lines = text.split('\n')
        section_lines = []
        in_section = False
        
        for line in lines:
            if keyword.lower() in line.lower():
                in_section = True
                continue
            
            if in_section:
                if line.strip().startswith(('-', '•', '*', '1.', '2.', '3.')):
                    section_lines.append(line.strip())
                elif line.strip() and not line.strip().startswith('#'):
                    continue
                elif section_lines and not line.strip():
                    break
        
        return section_lines[:5]  # Return top 5
    
    def _generate_detailed_metrics(
        self,
        cv_analysis: Dict,
        transcript_analysis: Dict
    ) -> Dict[str, Any]:
        """Generate detailed metrics breakdown"""
        
        metrics = {
            "visual_behavior_metrics": [],
            "communication_metrics": []
        }
        
        # CV metrics
        if cv_analysis:
            if 'emotions' in cv_analysis:
                emotions = cv_analysis['emotions']
                metrics['visual_behavior_metrics'].append({
                    "metric": "Emotional Stability",
                    "value": emotions.get('emotional_stability', {}).get('score', 'N/A'),
                    "category": "Emotions"
                })
            
            if 'eye_contact' in cv_analysis:
                eye = cv_analysis['eye_contact']
                metrics['visual_behavior_metrics'].append({
                    "metric": "Eye Contact",
                    "value": f"{eye.get('looking_at_camera_percentage', 0):.1f}%",
                    "category": "Engagement"
                })
            
            if 'posture' in cv_analysis:
                posture = cv_analysis['posture']
                metrics['visual_behavior_metrics'].append({
                    "metric": "Posture Quality",
                    "value": f"{posture.get('good_posture_percentage', 0):.1f}%",
                    "category": "Body Language"
                })
        
        # Communication metrics
        if transcript_analysis:
            filler = transcript_analysis.get('filler_word_analysis', {})
            metrics['communication_metrics'].append({
                "metric": "Filler Word Usage",
                "value": f"{filler.get('filler_percentage', 0):.2f}%",
                "rating": filler.get('rating', 'unknown')
            })
            
            pace = transcript_analysis.get('speaking_pace', {})
            metrics['communication_metrics'].append({
                "metric": "Speaking Pace",
                "value": f"{pace.get('words_per_minute', 0):.1f} WPM",
                "rating": pace.get('pace_rating', 'unknown')
            })
            
            diversity = transcript_analysis.get('word_diversity', {})
            metrics['communication_metrics'].append({
                "metric": "Vocabulary Diversity",
                "value": f"{diversity.get('diversity_ratio', 0):.2%}",
                "rating": diversity.get('rating', 'unknown')
            })
        
        return metrics
    
    def _extract_action_items(self, ai_insights: Dict) -> list:
        """Extract actionable recommendations"""
        feedback = ai_insights.get('feedback', '')
        
        action_items = []
        
        # Look for sections with recommendations or action items
        lines = feedback.split('\n')
        in_action_section = False
        
        for line in lines:
            lower_line = line.lower()
            
            # Check if we're in an action-related section
            if any(keyword in lower_line for keyword in ['recommendation', 'next steps', 'action', 'improve']):
                in_action_section = True
                continue
            
            # Extract bullet points in action sections
            if in_action_section and line.strip().startswith(('-', '•', '*', '1.', '2.', '3.', '4.', '5.')):
                action_items.append(line.strip().lstrip('-•*123456789. '))
            elif in_action_section and not line.strip():
                # Empty line might indicate end of section
                if action_items:
                    break
        
        # If no action items found, generate generic ones based on scores
        if not action_items:
            action_items = [
                "Review the detailed analysis and identify key areas for improvement",
                "Practice interview scenarios to build confidence",
                "Focus on reducing filler words during responses",
                "Work on maintaining consistent eye contact",
                "Review communication feedback and implement suggestions"
            ]
        
        return action_items[:7]  # Return top 7 action items
    
    def generate_text_summary(self, analysis_data: Dict[str, Any]) -> str:
        """Generate a plain text summary of the analysis"""
        
        overall_score = analysis_data.get('overall_score', {})
        score = overall_score.get('overall_score', 0)
        grade = overall_score.get('grade', 'N/A')
        
        summary = f"""
INTERVIEW ANALYSIS SUMMARY
============================

Overall Performance: {score}/100 (Grade: {grade})

Visual Behavior Score: {overall_score.get('cv_score', 0)}/100
Communication Score: {overall_score.get('communication_score', 0)}/100

KEY HIGHLIGHTS:
- Interview performance rated as {overall_score.get('rating', 'unknown')}
- Analysis based on both visual behavior and communication patterns
- Comprehensive AI-powered insights included

For detailed analysis, please review the complete report.
        """
        
        return summary.strip()
