"""
Transcript Analysis Service
Analyzes interview transcripts for filler words, speaking pace, and other speech patterns
"""
import re
from typing import Dict, List, Any, Tuple
from collections import Counter

class TranscriptAnalyzer:
    """Service for analyzing interview transcripts"""
    
    # Filler words to track
    FILLER_WORDS = [
        "um", "uh", "er", "ah",
        "like", "you know", "so", "well",
        "actually", "basically", "literally",
        "i mean", "kind of", "sort of",
        "you see", "right", "okay"
    ]
    
    def __init__(self):
        """Initialize transcript analyzer"""
        pass
    
    def analyze_transcript(
        self,
        transcript: str,
        duration_seconds: float = 0
    ) -> Dict[str, Any]:
        """
        Perform comprehensive analysis on interview transcript.
        
        Args:
            transcript: Full transcript text
            duration_seconds: Duration of interview in seconds
            
        Returns:
            Dict containing analysis results
        """
        if not transcript or not transcript.strip():
            return self._empty_analysis()
        
        # Clean and normalize transcript
        transcript_lower = transcript.lower()
        
        # 1. Filler word analysis
        filler_analysis = self._analyze_filler_words(transcript_lower)
        
        # 2. Speaking pace analysis
        pace_analysis = self._analyze_speaking_pace(transcript, duration_seconds)
        
        # 3. Word diversity analysis
        diversity_analysis = self._analyze_word_diversity(transcript_lower)
        
        # 4. Sentence structure analysis
        structure_analysis = self._analyze_sentence_structure(transcript)
        
        # 5. Calculate overall communication score
        communication_score = self._calculate_communication_score(
            filler_analysis,
            pace_analysis,
            diversity_analysis,
            structure_analysis
        )
        
        return {
            "filler_word_analysis": filler_analysis,
            "speaking_pace": pace_analysis,
            "word_diversity": diversity_analysis,
            "sentence_structure": structure_analysis,
            "communication_score": communication_score,
            "full_transcript": transcript
        }
    
    def _analyze_filler_words(self, transcript_lower: str) -> Dict[str, Any]:
        """Analyze filler words in transcript"""
        
        filler_counts = {}
        total_filler_words = 0
        filler_positions = []
        
        # Count each filler word
        for filler in self.FILLER_WORDS:
            # Use word boundaries to match whole words/phrases
            pattern = r'\b' + re.escape(filler) + r'\b'
            matches = list(re.finditer(pattern, transcript_lower))
            count = len(matches)
            
            if count > 0:
                filler_counts[filler] = count
                total_filler_words += count
                
                # Record positions for timeline
                for match in matches:
                    filler_positions.append({
                        'word': filler,
                        'position': match.start()
                    })
        
        # Calculate total word count (approximate)
        words = transcript_lower.split()
        total_words = len(words)
        
        # Calculate filler word percentage
        filler_percentage = (total_filler_words / total_words * 100) if total_words > 0 else 0
        
        # Find most used filler word
        most_used = max(filler_counts.items(), key=lambda x: x[1]) if filler_counts else (None, 0)
        
        # Benchmark comparison (industry standard: < 5% is good)
        if filler_percentage < 3:
            rating = "excellent"
            feedback = "Minimal filler words - very professional speech"
        elif filler_percentage < 5:
            rating = "good"
            feedback = "Filler word usage is within acceptable range"
        elif filler_percentage < 8:
            rating = "fair"
            feedback = "Consider reducing filler words for better clarity"
        else:
            rating = "needs_improvement"
            feedback = "High filler word usage - practice speaking more deliberately"
        
        return {
            "total_filler_words": total_filler_words,
            "total_words": total_words,
            "filler_percentage": round(filler_percentage, 2),
            "filler_counts": dict(sorted(filler_counts.items(), key=lambda x: x[1], reverse=True)),
            "most_used_filler": most_used[0] if most_used[0] else "none",
            "most_used_count": most_used[1],
            "rating": rating,
            "feedback": feedback,
            "filler_positions": filler_positions[:50]  # Limit to first 50 for performance
        }
    
    def _analyze_speaking_pace(self, transcript: str, duration_seconds: float) -> Dict[str, Any]:
        """Analyze speaking pace"""
        
        words = transcript.split()
        total_words = len(words)
        
        if duration_seconds > 0:
            words_per_minute = (total_words / duration_seconds) * 60
            
            # Benchmark: 125-150 WPM is ideal for interviews
            if words_per_minute < 100:
                pace_rating = "too_slow"
                pace_feedback = "Speaking pace is quite slow - try to be more energetic"
            elif words_per_minute < 125:
                pace_rating = "slightly_slow"
                pace_feedback = "Speaking pace is slightly slow but acceptable"
            elif words_per_minute <= 150:
                pace_rating = "optimal"
                pace_feedback = "Perfect speaking pace - clear and engaging"
            elif words_per_minute <= 180:
                pace_rating = "slightly_fast"
                pace_feedback = "Speaking pace is slightly fast - remember to breathe"
            else:
                pace_rating = "too_fast"
                pace_feedback = "Speaking too quickly - slow down for better clarity"
        else:
            words_per_minute = 0
            pace_rating = "unknown"
            pace_feedback = "Unable to calculate speaking pace"
        
        return {
            "words_per_minute": round(words_per_minute, 1),
            "total_words": total_words,
            "duration_seconds": duration_seconds,
            "pace_rating": pace_rating,
            "pace_feedback": pace_feedback
        }
    
    def _analyze_word_diversity(self, transcript_lower: str) -> Dict[str, Any]:
        """Analyze vocabulary diversity"""
        
        # Remove punctuation and split into words
        words = re.findall(r'\b\w+\b', transcript_lower)
        
        if not words:
            return {
                "total_words": 0,
                "unique_words": 0,
                "diversity_ratio": 0,
                "rating": "unknown"
            }
        
        total_words = len(words)
        unique_words = len(set(words))
        diversity_ratio = unique_words / total_words if total_words > 0 else 0
        
        # Benchmark: > 0.5 is good vocabulary diversity
        if diversity_ratio >= 0.6:
            rating = "excellent"
            feedback = "Excellent vocabulary diversity"
        elif diversity_ratio >= 0.5:
            rating = "good"
            feedback = "Good vocabulary diversity"
        elif diversity_ratio >= 0.4:
            rating = "fair"
            feedback = "Fair vocabulary - try using more varied words"
        else:
            rating = "needs_improvement"
            feedback = "Limited vocabulary - expand your word choices"
        
        # Find most common words (excluding common stop words)
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'is', 'was', 'are', 'were', 'been', 'be', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'must', 'can', 'this', 'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'my', 'your', 'his', 'her', 'its', 'our', 'their'}
        
        content_words = [w for w in words if w not in stop_words and len(w) > 2]
        word_counts = Counter(content_words)
        most_common = word_counts.most_common(10)
        
        return {
            "total_words": total_words,
            "unique_words": unique_words,
            "diversity_ratio": round(diversity_ratio, 3),
            "rating": rating,
            "feedback": feedback,
            "most_common_words": [{"word": w, "count": c} for w, c in most_common]
        }
    
    def _analyze_sentence_structure(self, transcript: str) -> Dict[str, Any]:
        """Analyze sentence structure and patterns"""
        
        # Split into sentences
        sentences = re.split(r'[.!?]+', transcript)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        if not sentences:
            return {
                "total_sentences": 0,
                "avg_sentence_length": 0,
                "rating": "unknown"
            }
        
        total_sentences = len(sentences)
        sentence_lengths = [len(s.split()) for s in sentences]
        avg_sentence_length = sum(sentence_lengths) / len(sentence_lengths)
        
        # Benchmark: 15-20 words per sentence is ideal
        if avg_sentence_length < 8:
            structure_rating = "choppy"
            structure_feedback = "Sentences are quite short - try combining related ideas"
        elif avg_sentence_length <= 20:
            structure_rating = "good"
            structure_feedback = "Good sentence structure and flow"
        elif avg_sentence_length <= 30:
            structure_rating = "long"
            structure_feedback = "Sentences are quite long - consider breaking them up"
        else:
            structure_rating = "too_long"
            structure_feedback = "Sentences are too long - break into smaller chunks"
        
        return {
            "total_sentences": total_sentences,
            "avg_sentence_length": round(avg_sentence_length, 1),
            "shortest_sentence": min(sentence_lengths) if sentence_lengths else 0,
            "longest_sentence": max(sentence_lengths) if sentence_lengths else 0,
            "rating": structure_rating,
            "feedback": structure_feedback
        }
    
    def _calculate_communication_score(
        self,
        filler_analysis: Dict,
        pace_analysis: Dict,
        diversity_analysis: Dict,
        structure_analysis: Dict
    ) -> Dict[str, Any]:
        """Calculate overall communication score (0-100)"""
        
        score = 100.0
        deductions = []
        
        # Filler word penalty (up to -30 points)
        filler_pct = filler_analysis['filler_percentage']
        if filler_pct > 8:
            deduction = min(30, (filler_pct - 8) * 3)
            score -= deduction
            deductions.append(f"Filler words (-{deduction:.1f})")
        elif filler_pct > 5:
            deduction = (filler_pct - 5) * 2
            score -= deduction
            deductions.append(f"Filler words (-{deduction:.1f})")
        
        # Speaking pace penalty (up to -20 points)
        wpm = pace_analysis['words_per_minute']
        if pace_analysis['pace_rating'] in ['too_slow', 'too_fast']:
            score -= 20
            deductions.append("Speaking pace (-20)")
        elif pace_analysis['pace_rating'] in ['slightly_slow', 'slightly_fast']:
            score -= 10
            deductions.append("Speaking pace (-10)")
        
        # Vocabulary diversity bonus/penalty (up to ±15 points)
        diversity_ratio = diversity_analysis['diversity_ratio']
        if diversity_ratio >= 0.6:
            score += 10
            deductions.append("Vocabulary diversity (+10)")
        elif diversity_ratio < 0.4:
            score -= 15
            deductions.append("Vocabulary diversity (-15)")
        
        # Sentence structure penalty (up to -15 points)
        if structure_analysis['rating'] in ['choppy', 'too_long']:
            score -= 15
            deductions.append("Sentence structure (-15)")
        elif structure_analysis['rating'] == 'long':
            score -= 8
            deductions.append("Sentence structure (-8)")
        
        # Ensure score is between 0-100
        score = max(0, min(100, score))
        
        # Determine grade
        if score >= 90:
            grade = "A+"
        elif score >= 85:
            grade = "A"
        elif score >= 80:
            grade = "B+"
        elif score >= 75:
            grade = "B"
        elif score >= 70:
            grade = "C+"
        elif score >= 65:
            grade = "C"
        elif score >= 60:
            grade = "D"
        else:
            grade = "F"
        
        return {
            "score": round(score, 1),
            "grade": grade,
            "deductions": deductions,
            "rating": "excellent" if score >= 85 else "good" if score >= 70 else "fair" if score >= 60 else "needs_improvement"
        }
    
    def _empty_analysis(self) -> Dict[str, Any]:
        """Return empty analysis structure"""
        return {
            "filler_word_analysis": {
                "total_filler_words": 0,
                "total_words": 0,
                "filler_percentage": 0,
                "filler_counts": {},
                "most_used_filler": "none",
                "most_used_count": 0,
                "rating": "unknown",
                "feedback": "No transcript available",
                "filler_positions": []
            },
            "speaking_pace": {
                "words_per_minute": 0,
                "total_words": 0,
                "duration_seconds": 0,
                "pace_rating": "unknown",
                "pace_feedback": "No transcript available"
            },
            "word_diversity": {
                "total_words": 0,
                "unique_words": 0,
                "diversity_ratio": 0,
                "rating": "unknown",
                "feedback": "No transcript available",
                "most_common_words": []
            },
            "sentence_structure": {
                "total_sentences": 0,
                "avg_sentence_length": 0,
                "shortest_sentence": 0,
                "longest_sentence": 0,
                "rating": "unknown",
                "feedback": "No transcript available"
            },
            "communication_score": {
                "score": 0,
                "grade": "N/A",
                "deductions": [],
                "rating": "unknown"
            },
            "full_transcript": ""
        }

