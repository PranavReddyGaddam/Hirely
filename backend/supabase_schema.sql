-- Supabase Database Schema for Hirely
-- Run this script in your Supabase SQL editor to create all required tables

-- NOTE: On Supabase managed Postgres you cannot set app-level GUCs like app.jwt_secret.
-- Supabase Auth manages JWT secrets; use Dashboard/Secrets instead of ALTER DATABASE.
-- Enable Row Level Security (RLS) will be handled per-table below via ALTER TABLE ... ENABLE RLS.

-- Users table (profiles linked to auth.users)
CREATE TABLE IF NOT EXISTS public.users (
    id UUID REFERENCES auth.users(id) ON DELETE CASCADE PRIMARY KEY,
    email TEXT UNIQUE NOT NULL,
    full_name TEXT NOT NULL,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Enable RLS on users table
ALTER TABLE public.users ENABLE ROW LEVEL SECURITY;

-- Users can only see and modify their own data
CREATE POLICY "Users can view own profile" ON public.users
    FOR SELECT USING (auth.uid() = id);

CREATE POLICY "Users can update own profile" ON public.users
    FOR UPDATE USING (auth.uid() = id);

CREATE POLICY "Users can insert own profile" ON public.users
    FOR INSERT WITH CHECK (auth.uid() = id);

-- Interviews table
CREATE TABLE IF NOT EXISTS public.interviews (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT,
    interview_type TEXT NOT NULL CHECK (interview_type IN ('behavioral', 'technical', 'system_design', 'mock_interview', 'mixed', 'custom')),
    job_description TEXT,
    company_name TEXT,
    position_title TEXT,
    duration_minutes INTEGER DEFAULT 30,
    status TEXT NOT NULL DEFAULT 'draft' CHECK (status IN ('draft', 'active', 'completed', 'cancelled')),
    user_id UUID REFERENCES public.users(id) ON DELETE CASCADE NOT NULL,
    video_path TEXT,
    video_filename TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE
);

-- Enable RLS on interviews table
ALTER TABLE public.interviews ENABLE ROW LEVEL SECURITY;

-- Users can only see and modify their own interviews
CREATE POLICY "Users can view own interviews" ON public.interviews
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own interviews" ON public.interviews
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own interviews" ON public.interviews
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own interviews" ON public.interviews
    FOR DELETE USING (auth.uid() = user_id);

-- Questions table
CREATE TABLE IF NOT EXISTS public.questions (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    interview_id UUID REFERENCES public.interviews(id) ON DELETE CASCADE NOT NULL,
    question_text TEXT NOT NULL,
    question_type TEXT NOT NULL,
    difficulty_level TEXT DEFAULT 'medium' CHECK (difficulty_level IN ('easy', 'medium', 'hard')),
    expected_duration INTEGER DEFAULT 120,
    order_index INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Enable RLS on questions table
ALTER TABLE public.questions ENABLE ROW LEVEL SECURITY;

-- Users can only see questions for their own interviews
CREATE POLICY "Users can view questions for own interviews" ON public.questions
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM public.interviews 
            WHERE interviews.id = questions.interview_id 
            AND interviews.user_id = auth.uid()
        )
    );

CREATE POLICY "Users can insert questions for own interviews" ON public.questions
    FOR INSERT WITH CHECK (
        EXISTS (
            SELECT 1 FROM public.interviews 
            WHERE interviews.id = questions.interview_id 
            AND interviews.user_id = auth.uid()
        )
    );

CREATE POLICY "Users can update questions for own interviews" ON public.questions
    FOR UPDATE USING (
        EXISTS (
            SELECT 1 FROM public.interviews 
            WHERE interviews.id = questions.interview_id 
            AND interviews.user_id = auth.uid()
        )
    );

CREATE POLICY "Users can delete questions for own interviews" ON public.questions
    FOR DELETE USING (
        EXISTS (
            SELECT 1 FROM public.interviews 
            WHERE interviews.id = questions.interview_id 
            AND interviews.user_id = auth.uid()
        )
    );

-- Responses table
CREATE TABLE IF NOT EXISTS public.responses (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    interview_id UUID REFERENCES public.interviews(id) ON DELETE CASCADE NOT NULL,
    question_id UUID REFERENCES public.questions(id) ON DELETE CASCADE NOT NULL,
    response_text TEXT,
    audio_duration FLOAT,
    confidence_score FLOAT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Enable RLS on responses table
ALTER TABLE public.responses ENABLE ROW LEVEL SECURITY;

-- Users can only see responses for their own interviews
CREATE POLICY "Users can view responses for own interviews" ON public.responses
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM public.interviews 
            WHERE interviews.id = responses.interview_id 
            AND interviews.user_id = auth.uid()
        )
    );

CREATE POLICY "Users can insert responses for own interviews" ON public.responses
    FOR INSERT WITH CHECK (
        EXISTS (
            SELECT 1 FROM public.interviews 
            WHERE interviews.id = responses.interview_id 
            AND interviews.user_id = auth.uid()
        )
    );

CREATE POLICY "Users can update responses for own interviews" ON public.responses
    FOR UPDATE USING (
        EXISTS (
            SELECT 1 FROM public.interviews 
            WHERE interviews.id = responses.interview_id 
            AND interviews.user_id = auth.uid()
        )
    );

CREATE POLICY "Users can delete responses for own interviews" ON public.responses
    FOR DELETE USING (
        EXISTS (
            SELECT 1 FROM public.interviews 
            WHERE interviews.id = responses.interview_id 
            AND interviews.user_id = auth.uid()
        )
    );

-- Analysis table
CREATE TABLE IF NOT EXISTS public.analysis (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    interview_id UUID REFERENCES public.interviews(id) ON DELETE CASCADE NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'processing', 'completed', 'failed')),
    analysis_type TEXT DEFAULT 'comprehensive',
    include_voice_analysis BOOLEAN DEFAULT true,
    include_behavioral_analysis BOOLEAN DEFAULT true,
    custom_criteria JSONB,
    overall_score FLOAT,
    summary TEXT,
    strengths TEXT[],
    areas_for_improvement TEXT[],
    recommendations TEXT[],
    detailed_analysis JSONB,
    user_id UUID REFERENCES public.users(id) ON DELETE CASCADE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE
);

-- Enable RLS on analysis table
ALTER TABLE public.analysis ENABLE ROW LEVEL SECURITY;

-- Users can only see analysis for their own interviews
CREATE POLICY "Users can view own analysis" ON public.analysis
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own analysis" ON public.analysis
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own analysis" ON public.analysis
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own analysis" ON public.analysis
    FOR DELETE USING (auth.uid() = user_id);

-- Feedback items table
CREATE TABLE IF NOT EXISTS public.feedback_items (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    analysis_id UUID REFERENCES public.analysis(id) ON DELETE CASCADE NOT NULL,
    category TEXT NOT NULL CHECK (category IN ('communication', 'technical_skills', 'problem_solving', 'confidence', 'clarity', 'structure')),
    score FLOAT NOT NULL CHECK (score >= 0 AND score <= 1),
    feedback_text TEXT NOT NULL,
    suggestions TEXT[],
    strengths TEXT[],
    areas_for_improvement TEXT[],
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Enable RLS on feedback_items table
ALTER TABLE public.feedback_items ENABLE ROW LEVEL SECURITY;

-- Users can only see feedback for their own analysis
CREATE POLICY "Users can view feedback for own analysis" ON public.feedback_items
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM public.analysis 
            WHERE analysis.id = feedback_items.analysis_id 
            AND analysis.user_id = auth.uid()
        )
    );

CREATE POLICY "Users can insert feedback for own analysis" ON public.feedback_items
    FOR INSERT WITH CHECK (
        EXISTS (
            SELECT 1 FROM public.analysis 
            WHERE analysis.id = feedback_items.analysis_id 
            AND analysis.user_id = auth.uid()
        )
    );

CREATE POLICY "Users can update feedback for own analysis" ON public.feedback_items
    FOR UPDATE USING (
        EXISTS (
            SELECT 1 FROM public.analysis 
            WHERE analysis.id = feedback_items.analysis_id 
            AND analysis.user_id = auth.uid()
        )
    );

CREATE POLICY "Users can delete feedback for own analysis" ON public.feedback_items
    FOR DELETE USING (
        EXISTS (
            SELECT 1 FROM public.analysis 
            WHERE analysis.id = feedback_items.analysis_id 
            AND analysis.user_id = auth.uid()
        )
    );

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_interviews_user_id ON public.interviews(user_id);
CREATE INDEX IF NOT EXISTS idx_interviews_status ON public.interviews(status);
CREATE INDEX IF NOT EXISTS idx_questions_interview_id ON public.questions(interview_id);
CREATE INDEX IF NOT EXISTS idx_responses_interview_id ON public.responses(interview_id);
CREATE INDEX IF NOT EXISTS idx_responses_question_id ON public.responses(question_id);
CREATE INDEX IF NOT EXISTS idx_analysis_interview_id ON public.analysis(interview_id);
CREATE INDEX IF NOT EXISTS idx_analysis_user_id ON public.analysis(user_id);
CREATE INDEX IF NOT EXISTS idx_analysis_status ON public.analysis(status);
CREATE INDEX IF NOT EXISTS idx_feedback_items_analysis_id ON public.feedback_items(analysis_id);

-- Create updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Add updated_at triggers
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON public.users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_interviews_updated_at BEFORE UPDATE ON public.interviews
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Create function to handle new user registration
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO public.users (id, email, full_name)
    VALUES (
        NEW.id,
        NEW.email,
        COALESCE(NEW.raw_user_meta_data->>'full_name', NEW.email)
    );
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Create trigger for new user registration
DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
CREATE TRIGGER on_auth_user_created
    AFTER INSERT ON auth.users
    FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();

-- Grant necessary permissions
GRANT USAGE ON SCHEMA public TO anon, authenticated;
GRANT ALL ON ALL TABLES IN SCHEMA public TO anon, authenticated;
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO anon, authenticated;
GRANT ALL ON ALL FUNCTIONS IN SCHEMA public TO anon, authenticated;
