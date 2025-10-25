-- ============================================================================
-- SUPABASE VIDEO STORAGE SETUP
-- Run this SQL in your Supabase SQL Editor
-- ============================================================================

-- 1. Create Storage Bucket for Interview Videos
-- ============================================================================
INSERT INTO storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
VALUES (
  'interview-videos',
  'interview-videos',
  false, -- Private bucket (users can only access their own videos)
  524288000, -- 500 MB file size limit
  ARRAY['video/webm', 'video/mp4', 'video/quicktime'] -- Allowed video types
)
ON CONFLICT (id) DO NOTHING;

-- 2. Storage Policies - Allow users to upload their own videos
-- ============================================================================

-- Policy: Users can upload videos to their own folder (user_id/*)
CREATE POLICY "Users can upload their own interview videos"
ON storage.objects
FOR INSERT
TO authenticated
WITH CHECK (
  bucket_id = 'interview-videos' 
  AND (storage.foldername(name))[1] = auth.uid()::text
);

-- Policy: Users can view/download their own videos
CREATE POLICY "Users can view their own interview videos"
ON storage.objects
FOR SELECT
TO authenticated
USING (
  bucket_id = 'interview-videos' 
  AND (storage.foldername(name))[1] = auth.uid()::text
);

-- Policy: Users can update their own videos
CREATE POLICY "Users can update their own interview videos"
ON storage.objects
FOR UPDATE
TO authenticated
USING (
  bucket_id = 'interview-videos' 
  AND (storage.foldername(name))[1] = auth.uid()::text
);

-- Policy: Users can delete their own videos
CREATE POLICY "Users can delete their own interview videos"
ON storage.objects
FOR DELETE
TO authenticated
USING (
  bucket_id = 'interview-videos' 
  AND (storage.foldername(name))[1] = auth.uid()::text
);

-- 3. Add video_url column to interviews table (if not exists)
-- ============================================================================
ALTER TABLE public.interviews 
ADD COLUMN IF NOT EXISTS video_url TEXT;

ALTER TABLE public.interviews 
ADD COLUMN IF NOT EXISTS video_storage_path TEXT;

ALTER TABLE public.interviews 
ADD COLUMN IF NOT EXISTS video_uploaded_at TIMESTAMPTZ;

ALTER TABLE public.interviews 
ADD COLUMN IF NOT EXISTS video_size_bytes BIGINT;

-- Add comment for documentation
COMMENT ON COLUMN public.interviews.video_url IS 'Public signed URL for accessing the interview video';
COMMENT ON COLUMN public.interviews.video_storage_path IS 'Storage path in Supabase: user_id/interview_id_timestamp.webm';
COMMENT ON COLUMN public.interviews.video_uploaded_at IS 'Timestamp when video was uploaded';
COMMENT ON COLUMN public.interviews.video_size_bytes IS 'Video file size in bytes';

-- 4. Create index for faster video lookups
-- ============================================================================
CREATE INDEX IF NOT EXISTS idx_interviews_video_storage_path 
ON public.interviews(video_storage_path) 
WHERE video_storage_path IS NOT NULL;

-- 5. Optional: Create a function to generate signed URLs (server-side)
-- ============================================================================
CREATE OR REPLACE FUNCTION public.get_interview_video_url(interview_id UUID, expires_in INT DEFAULT 3600)
RETURNS TEXT
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
  video_path TEXT;
  signed_url TEXT;
BEGIN
  -- Get the video storage path for this interview
  SELECT video_storage_path INTO video_path
  FROM public.interviews
  WHERE id = interview_id
  AND user_id = auth.uid(); -- Ensure user owns this interview
  
  IF video_path IS NULL THEN
    RETURN NULL;
  END IF;
  
  -- Generate signed URL (valid for expires_in seconds, default 1 hour)
  -- Note: This requires storage.foldername extension
  SELECT storage.presigned_url('interview-videos', video_path, expires_in)
  INTO signed_url;
  
  RETURN signed_url;
END;
$$;

-- Grant execute permission to authenticated users
GRANT EXECUTE ON FUNCTION public.get_interview_video_url TO authenticated;

-- 6. Optional: Create a trigger to clean up storage when interview is deleted
-- ============================================================================
CREATE OR REPLACE FUNCTION public.delete_interview_video()
RETURNS TRIGGER
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
BEGIN
  -- Delete the video file from storage when interview is deleted
  IF OLD.video_storage_path IS NOT NULL THEN
    PERFORM storage.delete(ARRAY['interview-videos', OLD.video_storage_path]);
  END IF;
  RETURN OLD;
END;
$$;

-- Create trigger
DROP TRIGGER IF EXISTS on_interview_deleted ON public.interviews;
CREATE TRIGGER on_interview_deleted
  BEFORE DELETE ON public.interviews
  FOR EACH ROW
  EXECUTE FUNCTION public.delete_interview_video();

-- ============================================================================
-- VERIFICATION QUERIES
-- Run these to verify everything is set up correctly
-- ============================================================================

-- Check bucket exists
SELECT * FROM storage.buckets WHERE id = 'interview-videos';

-- Check policies
SELECT * FROM pg_policies WHERE tablename = 'objects' AND schemaname = 'storage';

-- Check interview columns
SELECT column_name, data_type, is_nullable 
FROM information_schema.columns 
WHERE table_name = 'interviews' 
AND column_name IN ('video_url', 'video_storage_path', 'video_uploaded_at', 'video_size_bytes');

-- ============================================================================
-- DONE! 
-- Now your app can upload videos to Supabase Storage
-- ============================================================================

