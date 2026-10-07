-- ═══════════════════════════════════════════════════════════════════════
-- AI-Powered Fitness Coach — Initial Database Schema
-- ═══════════════════════════════════════════════════════════════════════
-- Run this migration against your Supabase project:
--   1. Go to Supabase Dashboard → SQL Editor
--   2. Paste this entire file
--   3. Click "Run"
--
-- Or via CLI:
--   supabase db push
-- ═══════════════════════════════════════════════════════════════════════

-- ── Extensions ────────────────────────────────────────────────────────
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ═══════════════════════════════════════════════════════════════════════
-- 1. PROFILES TABLE
-- ═══════════════════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS public.profiles (
    id          UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    full_name   TEXT,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE public.profiles IS 'User profile data, linked 1:1 with auth.users';

-- ═══════════════════════════════════════════════════════════════════════
-- 2. VIDEOS TABLE
-- ═══════════════════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS public.videos (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    filename        TEXT NOT NULL,
    storage_path    TEXT NOT NULL,
    mime_type       TEXT,
    file_size       BIGINT,
    duration_seconds DOUBLE PRECISION,
    fps             DOUBLE PRECISION,
    width           INTEGER,
    height          INTEGER,
    status          TEXT NOT NULL DEFAULT 'UPLOADED'
                    CHECK (status IN ('UPLOADED', 'PROCESSING', 'COMPLETED', 'FAILED', 'DELETED')),
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE public.videos IS 'Uploaded exercise video metadata';

-- ═══════════════════════════════════════════════════════════════════════
-- 3. ANALYSES TABLE
-- ═══════════════════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS public.analyses (
    id                      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    video_id                UUID NOT NULL REFERENCES public.videos(id) ON DELETE CASCADE,
    user_id                 UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    exercise                TEXT CHECK (exercise IN ('squat', 'push_up', 'bicep_curl', 'shoulder_press')),
    confidence              DOUBLE PRECISION,
    total_reps              INTEGER DEFAULT 0,
    correct_reps            INTEGER DEFAULT 0,
    incorrect_reps          INTEGER DEFAULT 0,
    form_accuracy           DOUBLE PRECISION,
    range_of_motion         DOUBLE PRECISION,
    movement_consistency    DOUBLE PRECISION,
    overall_score           DOUBLE PRECISION,
    status                  TEXT NOT NULL DEFAULT 'QUEUED'
                            CHECK (status IN (
                                'QUEUED', 'VALIDATING', 'EXTRACTING_FRAMES',
                                'POSE_ESTIMATION', 'FEATURE_EXTRACTION',
                                'EXERCISE_RECOGNITION', 'TEMPORAL_ANALYSIS',
                                'FORM_ANALYSIS', 'REP_COUNTING', 'SCORING',
                                'REPORT_GENERATION', 'COMPLETED', 'FAILED'
                            )),
    error_message           TEXT,
    model_metadata          JSONB,
    created_at              TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    completed_at            TIMESTAMPTZ,
    updated_at              TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE public.analyses IS 'Exercise analysis results and progress tracking';

-- ═══════════════════════════════════════════════════════════════════════
-- 4. FORM ERRORS TABLE
-- ═══════════════════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS public.form_errors (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    analysis_id         UUID NOT NULL REFERENCES public.analyses(id) ON DELETE CASCADE,
    error_type          TEXT NOT NULL,
    severity            TEXT CHECK (severity IN ('LOW', 'MEDIUM', 'HIGH')),
    rep_number          INTEGER,
    timestamp_seconds   DOUBLE PRECISION,
    description         TEXT,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE public.form_errors IS 'Detected exercise form errors per analysis';

-- ═══════════════════════════════════════════════════════════════════════
-- 5. ANALYSIS METRICS TABLE
-- ═══════════════════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS public.analysis_metrics (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    analysis_id     UUID NOT NULL REFERENCES public.analyses(id) ON DELETE CASCADE,
    metric_name     TEXT NOT NULL,
    metric_value    DOUBLE PRECISION NOT NULL,
    unit            TEXT,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE public.analysis_metrics IS 'Detailed metrics per analysis (angles, distances, etc.)';

-- ═══════════════════════════════════════════════════════════════════════
-- 6. MODEL VERSIONS TABLE
-- ═══════════════════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS public.model_versions (
    id                      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    model_name              TEXT NOT NULL,
    model_type              TEXT NOT NULL,
    version                 TEXT NOT NULL,
    training_dataset        TEXT,
    feature_schema_version  TEXT,
    metrics                 JSONB,
    artifact_path           TEXT,
    status                  TEXT CHECK (status IN ('TRAINING', 'ACTIVE', 'DEPRECATED', 'FAILED')),
    created_at              TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (model_name, version)
);

COMMENT ON TABLE public.model_versions IS 'ML model version tracking and metadata';

-- ═══════════════════════════════════════════════════════════════════════
-- INDEXES
-- ═══════════════════════════════════════════════════════════════════════

-- Videos
CREATE INDEX IF NOT EXISTS idx_videos_user_id    ON public.videos(user_id);
CREATE INDEX IF NOT EXISTS idx_videos_created_at ON public.videos(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_videos_status     ON public.videos(status);

-- Analyses
CREATE INDEX IF NOT EXISTS idx_analyses_user_id    ON public.analyses(user_id);
CREATE INDEX IF NOT EXISTS idx_analyses_video_id   ON public.analyses(video_id);
CREATE INDEX IF NOT EXISTS idx_analyses_created_at ON public.analyses(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_analyses_status     ON public.analyses(status);

-- Form errors
CREATE INDEX IF NOT EXISTS idx_form_errors_analysis_id ON public.form_errors(analysis_id);

-- Analysis metrics
CREATE INDEX IF NOT EXISTS idx_analysis_metrics_analysis_id ON public.analysis_metrics(analysis_id);

-- Model versions
CREATE INDEX IF NOT EXISTS idx_model_versions_name_version ON public.model_versions(model_name, version);

-- ═══════════════════════════════════════════════════════════════════════
-- UPDATED_AT TRIGGER FUNCTION
-- ═══════════════════════════════════════════════════════════════════════

CREATE OR REPLACE FUNCTION public.handle_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply updated_at trigger to relevant tables
CREATE TRIGGER set_profiles_updated_at
    BEFORE UPDATE ON public.profiles
    FOR EACH ROW EXECUTE FUNCTION public.handle_updated_at();

CREATE TRIGGER set_videos_updated_at
    BEFORE UPDATE ON public.videos
    FOR EACH ROW EXECUTE FUNCTION public.handle_updated_at();

CREATE TRIGGER set_analyses_updated_at
    BEFORE UPDATE ON public.analyses
    FOR EACH ROW EXECUTE FUNCTION public.handle_updated_at();

-- ═══════════════════════════════════════════════════════════════════════
-- AUTO-CREATE PROFILE ON SIGNUP
-- ═══════════════════════════════════════════════════════════════════════

CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO public.profiles (id, full_name)
    VALUES (
        NEW.id,
        COALESCE(NEW.raw_user_meta_data->>'full_name', '')
    );
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Trigger on auth.users insert
CREATE TRIGGER on_auth_user_created
    AFTER INSERT ON auth.users
    FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();

-- ═══════════════════════════════════════════════════════════════════════
-- ROW LEVEL SECURITY
-- ═══════════════════════════════════════════════════════════════════════

-- Enable RLS on all user-sensitive tables
ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.videos ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.analyses ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.form_errors ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.analysis_metrics ENABLE ROW LEVEL SECURITY;

-- ── Profiles Policies ─────────────────────────────────────────────────
CREATE POLICY "Users can view own profile"
    ON public.profiles FOR SELECT
    USING (auth.uid() = id);

CREATE POLICY "Users can update own profile"
    ON public.profiles FOR UPDATE
    USING (auth.uid() = id)
    WITH CHECK (auth.uid() = id);

CREATE POLICY "Users can insert own profile"
    ON public.profiles FOR INSERT
    WITH CHECK (auth.uid() = id);

-- ── Videos Policies ───────────────────────────────────────────────────
CREATE POLICY "Users can view own videos"
    ON public.videos FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own videos"
    ON public.videos FOR INSERT
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own videos"
    ON public.videos FOR UPDATE
    USING (auth.uid() = user_id)
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can delete own videos"
    ON public.videos FOR DELETE
    USING (auth.uid() = user_id);

-- ── Analyses Policies ─────────────────────────────────────────────────
CREATE POLICY "Users can view own analyses"
    ON public.analyses FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own analyses"
    ON public.analyses FOR INSERT
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own analyses"
    ON public.analyses FOR UPDATE
    USING (auth.uid() = user_id)
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can delete own analyses"
    ON public.analyses FOR DELETE
    USING (auth.uid() = user_id);

-- ── Form Errors Policies ──────────────────────────────────────────────
CREATE POLICY "Users can view own form errors"
    ON public.form_errors FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM public.analyses
            WHERE analyses.id = form_errors.analysis_id
            AND analyses.user_id = auth.uid()
        )
    );

CREATE POLICY "Users can insert own form errors"
    ON public.form_errors FOR INSERT
    WITH CHECK (
        EXISTS (
            SELECT 1 FROM public.analyses
            WHERE analyses.id = form_errors.analysis_id
            AND analyses.user_id = auth.uid()
        )
    );

CREATE POLICY "Users can delete own form errors"
    ON public.form_errors FOR DELETE
    USING (
        EXISTS (
            SELECT 1 FROM public.analyses
            WHERE analyses.id = form_errors.analysis_id
            AND analyses.user_id = auth.uid()
        )
    );

-- ── Analysis Metrics Policies ─────────────────────────────────────────
CREATE POLICY "Users can view own analysis metrics"
    ON public.analysis_metrics FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM public.analyses
            WHERE analyses.id = analysis_metrics.analysis_id
            AND analyses.user_id = auth.uid()
        )
    );

CREATE POLICY "Users can insert own analysis metrics"
    ON public.analysis_metrics FOR INSERT
    WITH CHECK (
        EXISTS (
            SELECT 1 FROM public.analyses
            WHERE analyses.id = analysis_metrics.analysis_id
            AND analyses.user_id = auth.uid()
        )
    );

CREATE POLICY "Users can delete own analysis metrics"
    ON public.analysis_metrics FOR DELETE
    USING (
        EXISTS (
            SELECT 1 FROM public.analyses
            WHERE analyses.id = analysis_metrics.analysis_id
            AND analyses.user_id = auth.uid()
        )
    );

-- ── Service Role Bypass (for Celery worker backend) ───────────────────
-- The service role key bypasses RLS by default in Supabase.
-- This allows the Celery worker to update analysis results.
-- No additional policy needed for service_role.

-- ═══════════════════════════════════════════════════════════════════════
-- SUPABASE STORAGE CONFIGURATION
-- ═══════════════════════════════════════════════════════════════════════
-- NOTE: Storage buckets and policies must be created via SQL or Dashboard.
-- The following creates private buckets with user-scoped access.

-- Create private buckets
INSERT INTO storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
VALUES
    ('exercise-videos', 'exercise-videos', false, 524288000, -- 500MB
     ARRAY['video/mp4', 'video/quicktime', 'video/x-msvideo', 'video/x-matroska', 'video/webm']),
    ('analysis-reports', 'analysis-reports', false, 52428800, -- 50MB
     ARRAY['application/pdf'])
ON CONFLICT (id) DO NOTHING;

-- ── Storage Policies: exercise-videos ─────────────────────────────────

-- Users can upload to their own folder
CREATE POLICY "Users can upload exercise videos"
    ON storage.objects FOR INSERT
    WITH CHECK (
        bucket_id = 'exercise-videos'
        AND auth.uid()::text = (storage.foldername(name))[1]
    );

-- Users can view their own videos
CREATE POLICY "Users can view own exercise videos"
    ON storage.objects FOR SELECT
    USING (
        bucket_id = 'exercise-videos'
        AND auth.uid()::text = (storage.foldername(name))[1]
    );

-- Users can delete their own videos
CREATE POLICY "Users can delete own exercise videos"
    ON storage.objects FOR DELETE
    USING (
        bucket_id = 'exercise-videos'
        AND auth.uid()::text = (storage.foldername(name))[1]
    );

-- ── Storage Policies: analysis-reports ────────────────────────────────

-- Users can view their own reports
CREATE POLICY "Users can view own analysis reports"
    ON storage.objects FOR SELECT
    USING (
        bucket_id = 'analysis-reports'
        AND auth.uid()::text = (storage.foldername(name))[1]
    );

-- Service role inserts reports (no user INSERT policy needed)
-- The backend uses service_role key which bypasses RLS.

-- ═══════════════════════════════════════════════════════════════════════
-- DONE
-- ═══════════════════════════════════════════════════════════════════════
