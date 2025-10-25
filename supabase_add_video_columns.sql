-- ============================================================================
-- ADD VIDEO COLUMNS TO INTERVIEWS TABLE
-- Run this SQL in your Supabase SQL Editor
-- ============================================================================

-- Add video storage columns to interviews table (if they don't exist)
-- ============================================================================

ALTER TABLE public.interviews 
ADD COLUMN IF NOT EXISTS video_storage_path TEXT;

ALTER TABLE public.interviews 
ADD COLUMN IF NOT EXISTS video_url TEXT;

ALTER TABLE public.interviews 
ADD COLUMN IF NOT EXISTS video_uploaded_at TIMESTAMP WITH TIME ZONE;

ALTER TABLE public.interviews 
ADD COLUMN IF NOT EXISTS video_size_bytes BIGINT;

-- Add comments for documentation
COMMENT ON COLUMN public.interviews.video_storage_path IS 'Storage path in S3/Supabase: user_id/interview_id_timestamp.webm';
COMMENT ON COLUMN public.interviews.video_url IS 'Public/signed URL for accessing the interview video';
COMMENT ON COLUMN public.interviews.video_uploaded_at IS 'Timestamp when video was uploaded';
COMMENT ON COLUMN public.interviews.video_size_bytes IS 'Video file size in bytes';

-- Create index for faster video lookups
CREATE INDEX IF NOT EXISTS idx_interviews_video_storage_path 
ON public.interviews(video_storage_path) 
WHERE video_storage_path IS NOT NULL;

-- ============================================================================
-- VERIFICATION
-- Run this to verify columns were added
-- ============================================================================

SELECT column_name, data_type, is_nullable 
FROM information_schema.columns 
WHERE table_name = 'interviews' 
AND column_name IN ('video_storage_path', 'video_url', 'video_uploaded_at', 'video_size_bytes');

-- ============================================================================
-- DONE!
-- ============================================================================
