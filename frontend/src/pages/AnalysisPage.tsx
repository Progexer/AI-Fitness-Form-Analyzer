import React, { useEffect, useState } from 'react';
import { AnalysisResult, AnalysisProgress } from '../types';
import { api } from '../services/api';
import { LiveAnalysisOverlay } from '../components/LiveAnalysisOverlay';
import { RadarChart } from '../components/RadarChart';
import { RepCard } from '../components/RepCard';
import {
  Download,
  ArrowLeft,
  Sparkles,
  CheckCircle2,
  AlertTriangle,
  Flame,
  Award,
  BookOpen,
  Share2
} from 'lucide-react';

interface AnalysisPageProps {
  analysisId: string;
  onBack: () => void;
}

export const AnalysisPage: React.FC<AnalysisPageProps> = ({ analysisId, onBack }) => {
  const [analysis, setAnalysis] = useState<AnalysisResult | null>(null);
  const [progress, setProgress] = useState<AnalysisProgress | null>(null);
  const [loading, setLoading] = useState(true);
  const [downloading, setDownloading] = useState(false);

  useEffect(() => {
    let unsubscribeSSE: (() => void) | null = null;

    const checkAndSubscribe = async () => {
      try {
        // First try fetching directly
        const res = await api.getAnalysisResult(analysisId);
        setAnalysis(res);
        setLoading(false);
      } catch (err) {
        // If still processing or not found yet, subscribe to live SSE stream
        unsubscribeSSE = api.subscribeAnalysisProgress(
          analysisId,
          (prog) => {
            setProgress(prog);
            if (prog.result) {
              setAnalysis(prog.result);
            }
          },
          (finalRes) => {
            setAnalysis(finalRes);
            setProgress(null);
            setLoading(false);
          },
          (error) => {
            console.error('SSE Error:', error);
            setLoading(false);
          }
        );
      }
    };

    checkAndSubscribe();

    return () => {
      if (unsubscribeSSE) unsubscribeSSE();
    };
  }, [analysisId]);

  const handleDownloadPdf = async () => {
    if (!analysis) return;
    setDownloading(true);
    try {
      await api.downloadPdfReport(analysis.id, `AI_Coach_${analysis.exercise}_${analysis.id.slice(0, 8)}.pdf`);
    } catch (e) {
      console.error('PDF download error:', e);
    } finally {
      setDownloading(false);
    }
  };

  const getScoreColor = (score: number) => {
    if (score >= 85) return '#10b981';
    if (score >= 70) return '#f59e0b';
    return '#ef4444';
  };

  // If live processing in progress
  if (progress && progress.status === 'processing') {
    return (
      <div style={{ padding: '32px 36px', maxWidth: '1000px', margin: '0 auto' }}>
        <button
          className="btn-secondary"
          onClick={onBack}
          style={{ marginBottom: '24px', padding: '8px 14px' }}
        >
          <ArrowLeft size={16} />
          <span>Back to Dashboard</span>
        </button>

        <LiveAnalysisOverlay progress={progress} />
      </div>
    );
  }

  if (loading && !analysis) {
    return (
      <div style={{ padding: '80px 20px', textAlign: 'center' }}>
        <div className="animate-spin" style={{ display: 'inline-flex', marginBottom: '16px' }}>
          <Sparkles size={36} color="#10b981" />
        </div>
        <h2 style={{ fontSize: '1.25rem', color: '#fff', marginBottom: '8px' }}>
          Loading Biomechanical Telemetry...
        </h2>
        <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>
          Synchronizing pose landmarks and model scoring
        </p>
      </div>
    );
  }

  if (!analysis) {
    return (
      <div style={{ padding: '80px 20px', textAlign: 'center' }}>
        <p style={{ color: 'var(--text-secondary)' }}>Analysis record not found.</p>
        <button className="btn-secondary" onClick={onBack} style={{ marginTop: '16px' }}>
          Back to Dashboard
        </button>
      </div>
    );
  }

  const feedback = analysis.coaching_feedback;
  const mb = analysis.metrics_breakdown;
  const breakdown = {
    form_accuracy: mb?.form_accuracy ?? 85,
    range_of_motion: mb?.range_of_motion ?? 78,
    tempo_smoothness: mb?.tempo_smoothness ?? 82,
    bilateral_symmetry: mb?.bilateral_symmetry ?? 88,
    movement_consistency: mb?.movement_consistency ?? 82,
    rep_completion: mb?.rep_completion ?? 80,
  };

  return (
    <div style={{ padding: '32px 36px', maxWidth: '1300px', margin: '0 auto' }}>
      {/* Top Header & Actions */}
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          marginBottom: '28px',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
          <button
            className="btn-secondary"
            onClick={onBack}
            style={{ padding: '10px 14px' }}
          >
            <ArrowLeft size={16} />
          </button>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
              <h1 style={{ fontSize: '1.8rem', fontWeight: 800, color: '#fff', textTransform: 'capitalize' }}>
                {analysis.exercise.replace('_', ' ')} Evaluation
              </h1>
              <span className="badge badge-emerald">
                Grade: {analysis.grade}
              </span>
              <span className="badge badge-cyan" style={{ textTransform: 'none' }}>
                Model: {analysis.model_used}
              </span>
            </div>
            <p style={{ fontSize: '0.82rem', color: 'var(--text-muted)', marginTop: '2px' }}>
              Session ID: {analysis.id} • Processed in {analysis.processing_time_sec}s
            </p>
          </div>
        </div>

        <button
          className="btn-primary"
          onClick={handleDownloadPdf}
          disabled={downloading}
          style={{ padding: '10px 18px' }}
        >
          <Download size={16} />
          <span>{downloading ? 'Generating PDF...' : 'Download Official PDF Report'}</span>
        </button>
      </div>

      {/* Main Score & Radar Hero Grid */}
      <div
        style={{
          display: 'grid',
          gridTemplateColumns: '1.1fr 1.3fr 1fr',
          gap: '24px',
          marginBottom: '28px',
        }}
      >
        {/* Overall Score Card */}
        <div
          className="glass-card"
          style={{
            padding: '28px',
            display: 'flex',
            flexDirection: 'column',
            justifyContent: 'space-between',
          }}
        >
          <div>
            <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)', textTransform: 'uppercase', fontWeight: 600 }}>
              Composite Form Score
            </span>
            <div
              style={{
                fontSize: '3.6rem',
                fontWeight: 800,
                color: getScoreColor(analysis.overall_score),
                fontFamily: 'var(--font-mono)',
                lineHeight: 1.1,
                marginTop: '8px',
              }}
            >
              {analysis.overall_score}
              <span style={{ fontSize: '1.4rem', color: 'var(--text-muted)', fontWeight: 500 }}>/100</span>
            </div>
            <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginTop: '8px' }}>
              {analysis.overall_score >= 85
                ? 'Optimal biomechanical posture with high mechanical efficiency.'
                : 'Minor deviations detected. Review recommended corrective drills.'}
            </div>
          </div>

          <div
            style={{
              paddingTop: '20px',
              borderTop: '1px solid var(--border-subtle)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
            }}
          >
            <div>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Verified Reps</div>
              <div style={{ fontSize: '1.4rem', fontWeight: 800, color: '#fff', fontFamily: 'var(--font-mono)' }}>
                {analysis.total_reps}
              </div>
            </div>
            <div>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Letter Grade</div>
              <div style={{ fontSize: '1.4rem', fontWeight: 800, color: '#10b981', fontFamily: 'var(--font-mono)' }}>
                {analysis.grade}
              </div>
            </div>
            <div>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Fault Rate</div>
              <div style={{ fontSize: '1.4rem', fontWeight: 800, color: '#f59e0b', fontFamily: 'var(--font-mono)' }}>
                {analysis.reps.reduce((acc, r) => acc + (r.form_errors?.length || 0), 0)}
              </div>
            </div>
          </div>
        </div>

        {/* 4 Biomechanical Domain Sliders */}
        <div className="glass-card" style={{ padding: '24px' }}>
          <h3 style={{ fontSize: '1.05rem', fontWeight: 700, color: '#fff', marginBottom: '18px' }}>
            Biomechanical Quality Domains
          </h3>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.82rem', marginBottom: '6px' }}>
                <span style={{ color: '#fff', fontWeight: 600 }}>Form Accuracy (35% weight)</span>
                <span style={{ color: '#34d399', fontFamily: 'var(--font-mono)' }}>{breakdown.form_accuracy}%</span>
              </div>
              <div style={{ height: '6px', width: '100%', background: 'rgba(255, 255, 255, 0.08)', borderRadius: '9999px', overflow: 'hidden' }}>
                <div style={{ height: '100%', width: `${breakdown.form_accuracy}%`, background: '#10b981', borderRadius: '9999px' }} />
              </div>
            </div>

            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.82rem', marginBottom: '6px' }}>
                <span style={{ color: '#fff', fontWeight: 600 }}>Range of Motion (25% weight)</span>
                <span style={{ color: '#38bdf8', fontFamily: 'var(--font-mono)' }}>{breakdown.range_of_motion}%</span>
              </div>
              <div style={{ height: '6px', width: '100%', background: 'rgba(255, 255, 255, 0.08)', borderRadius: '9999px', overflow: 'hidden' }}>
                <div style={{ height: '100%', width: `${breakdown.range_of_motion}%`, background: '#06b6d4', borderRadius: '9999px' }} />
              </div>
            </div>

            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.82rem', marginBottom: '6px' }}>
                <span style={{ color: '#fff', fontWeight: 600 }}>Movement Consistency (20% weight)</span>
                <span style={{ color: '#fbbf24', fontFamily: 'var(--font-mono)' }}>{breakdown.movement_consistency}%</span>
              </div>
              <div style={{ height: '6px', width: '100%', background: 'rgba(255, 255, 255, 0.08)', borderRadius: '9999px', overflow: 'hidden' }}>
                <div style={{ height: '100%', width: `${breakdown.movement_consistency}%`, background: '#f59e0b', borderRadius: '9999px' }} />
              </div>
            </div>

            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.82rem', marginBottom: '6px' }}>
                <span style={{ color: '#fff', fontWeight: 600 }}>Rep Completion (20% weight)</span>
                <span style={{ color: '#a78bfa', fontFamily: 'var(--font-mono)' }}>{breakdown.rep_completion}%</span>
              </div>
              <div style={{ height: '6px', width: '100%', background: 'rgba(255, 255, 255, 0.08)', borderRadius: '9999px', overflow: 'hidden' }}>
                <div style={{ height: '100%', width: `${breakdown.rep_completion}%`, background: '#8b5cf6', borderRadius: '9999px' }} />
              </div>
            </div>
          </div>
        </div>

        {/* SVG Radar Chart */}
        <div className="glass-card" style={{ padding: '20px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
          <RadarChart metrics={breakdown} size={250} />
        </div>
      </div>

      {/* AI Coaching Insights & Corrective Drills Section */}
      {feedback && (
        <div
          style={{
            display: 'grid',
            gridTemplateColumns: '1.2fr 1fr',
            gap: '24px',
            marginBottom: '28px',
          }}
        >
          {/* Coaching Summary & Strengths */}
          <div className="glass-card" style={{ padding: '24px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '14px' }}>
              <Sparkles size={20} color="#10b981" />
              <h3 style={{ fontSize: '1.05rem', fontWeight: 700, color: '#fff' }}>
                AI Biomechanical Diagnosis
              </h3>
            </div>

            <p style={{ fontSize: '0.9rem', color: 'var(--text-secondary)', lineHeight: 1.6, marginBottom: '18px' }}>
              {feedback.summary}
            </p>

            <h4 style={{ fontSize: '0.82rem', textTransform: 'uppercase', color: 'var(--text-muted)', marginBottom: '10px', fontWeight: 700 }}>
              Observed Strengths
            </h4>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
              {feedback.strengths?.map((str, i) => (
                <div key={i} style={{ display: 'flex', alignItems: 'flex-start', gap: '10px' }}>
                  <CheckCircle2 size={16} color="#10b981" style={{ marginTop: '2px', flexShrink: 0 }} />
                  <span style={{ fontSize: '0.85rem', color: '#fff' }}>{str}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Corrective Drills */}
          <div className="glass-card" style={{ padding: '24px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '14px' }}>
              <BookOpen size={20} color="#06b6d4" />
              <h3 style={{ fontSize: '1.05rem', fontWeight: 700, color: '#fff' }}>
                Targeted Corrective Drills
              </h3>
            </div>

            {feedback.recommended_drills && feedback.recommended_drills.length > 0 ? (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                {feedback.recommended_drills.map((drill, i) => (
                  <div
                    key={i}
                    style={{
                      padding: '12px 14px',
                      borderRadius: 'var(--radius-md)',
                      background: 'rgba(255, 255, 255, 0.03)',
                      border: '1px solid var(--border-subtle)',
                    }}
                  >
                    <div style={{ fontSize: '0.88rem', fontWeight: 600, color: '#38bdf8', marginBottom: '4px' }}>
                      {drill.drill}
                    </div>
                    <div style={{ fontSize: '0.78rem', color: 'var(--text-secondary)', lineHeight: 1.4 }}>
                      {drill.description}
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>
                No significant biomechanical breakdown detected. Keep progressing load and volume!
              </p>
            )}
          </div>
        </div>
      )}

      {/* Rep-by-Rep Breakdown Section */}
      <div>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '16px' }}>
          <h3 style={{ fontSize: '1.15rem', fontWeight: 700, color: '#fff' }}>
            Repetition Telemetry Breakdown ({analysis.reps?.length || 0} Reps)
          </h3>
          <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
            Inflections validated via state-machine
          </span>
        </div>

        {analysis.reps && analysis.reps.length > 0 ? (
          analysis.reps.map((rep) => (
            <RepCard key={rep.rep_number} rep={rep} />
          ))
        ) : (
          <div className="glass-card" style={{ padding: '30px', textAlign: 'center', color: 'var(--text-muted)' }}>
            No individual reps detected in this video clip.
          </div>
        )}
      </div>
    </div>
  );
};
