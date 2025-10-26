"""
Enhanced Metrics Calculator
Calculates detailed, actionable metrics from existing CV and transcript analysis data
"""

from typing import Dict, List, Optional, Any
import numpy as np


class EnhancedMetricsCalculator:
    """Calculate enhanced metrics from existing analysis data"""
    
    def __init__(self):
        # Benchmark data (based on typical interview performance)
        self.benchmarks = {
            'eye_contact': {'avg': 65, 'top_10': 85},
            'posture': {'avg': 70, 'top_10': 88},
            'filler_words': {'avg': 8.5, 'top_10': 2.0},
            'speaking_pace': {'avg': 140, 'top_10': 150, 'min': 130, 'max': 160},
            'vocabulary_diversity': {'avg': 0.55, 'top_10': 0.75},
            'confidence': {'avg': 70, 'top_10': 90},
        }
    
    def calculate_enhanced_cv_metrics(self, cv_analysis: Dict) -> Dict[str, Any]:
        """Calculate enhanced CV/visual behavior metrics"""
        enhanced = {
            'professional_presence': self._calculate_professional_presence(cv_analysis),
            'eye_contact_detailed': self._calculate_eye_contact_details(cv_analysis),
            'posture_detailed': self._calculate_posture_details(cv_analysis),
            'energy_enthusiasm': self._calculate_energy_metrics(cv_analysis),
            'nervousness_indicators': self._calculate_nervousness_metrics(cv_analysis),
            'time_series': self._extract_time_series_if_available(cv_analysis)
        }
        return enhanced
    
    def calculate_enhanced_communication_metrics(self, transcript_analysis: Dict) -> Dict[str, Any]:
        """Calculate enhanced communication metrics"""
        enhanced = {
            'speech_quality': self._calculate_speech_quality(transcript_analysis),
            'filler_analysis_detailed': self._calculate_filler_details(transcript_analysis),
            'response_structure': self._calculate_response_structure(transcript_analysis),
            'vocabulary_detailed': self._calculate_vocabulary_details(transcript_analysis),
            'confidence_indicators': self._calculate_comm_confidence(transcript_analysis)
        }
        return enhanced
    
    def calculate_improvement_roadmap(
        self,
        cv_analysis: Dict,
        transcript_analysis: Dict,
        enhanced_cv: Dict,
        enhanced_comm: Dict
    ) -> List[Dict[str, Any]]:
        """Generate prioritized improvement roadmap"""
        issues = []
        
        # Check eye contact
        if cv_analysis.get('eye_contact', {}).get('looking_at_camera_percentage', 100) < 70:
            issues.append({
                'priority': 'high',
                'category': 'Visual Behavior',
                'issue': 'Low Eye Contact',
                'current': f"{cv_analysis.get('eye_contact', {}).get('looking_at_camera_percentage', 0):.0f}%",
                'target': '80%+',
                'impact': 'Eye contact shows confidence and engagement',
                'action': 'Practice looking directly at camera, imagine interviewer behind it'
            })
        
        # Check filler words
        filler_pct = transcript_analysis.get('filler_word_analysis', {}).get('filler_percentage', 0)
        if filler_pct > 5.0:
            issues.append({
                'priority': 'high',
                'category': 'Communication',
                'issue': 'Frequent Filler Words',
                'current': f"{filler_pct:.1f}%",
                'target': '<3%',
                'impact': 'Filler words reduce perceived confidence',
                'action': 'Practice pausing instead of using "um", "uh". Record yourself speaking.'
            })
        
        # Check posture
        good_posture = cv_analysis.get('posture', {}).get('good_posture_percentage', 100)
        if good_posture < 75:
            issues.append({
                'priority': 'medium',
                'category': 'Visual Behavior',
                'issue': 'Inconsistent Posture',
                'current': f"{good_posture:.0f}%",
                'target': '85%+',
                'impact': 'Posture affects perceived professionalism',
                'action': 'Sit up straight, feet flat on floor, shoulders back'
            })
        
        # Check vocabulary
        diversity = transcript_analysis.get('word_diversity', {}).get('diversity_ratio', 1.0)
        if diversity < 0.55:
            issues.append({
                'priority': 'medium',
                'category': 'Communication',
                'issue': 'Limited Vocabulary',
                'current': f"{diversity:.0%}",
                'target': '65%+',
                'impact': 'Vocabulary shows communication skills',
                'action': 'Use varied words, avoid repeating same phrases'
            })
        
        # Check fidgeting
        fidgeting = enhanced_cv.get('nervousness_indicators', {}).get('hand_fidgeting_count', 0)
        if fidgeting > 10:
            issues.append({
                'priority': 'low',
                'category': 'Visual Behavior',
                'issue': 'Fidgeting Detected',
                'current': f"{fidgeting} times",
                'target': '<5 times',
                'impact': 'Subtle sign of nervousness',
                'action': 'Keep hands still, on desk or lap. Practice awareness.'
            })
        
        # Sort by priority
        priority_order = {'high': 0, 'medium': 1, 'low': 2}
        issues.sort(key=lambda x: priority_order.get(x['priority'], 3))
        
        return issues[:5]  # Return top 5 priorities
    
    def calculate_comparison_metrics(
        self,
        cv_analysis: Dict,
        transcript_analysis: Dict
    ) -> Dict[str, Any]:
        """Compare user's performance to benchmarks"""
        comparisons = {}
        
        # Eye contact comparison
        eye_contact = cv_analysis.get('eye_contact', {}).get('looking_at_camera_percentage', 0)
        comparisons['eye_contact'] = {
            'your_score': eye_contact,
            'average': self.benchmarks['eye_contact']['avg'],
            'top_10_percent': self.benchmarks['eye_contact']['top_10'],
            'status': 'above_average' if eye_contact > self.benchmarks['eye_contact']['avg'] else 'below_average',
            'percentile': self._calculate_percentile(eye_contact, 'eye_contact')
        }
        
        # Filler words comparison
        filler_pct = transcript_analysis.get('filler_word_analysis', {}).get('filler_percentage', 0)
        comparisons['filler_words'] = {
            'your_score': filler_pct,
            'average': self.benchmarks['filler_words']['avg'],
            'top_10_percent': self.benchmarks['filler_words']['top_10'],
            'status': 'above_average' if filler_pct < self.benchmarks['filler_words']['avg'] else 'below_average',
            'percentile': self._calculate_percentile(filler_pct, 'filler_words', inverse=True)
        }
        
        # Speaking pace comparison
        pace = transcript_analysis.get('speaking_pace', {}).get('words_per_minute', 0)
        comparisons['speaking_pace'] = {
            'your_score': pace,
            'average': self.benchmarks['speaking_pace']['avg'],
            'top_10_percent': self.benchmarks['speaking_pace']['top_10'],
            'ideal_range': f"{self.benchmarks['speaking_pace']['min']}-{self.benchmarks['speaking_pace']['max']}",
            'status': 'on_target' if self.benchmarks['speaking_pace']['min'] <= pace <= self.benchmarks['speaking_pace']['max'] else 'needs_adjustment'
        }
        
        # Vocabulary comparison
        diversity = transcript_analysis.get('word_diversity', {}).get('diversity_ratio', 0)
        comparisons['vocabulary'] = {
            'your_score': diversity,
            'average': self.benchmarks['vocabulary_diversity']['avg'],
            'top_10_percent': self.benchmarks['vocabulary_diversity']['top_10'],
            'status': 'above_average' if diversity > self.benchmarks['vocabulary_diversity']['avg'] else 'below_average',
            'percentile': self._calculate_percentile(diversity, 'vocabulary_diversity')
        }
        
        return comparisons
    
    def _calculate_professional_presence(self, cv_analysis: Dict) -> Dict:
        """Calculate overall professional presence score"""
        scores = []
        weights = []
        
        # Eye contact (30% weight)
        eye_contact = cv_analysis.get('eye_contact', {}).get('looking_at_camera_percentage', 0)
        scores.append(eye_contact)
        weights.append(0.3)
        
        # Posture (30% weight)
        posture = cv_analysis.get('posture', {}).get('good_posture_percentage', 0)
        scores.append(posture)
        weights.append(0.3)
        
        # Engagement (20% weight)
        engagement = cv_analysis.get('overall_interview_score', {}).get('engagement_score', 0)
        scores.append(engagement)
        weights.append(0.2)
        
        # Emotional stability (20% weight)
        emotional_stability = cv_analysis.get('emotions', {}).get('emotional_stability', {}).get('score', 50)
        scores.append(emotional_stability)
        weights.append(0.2)
        
        total_score = sum(s * w for s, w in zip(scores, weights))
        
        return {
            'overall_score': round(total_score, 1),
            'components': {
                'eye_contact': eye_contact,
                'posture': posture,
                'engagement': engagement,
                'emotional_stability': emotional_stability
            },
            'rating': self._get_rating(total_score)
        }
    
    def _calculate_eye_contact_details(self, cv_analysis: Dict) -> Dict:
        """Detailed eye contact analysis"""
        eye_data = cv_analysis.get('eye_contact', {})
        
        looking_at_camera = eye_data.get('looking_at_camera_percentage', 0)
        looking_away = eye_data.get('looking_away_percentage', 0)
        looking_down = eye_data.get('looking_down_percentage', 0)
        
        return {
            'direct_contact_percentage': looking_at_camera,
            'looking_away_percentage': looking_away,
            'looking_down_percentage': looking_down,
            'quality_rating': self._get_eye_contact_rating(looking_at_camera),
            'improvement_needed': looking_at_camera < 75,
            'tip': self._get_eye_contact_tip(looking_at_camera, looking_down)
        }
    
    def _calculate_posture_details(self, cv_analysis: Dict) -> Dict:
        """Detailed posture analysis"""
        posture_data = cv_analysis.get('posture', {})
        
        good_posture_pct = posture_data.get('good_posture_percentage', 0)
        slouching = posture_data.get('slouching_detected', False)
        
        return {
            'upright_percentage': good_posture_pct,
            'slouching_detected': slouching,
            'quality_rating': self._get_posture_rating(good_posture_pct),
            'improvement_needed': good_posture_pct < 80,
            'tip': 'Maintain upright posture throughout. Take breaks if needed to reset posture.' if good_posture_pct < 80 else 'Excellent posture maintained!'
        }
    
    def _calculate_energy_metrics(self, cv_analysis: Dict) -> Dict:
        """Calculate energy and enthusiasm metrics"""
        emotions = cv_analysis.get('emotions', {})
        smile_data = emotions.get('smile_analysis', {})
        
        genuine_smiles = smile_data.get('genuine_smile_count', 0)
        dominant_emotion = emotions.get('dominant_emotion', 'calm')
        
        # Energy level based on emotions
        energy_level = 70  # Default
        if dominant_emotion in ['genuine_smile', 'happy']:
            energy_level = 85
        elif dominant_emotion in ['sad', 'tense']:
            energy_level = 50
        
        return {
            'energy_level': energy_level,
            'genuine_smiles': genuine_smiles,
            'dominant_emotion': dominant_emotion,
            'enthusiasm_rating': 'High' if genuine_smiles > 5 else 'Moderate' if genuine_smiles > 2 else 'Low'
        }
    
    def _calculate_nervousness_metrics(self, cv_analysis: Dict) -> Dict:
        """Calculate nervousness indicators"""
        gestures = cv_analysis.get('gestures', {})
        emotions = cv_analysis.get('emotions', {})
        
        hand_fidgeting = gestures.get('hand_fidgeting_count', 0)
        face_touching = gestures.get('face_touching_count', 0)
        blink_rate = emotions.get('blink_rate', 0)
        stress_level = emotions.get('stress_level', 'unknown')
        
        total_nervous_movements = hand_fidgeting + face_touching
        
        return {
            'hand_fidgeting_count': hand_fidgeting,
            'face_touching_count': face_touching,
            'total_nervous_movements': total_nervous_movements,
            'blink_rate': blink_rate,
            'stress_level': stress_level,
            'nervousness_rating': self._get_nervousness_rating(total_nervous_movements, stress_level)
        }
    
    def _calculate_speech_quality(self, transcript_analysis: Dict) -> Dict:
        """Calculate speech quality metrics"""
        pace_data = transcript_analysis.get('speaking_pace', {})
        
        wpm = pace_data.get('words_per_minute', 0)
        pace_rating = pace_data.get('pace_rating', 'unknown')
        
        # Calculate pace consistency (if we have variation data)
        pace_consistency = 85  # Default estimate
        
        return {
            'speaking_pace_wpm': wpm,
            'pace_rating': pace_rating,
            'pace_consistency': pace_consistency,
            'in_ideal_range': 130 <= wpm <= 160,
            'tip': self._get_pace_tip(wpm)
        }
    
    def _calculate_filler_details(self, transcript_analysis: Dict) -> Dict:
        """Detailed filler word analysis"""
        filler_data = transcript_analysis.get('filler_word_analysis', {})
        
        total = filler_data.get('total_filler_words', 0)
        percentage = filler_data.get('filler_percentage', 0)
        most_used = filler_data.get('most_used_filler', 'none')
        most_used_count = filler_data.get('most_used_count', 0)
        rating = filler_data.get('rating', 'unknown')
        
        return {
            'total_count': total,
            'percentage': percentage,
            'most_used': most_used,
            'most_used_count': most_used_count,
            'rating': rating,
            'confidence_impact': self._get_filler_impact(percentage),
            'tip': self._get_filler_tip(percentage, most_used)
        }
    
    def _calculate_response_structure(self, transcript_analysis: Dict) -> Dict:
        """Analyze response structure"""
        messages = transcript_analysis.get('messages', [])
        
        if not messages:
            return {
                'avg_response_length_words': 0,
                'responses_analyzed': 0
            }
        
        # Filter user responses
        user_responses = [msg for msg in messages if msg.get('role') == 'user']
        
        if not user_responses:
            return {
                'avg_response_length_words': 0,
                'responses_analyzed': 0
            }
        
        # Calculate average response length
        response_lengths = [len(msg.get('message', '').split()) for msg in user_responses]
        avg_length = np.mean(response_lengths) if response_lengths else 0
        
        # Check for too short or too long
        too_short = sum(1 for length in response_lengths if length < 20)
        too_long = sum(1 for length in response_lengths if length > 150)
        
        return {
            'avg_response_length_words': round(avg_length, 1),
            'responses_analyzed': len(user_responses),
            'too_short_count': too_short,
            'too_long_count': too_long,
            'balance_rating': 'Good' if too_short == 0 and too_long == 0 else 'Needs Work'
        }
    
    def _calculate_vocabulary_details(self, transcript_analysis: Dict) -> Dict:
        """Detailed vocabulary analysis"""
        diversity_data = transcript_analysis.get('word_diversity', {})
        
        unique = diversity_data.get('unique_words', 0)
        total = diversity_data.get('total_words', 0)
        ratio = diversity_data.get('diversity_ratio', 0)
        
        return {
            'unique_words': unique,
            'total_words': total,
            'diversity_ratio': ratio,
            'diversity_percentage': ratio * 100,
            'rating': self._get_vocabulary_rating(ratio),
            'tip': 'Expand vocabulary, avoid repeating same words' if ratio < 0.55 else 'Strong vocabulary diversity!'
        }
    
    def _calculate_comm_confidence(self, transcript_analysis: Dict) -> Dict:
        """Calculate communication confidence indicators"""
        filler_pct = transcript_analysis.get('filler_word_analysis', {}).get('filler_percentage', 0)
        
        # Confidence is inversely related to filler words
        confidence_score = max(0, 100 - (filler_pct * 10))
        
        return {
            'confidence_score': round(confidence_score, 1),
            'rating': self._get_confidence_rating(confidence_score),
            'based_on': 'Low filler word usage indicates confidence'
        }
    
    def _extract_time_series_if_available(self, cv_analysis: Dict) -> Optional[Dict]:
        """Extract time-series data if available"""
        # Check if we have frame-by-frame data
        if 'frame_data' in cv_analysis or 'time_series' in cv_analysis:
            return cv_analysis.get('time_series', cv_analysis.get('frame_data'))
        return None
    
    def _calculate_percentile(self, score: float, metric: str, inverse: bool = False) -> int:
        """Estimate percentile ranking"""
        if metric not in self.benchmarks:
            return 50
        
        bench = self.benchmarks[metric]
        avg = bench['avg']
        top = bench['top_10']
        
        if inverse:
            # For metrics where lower is better (e.g., filler words)
            if score <= top:
                return 90
            elif score <= avg:
                return 60
            elif score <= avg * 1.5:
                return 40
            else:
                return 20
        else:
            # For metrics where higher is better
            if score >= top:
                return 90
            elif score >= avg:
                return 60
            elif score >= avg * 0.75:
                return 40
            else:
                return 20
    
    def _get_rating(self, score: float) -> str:
        """Get rating from score"""
        if score >= 85:
            return 'Excellent'
        elif score >= 75:
            return 'Good'
        elif score >= 65:
            return 'Fair'
        else:
            return 'Needs Improvement'
    
    def _get_eye_contact_rating(self, percentage: float) -> str:
        """Get eye contact rating"""
        if percentage >= 80:
            return 'Excellent'
        elif percentage >= 65:
            return 'Good'
        elif percentage >= 50:
            return 'Fair'
        else:
            return 'Needs Improvement'
    
    def _get_eye_contact_tip(self, looking_at_camera: float, looking_down: float) -> str:
        """Get personalized eye contact tip"""
        if looking_at_camera < 65:
            if looking_down > 20:
                return 'Looking down too often. Place notes at eye level, practice confidence.'
            else:
                return 'Maintain eye contact with camera. Imagine interviewer behind it.'
        return 'Great eye contact! Keep it up.'
    
    def _get_posture_rating(self, percentage: float) -> str:
        """Get posture rating"""
        if percentage >= 85:
            return 'Excellent'
        elif percentage >= 75:
            return 'Good'
        elif percentage >= 65:
            return 'Fair'
        else:
            return 'Needs Improvement'
    
    def _get_nervousness_rating(self, movements: int, stress_level: str) -> str:
        """Get nervousness rating"""
        if movements < 5 and stress_level != 'high_stress':
            return 'Calm'
        elif movements < 10:
            return 'Slightly Nervous'
        else:
            return 'Nervous'
    
    def _get_pace_tip(self, wpm: float) -> str:
        """Get pace tip"""
        if wpm < 130:
            return 'Speaking too slowly. Practice speaking at natural pace (130-160 WPM).'
        elif wpm > 160:
            return 'Speaking too fast. Slow down, take breaths between sentences.'
        return 'Perfect pace! Clear and natural.'
    
    def _get_filler_impact(self, percentage: float) -> str:
        """Get filler word impact assessment"""
        if percentage < 3:
            return 'Minimal impact - Professional'
        elif percentage < 6:
            return 'Slight impact - Acceptable'
        elif percentage < 10:
            return 'Moderate impact - Reduces confidence perception'
        else:
            return 'High impact - Significantly reduces professionalism'
    
    def _get_filler_tip(self, percentage: float, most_used: str) -> str:
        """Get personalized filler tip"""
        if percentage < 3:
            return 'Excellent filler word control!'
        elif percentage < 6:
            return f'Good control. Watch for "{most_used}" - pause instead.'
        else:
            return f'Reduce "{most_used}" usage. Practice pausing, recording yourself helps.'
    
    def _get_vocabulary_rating(self, ratio: float) -> str:
        """Get vocabulary rating"""
        if ratio >= 0.7:
            return 'Excellent'
        elif ratio >= 0.6:
            return 'Good'
        elif ratio >= 0.5:
            return 'Fair'
        else:
            return 'Needs Improvement'
    
    def _get_confidence_rating(self, score: float) -> str:
        """Get confidence rating"""
        if score >= 85:
            return 'Very Confident'
        elif score >= 70:
            return 'Confident'
        elif score >= 60:
            return 'Moderately Confident'
        else:
            return 'Needs Work'
