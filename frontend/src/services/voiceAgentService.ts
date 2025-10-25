/**
 * Service for managing voice agents in interview sessions
 * Handles agent creation with interview-specific configurations
 */

export interface InterviewVoiceAgent {
  agentId: string;
  agentName: string;
  role: 'interviewer' | 'evaluator' | 'coach';
  interviewType: 'technical' | 'behavioral' | 'system_design' | 'mixed';
  isActive: boolean;
}

export interface VoiceAgentConfig {
  interviewId: string;
  questionId?: string;
  interviewType: string;
  role: 'interviewer' | 'evaluator' | 'coach';
  enhancedNoiseReduction?: boolean;
  candidateData?: any;
}

class VoiceAgentService {
  private baseUrl = '/api/v1/elevenlabs';

  /**
   * Create a voice agent for interview sessions with enhanced noise reduction
   */
  async createInterviewAgent(config: VoiceAgentConfig): Promise<InterviewVoiceAgent> {
    try {
      const token = localStorage.getItem('hirely_token');
      if (!token) {
        throw new Error('Authentication required');
      }

      // Create agent persona based on interview type and role
      const persona = this.createInterviewPersona(config);
      
      const response = await fetch(`${this.baseUrl}/create-agent`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          persona,
          startup_idea: null, // Not applicable for interviews
          previous_analysis: null, // Not applicable for interviews
          interview_config: {
            interview_id: config.interviewId,
            question_id: config.questionId,
            interview_type: config.interviewType,
            role: config.role,
            enhanced_noise_reduction: config.enhancedNoiseReduction ?? true,
            candidate_data: config.candidateData // Pass real interview data
          }
        })
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to create voice agent');
      }

      const data = await response.json();
      
      return {
        agentId: data.agent_id,
        agentName: data.persona_name,
        role: config.role,
        interviewType: config.interviewType as any,
        isActive: false
      };

    } catch (error) {
      console.error('Error creating interview voice agent:', error);
      throw error;
    }
  }

  /**
   * Create persona configuration based on interview type and role
   */
  private createInterviewPersona(config: VoiceAgentConfig) {
    const basePersona = {
      id: `interview-${config.role}-${Date.now()}`,
      location: 'San Francisco, CA',
      bio: '',
      expertise: [] as string[],
      experience: '10+ years',
      industry: 'Technology',
      insights: [] as string[]
    };

    switch (config.role) {
      case 'interviewer':
        return {
          ...basePersona,
          name: this.getInterviewerName(config.interviewType),
          title: this.getInterviewerTitle(config.interviewType),
          bio: this.getInterviewerBio(config.interviewType),
          expertise: this.getInterviewerExpertise(config.interviewType),
          insights: this.getInterviewerInsights(config.interviewType)
        };

      case 'evaluator':
        return {
          ...basePersona,
          name: 'Dr. Sarah Martinez',
          title: 'Senior Technical Evaluator',
          bio: 'Experienced technical evaluator with 10+ years assessing engineering talent at top tech companies. Specializes in comprehensive technical interviews and candidate evaluation.',
          expertise: ['Technical Assessment', 'Code Review', 'System Design Evaluation', 'Problem Solving Analysis'],
          insights: [
            'Focus on problem-solving approach over perfect solutions',
            'Communication skills are as important as technical skills',
            'Ask clarifying questions before jumping into solutions'
          ]
        };

      case 'coach':
        return {
          ...basePersona,
          name: 'Alex Chen',
          title: 'Interview Coach',
          bio: 'Professional interview coach who has helped 500+ candidates land jobs at top tech companies. Expert in interview preparation and performance optimization.',
          expertise: ['Interview Preparation', 'Communication Skills', 'Technical Coaching', 'Confidence Building'],
          insights: [
            'Practice explaining your thought process out loud',
            'Structure your answers with clear examples',
            'Stay calm and think through problems systematically'
          ]
        };

      default:
        return {
          ...basePersona,
          name: 'Interview Assistant',
          title: 'AI Interview Assistant',
          bio: 'AI-powered interview assistant designed to help you practice and improve your interview skills.',
          expertise: ['Interview Practice', 'Technical Questions', 'Communication'],
          insights: ['Practice makes perfect', 'Be clear and concise', 'Ask questions when needed']
        };
    }
  }

  private getInterviewerName(interviewType: string): string {
    const names = {
      technical: 'Michael Rodriguez',
      behavioral: 'Jennifer Kim',
      system_design: 'David Park',
      mixed: 'Sarah Johnson'
    };
    return names[interviewType as keyof typeof names] || 'Interview Assistant';
  }

  private getInterviewerTitle(interviewType: string): string {
    const titles = {
      technical: 'Senior Software Engineer',
      behavioral: 'Engineering Manager',
      system_design: 'Principal Architect',
      mixed: 'Senior Technical Interviewer'
    };
    return titles[interviewType as keyof typeof titles] || 'Technical Interviewer';
  }

  private getInterviewerBio(interviewType: string): string {
    const bios = {
      technical: 'Senior software engineer with 8+ years of experience conducting technical interviews. Expert in algorithms, data structures, and coding best practices.',
      behavioral: 'Engineering manager with 10+ years of experience leading teams and conducting behavioral interviews. Focuses on leadership, communication, and cultural fit.',
      system_design: 'Principal architect with 12+ years of experience designing large-scale systems. Expert in distributed systems, scalability, and system architecture.',
      mixed: 'Senior technical interviewer with 9+ years of experience across all interview types. Balances technical depth with behavioral assessment.'
    };
    return bios[interviewType as keyof typeof bios] || 'Experienced technical interviewer';
  }

  private getInterviewerExpertise(interviewType: string): string[] {
    const expertise = {
      technical: ['Algorithms', 'Data Structures', 'Coding', 'Problem Solving', 'Code Review'],
      behavioral: ['Leadership', 'Communication', 'Team Management', 'Conflict Resolution', 'Cultural Fit'],
      system_design: ['System Architecture', 'Scalability', 'Distributed Systems', 'Database Design', 'Performance Optimization'],
      mixed: ['Technical Assessment', 'Behavioral Evaluation', 'System Design', 'Problem Solving', 'Communication']
    };
    return expertise[interviewType as keyof typeof expertise] || ['Technical Interviewing'];
  }

  private getInterviewerInsights(interviewType: string): string[] {
    const insights = {
      technical: [
        'Think out loud and explain your approach',
        'Start with a brute force solution, then optimize',
        'Consider edge cases and test your solution'
      ],
      behavioral: [
        'Use the STAR method: Situation, Task, Action, Result',
        'Be specific with examples from your experience',
        'Show both successes and learning from failures'
      ],
      system_design: [
        'Start with requirements and constraints',
        'Design high-level architecture first',
        'Consider scalability, reliability, and performance'
      ],
      mixed: [
        'Balance technical depth with clear communication',
        'Ask clarifying questions when needed',
        'Show your problem-solving process'
      ]
    };
    return insights[interviewType as keyof typeof insights] || ['Be clear and thorough'];
  }

  /**
   * Delete a voice agent
   */
  async deleteAgent(agentId: string): Promise<void> {
    try {
      const token = localStorage.getItem('hirely_token');
      if (!token) {
        throw new Error('Authentication required');
      }

      const response = await fetch(`${this.baseUrl}/agent/${agentId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to delete agent');
      }

    } catch (error) {
      console.error('Error deleting voice agent:', error);
      throw error;
    }
  }
}

export const voiceAgentService = new VoiceAgentService();
