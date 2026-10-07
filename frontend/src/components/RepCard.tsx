import React from 'react';
import { RepTelemetry } from '../types';
import { Clock, AlertTriangle, CheckCircle, ChevronRight } from 'lucide-react';

interface RepCardProps {
  rep: RepTelemetry;
}

export const RepCard: React.FC<RepCardProps> = ({ rep }) => {
  const getScoreColor = (score: number) => {
    if (score >= 85) return '#10b981';
    if (score >= 70) return '#f59e0b';
    return '#ef4444';
  };

  return (
    <div
      className="glass-card"
      style={{
        padding: '16px 20px',
        marginBottom: '12px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
      }}
    >
      <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
        {/* Rep Number Badge */}
        <div
          style={{
            width: '44px',
            height: '44px',
            borderRadius: '12px',
            background: 'rgba(255, 255, 255, 0.04)',
            border: '1px solid var(--border-subtle)',
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
          }}
        >
          <span style={{ fontSize: '0.62rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>REP</span>
          <span style={{ fontSize: '1.05rem', fontWeight: 800, color: '#fff', fontFamily: 'var(--font-mono)' }}>
            #{rep.rep_number}
          </span>
        </div>

        {/* Telemetry Details */}
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '4px' }}>
            <span style={{ fontSize: '0.85rem', fontWeight: 600, color: '#fff' }}>
              Duration: {rep.duration_sec}s
            </span>
            <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
              (Ecc: {rep.eccentric_duration_sec}s / Con: {rep.concentric_duration_sec}s)
            </span>
            <span style={{ fontSize: '0.75rem', color: '#38bdf8' }}>
              ROM: {rep.rom}°
            </span>
          </div>

          {/* Form Fault Tags */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px', flexWrap: 'wrap' }}>
            {rep.form_errors && rep.form_errors.length > 0 ? (
              rep.form_errors.map((err, i) => (
                <span
                  key={i}
                  className="badge badge-rose"
                  style={{ fontSize: '0.65rem', padding: '2px 8px' }}
                >
                  <AlertTriangle size={10} />
                  {err.replace('_', ' ')}
                </span>
              ))
            ) : (
              <span
                className="badge badge-emerald"
                style={{ fontSize: '0.65rem', padding: '2px 8px' }}
              >
                <CheckCircle size={10} />
                Optimal Form
              </span>
            )}
          </div>
        </div>
      </div>

      {/* Score Pill */}
      <div style={{ textAlign: 'right' }}>
        <div
          style={{
            fontSize: '1.3rem',
            fontWeight: 800,
            color: getScoreColor(rep.score),
            fontFamily: 'var(--font-mono)',
          }}
        >
          {Math.round(rep.score)}
          <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>/100</span>
        </div>
        <div style={{ fontSize: '0.68rem', color: 'var(--text-muted)' }}>Rep Score</div>
      </div>
    </div>
  );
};
