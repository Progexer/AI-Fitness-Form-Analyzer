import React, { useEffect, useState } from 'react';
import { ModelInfo } from '../types';
import { api } from '../services/api';
import { Cpu, Zap, Activity, CheckCircle, Database, ShieldCheck, Layers } from 'lucide-react';

export const ModelsPage: React.FC = () => {
  const [models, setModels] = useState<ModelInfo[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.listModels()
      .then((data) => setModels(data))
      .catch((e) => console.error(e))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div style={{ padding: '32px 36px', maxWidth: '1300px', margin: '0 auto' }}>
      <div style={{ marginBottom: '28px' }}>
        <h1 style={{ fontSize: '1.85rem', fontWeight: 800, color: '#fff', marginBottom: '6px' }}>
          AI Models & Viva Architecture Governance
        </h1>
        <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>
          Real-time latency benchmarks, architectural trade-offs, and dataset integrity metrics for 3rd-year university viva defense.
        </p>
      </div>

      {/* Model Cards Grid */}
      <div
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(350px, 1fr))',
          gap: '24px',
          marginBottom: '32px',
        }}
      >
        {models.map((m) => (
          <div
            key={m.id}
            className="glass-card"
            style={{
              padding: '24px',
              border: m.is_active ? '1px solid rgba(16, 185, 129, 0.5)' : '1px solid var(--border-subtle)',
              position: 'relative',
              boxShadow: m.is_active ? '0 10px 30px -10px var(--accent-primary-glow)' : undefined,
            }}
          >
            {m.is_active && (
              <div
                style={{
                  position: 'absolute',
                  top: '16px',
                  right: '16px',
                }}
              >
                <span className="badge badge-emerald" style={{ fontSize: '0.65rem' }}>
                  Active in Live Engine
                </span>
              </div>
            )}

            <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '14px' }}>
              <div style={{ padding: '10px', borderRadius: '10px', background: 'rgba(255, 255, 255, 0.04)' }}>
                <Cpu size={22} color={m.is_active ? '#10b981' : '#38bdf8'} />
              </div>
              <div>
                <h3 style={{ fontSize: '1.1rem', fontWeight: 700, color: '#fff' }}>{m.name}</h3>
                <span style={{ fontSize: '0.72rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>
                  {m.type.replace('_', ' ')}
                </span>
              </div>
            </div>

            <p style={{ fontSize: '0.82rem', color: 'var(--text-secondary)', lineHeight: 1.5, marginBottom: '20px' }}>
              {m.description}
            </p>

            {/* Performance KPI Table */}
            <div
              style={{
                display: 'grid',
                gridTemplateColumns: '1fr 1fr',
                gap: '12px',
                padding: '14px',
                borderRadius: 'var(--radius-md)',
                background: 'rgba(0, 0, 0, 0.25)',
                border: '1px solid var(--border-subtle)',
              }}
            >
              <div>
                <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>Validation Accuracy</div>
                <div style={{ fontSize: '1.2rem', fontWeight: 800, color: '#34d399', fontFamily: 'var(--font-mono)' }}>
                  {m.accuracy != null ? `${(m.accuracy * 100).toFixed(1)}%` : 'Not evaluated yet'}
                </div>
              </div>

              <div>
                <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>Macro F1-Score</div>
                <div style={{ fontSize: '1.2rem', fontWeight: 800, color: '#38bdf8', fontFamily: 'var(--font-mono)' }}>
                  {m.macro_f1 != null ? m.macro_f1.toFixed(3) : 'Not evaluated yet'}
                </div>
              </div>

              <div>
                <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>Inference Latency</div>
                <div style={{ fontSize: '1.2rem', fontWeight: 800, color: '#fbbf24', fontFamily: 'var(--font-mono)' }}>
                  {m.latency_ms != null ? `${m.latency_ms} ms` : 'Not measured yet'}
                </div>
              </div>

              <div>
                <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>Throughput</div>
                <div style={{ fontSize: '1.2rem', fontWeight: 800, color: '#a78bfa', fontFamily: 'var(--font-mono)' }}>
                  {m.fps != null ? `${Math.round(m.fps)} FPS` : 'Not measured yet'}
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Viva Defense & Dataset Integrity Section */}
      <div style={{ display: 'grid', gridTemplateColumns: '1.2fr 1fr', gap: '24px' }}>
        {/* Dataset Transparency Card */}
        <div className="glass-card" style={{ padding: '24px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '16px' }}>
            <Database size={20} color="#38bdf8" />
            <h3 style={{ fontSize: '1.1rem', fontWeight: 700, color: '#fff' }}>
              Dataset Architecture & Deduplication
            </h3>
          </div>

          <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', lineHeight: 1.6, display: 'flex', flexDirection: 'column', gap: '10px' }}>
            <div style={{ display: 'flex', alignItems: 'flex-start', gap: '10px' }}>
              <ShieldCheck size={16} color="#10b981" style={{ marginTop: '3px', flexShrink: 0 }} />
              <div>
                <strong style={{ color: '#fff' }}>Video-Level Stratified Splits:</strong> 70% Train (114 videos), 15% Validation (23 videos), 15% Test (27 videos). Video frames never cross splits, strictly preventing data leakage.
              </div>
            </div>

            <div style={{ display: 'flex', alignItems: 'flex-start', gap: '10px' }}>
              <ShieldCheck size={16} color="#10b981" style={{ marginTop: '3px', flexShrink: 0 }} />
              <div>
                <strong style={{ color: '#fff' }}>Deduplication Rigor:</strong> 8 overlapping files between <code>similar_dataset</code> and <code>final_kaggle</code> were identified via SHA-256 and quarantined.
              </div>
            </div>

            <div style={{ display: 'flex', alignItems: 'flex-start', gap: '10px' }}>
              <ShieldCheck size={16} color="#10b981" style={{ marginTop: '3px', flexShrink: 0 }} />
              <div>
                <strong style={{ color: '#fff' }}>Hammer Curl Exclusion:</strong> Excluded 19 non-target hammer curl videos to maintain clean focus on the 4 primary exercises.
              </div>
            </div>

            <div style={{ display: 'flex', alignItems: 'flex-start', gap: '10px' }}>
              <ShieldCheck size={16} color="#10b981" style={{ marginTop: '3px', flexShrink: 0 }} />
              <div>
                <strong style={{ color: '#fff' }}>Isolated Holdout:</strong> <code>my_test_video_1</code> is strictly isolated as an external generalization test set.
              </div>
            </div>
          </div>
        </div>

        {/* Viva Quick Reference */}
        <div className="glass-card" style={{ padding: '24px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '16px' }}>
            <Layers size={20} color="#a78bfa" />
            <h3 style={{ fontSize: '1.1rem', fontWeight: 700, color: '#fff' }}>
              Viva Defense Talking Points
            </h3>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px', fontSize: '0.82rem', color: 'var(--text-secondary)' }}>
            <div style={{ padding: '10px 12px', borderRadius: '8px', background: 'rgba(255, 255, 255, 0.03)' }}>
              <div style={{ fontWeight: 600, color: '#fff', marginBottom: '2px' }}>Why Random Forest + XGBoost?</div>
              <div>Sub-millisecond inference (0.49ms) makes them ideal for edge CPU execution while achieving &gt;90% accuracy on structured biomechanical vectors.</div>
            </div>

            <div style={{ padding: '10px 12px', borderRadius: '8px', background: 'rgba(255, 255, 255, 0.03)' }}>
              <div style={{ fontWeight: 600, color: '#fff', marginBottom: '2px' }}>Why State-Machine Rep Counter?</div>
              <div>Peak inflection tracking with hysteresis eliminates false positives caused by camera noise or mid-rep hesitation.</div>
            </div>

            <div style={{ padding: '10px 12px', borderRadius: '8px', background: 'rgba(255, 255, 255, 0.03)' }}>
              <div style={{ fontWeight: 600, color: '#fff', marginBottom: '2px' }}>Role of Bi-LSTM:</div>
              <div>Captures bidirectional temporal context across 30-frame sliding windows for continuous movement phase segmentation.</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
