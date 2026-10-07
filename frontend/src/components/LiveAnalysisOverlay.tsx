import React from 'react';
import { AnalysisProgress } from '../types';
import { Activity, Flame, ShieldAlert, Sparkles, CheckCircle2 } from 'lucide-react';

interface LiveAnalysisOverlayProps {
  progress: AnalysisProgress | null;
  videoUrl?: string;
}

export const LiveAnalysisOverlay: React.FC<LiveAnalysisOverlayProps> = ({ progress, videoUrl }) => {
  if (!progress) return null;

  const getPhaseBadgeColor = (phase: string) => {
    switch (phase) {
      case 'ECCENTRIC':
        return 'badge-cyan';
      case 'INFLECTION':
        return 'badge-amber';
      case 'CONCENTRIC':
        return 'badge-emerald';
      case 'COMPLETED':
        return 'badge-emerald';
      default:
        return 'badge-emerald';
    }
  };

  return (
    <div
      className="glass-card"
      style={{
        padding: '24px',
        position: 'relative',
        overflow: 'hidden',
        border: '1px solid rgba(16, 185, 129, 0.3)',
        boxShadow: '0 8px 32px rgba(0, 0, 0, 0.4)',
      }}
    >
      {/* Top Header */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '20px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <div className="animate-spin" style={{ display: 'inline-flex' }}>
            <Activity size={20} color="#10b981" />
          </div>
          <div>
            <h3 style={{ fontSize: '1.05rem', fontWeight: 700, color: '#fff' }}>
              Real-Time Biomechanical Analysis Stream
            </h3>
            <p style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>
              Frame {progress.current_frame} / {progress.total_frames} — Processing at 30 FPS
            </p>
          </div>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <span className={`badge ${getPhaseBadgeColor(progress.current_phase)}`}>
            Phase: {progress.current_phase}
          </span>
          <span className="badge badge-emerald">
            Rep #{progress.current_rep}
          </span>
        </div>
      </div>

      {/* Real-Time Angle Gauge & Metrics Bar */}
      <div
        style={{
          display: 'grid',
          gridTemplateColumns: '1fr 1fr 1fr',
          gap: '16px',
          marginBottom: '20px',
        }}
      >
        <div
          style={{
            background: 'rgba(255, 255, 255, 0.03)',
            borderRadius: 'var(--radius-md)',
            padding: '16px',
            border: '1px solid var(--border-subtle)',
            textAlign: 'center',
          }}
        >
          <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase', marginBottom: '4px' }}>
            Current Joint Angle
          </div>
          <div style={{ fontSize: '1.8rem', fontWeight: 800, color: '#38bdf8', fontFamily: 'var(--font-mono)' }}>
            {progress.current_angle ? `${Math.round(progress.current_angle)}°` : '--'}
          </div>
          <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', marginTop: '2px' }}>
            Kinematic Vertex Tracking
          </div>
        </div>

        <div
          style={{
            background: 'rgba(255, 255, 255, 0.03)',
            borderRadius: 'var(--radius-md)',
            padding: '16px',
            border: '1px solid var(--border-subtle)',
            textAlign: 'center',
          }}
        >
          <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase', marginBottom: '4px' }}>
            Repetition Counter
          </div>
          <div style={{ fontSize: '1.8rem', fontWeight: 800, color: '#34d399', fontFamily: 'var(--font-mono)' }}>
            {progress.current_rep}
          </div>
          <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', marginTop: '2px' }}>
            State-Machine Verified
          </div>
        </div>

        <div
          style={{
            background: 'rgba(255, 255, 255, 0.03)',
            borderRadius: 'var(--radius-md)',
            padding: '16px',
            border: '1px solid var(--border-subtle)',
            textAlign: 'center',
          }}
        >
          <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase', marginBottom: '4px' }}>
            Pipeline Progress
          </div>
          <div style={{ fontSize: '1.8rem', fontWeight: 800, color: '#f59e0b', fontFamily: 'var(--font-mono)' }}>
            {Math.round(progress.progress_percent)}%
          </div>
          <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', marginTop: '2px' }}>
            OpenCV → Pose → XGBoost
          </div>
        </div>
      </div>

      {/* Instant Coaching Cue Banner */}
      <div
        style={{
          background: 'rgba(16, 185, 129, 0.08)',
          border: '1px solid rgba(16, 185, 129, 0.25)',
          borderRadius: 'var(--radius-md)',
          padding: '14px 18px',
          display: 'flex',
          alignItems: 'center',
          gap: '12px',
          marginBottom: '18px',
        }}
      >
        <Sparkles size={20} color="#34d399" />
        <div style={{ flex: 1 }}>
          <span style={{ fontSize: '0.75rem', textTransform: 'uppercase', color: '#10b981', fontWeight: 700, letterSpacing: '0.05em' }}>
            Live Coaching Cue:
          </span>
          <p style={{ fontSize: '0.92rem', color: '#ffffff', fontWeight: 500, marginTop: '2px' }}>
            "{progress.latest_cue || 'Analyzing biomechanical movement pattern...'}"
          </p>
        </div>
      </div>

      {/* Progress Bar */}
      <div>
        <div
          style={{
            height: '8px',
            width: '100%',
            background: 'rgba(255, 255, 255, 0.08)',
            borderRadius: '9999px',
            overflow: 'hidden',
          }}
        >
          <div
            style={{
              height: '100%',
              width: `${progress.progress_percent}%`,
              background: 'linear-gradient(90deg, #10b981 0%, #06b6d4 100%)',
              borderRadius: '9999px',
              transition: 'width 0.2s ease-out',
              boxShadow: '0 0 12px rgba(16, 185, 129, 0.6)',
            }}
          />
        </div>
      </div>
    </div>
  );
};
