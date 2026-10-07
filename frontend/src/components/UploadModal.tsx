import React, { useState, useRef } from 'react';
import { UploadCloud, X, Film, CheckCircle2, AlertCircle, Loader2 } from 'lucide-react';
import { api } from '../services/api';

interface UploadModalProps {
  isOpen: boolean;
  onClose: () => void;
  onAnalysisStarted: (analysisId: string, videoId: string) => void;
}

export const UploadModal: React.FC<UploadModalProps> = ({ isOpen, onClose, onAnalysisStarted }) => {
  const [file, setFile] = useState<File | null>(null);
  const [exerciseOverride, setExerciseOverride] = useState<string>('');
  const [modelType, setModelType] = useState<string>('random_forest');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  if (!isOpen) return null;

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const selected = e.target.files[0];
      setFile(selected);
      setError(null);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      setFile(e.dataTransfer.files[0]);
      setError(null);
    }
  };

  const handleSubmit = async () => {
    if (!file) {
      setError('Please select or drop a workout video to analyze.');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      // 1. Upload video
      const uploaded = await api.uploadVideo(file);

      // 2. Start computer vision analysis
      const analysisRes = await api.startAnalysis(
        uploaded.id,
        exerciseOverride || undefined,
        modelType
      );

      onClose();
      onAnalysisStarted(analysisRes.analysis_id, uploaded.id);
    } catch (err: any) {
      setError(err.message || 'Failed to initiate video processing');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div
      style={{
        position: 'fixed',
        inset: 0,
        backgroundColor: 'rgba(5, 8, 16, 0.8)',
        backdropFilter: 'blur(8px)',
        zIndex: 50,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '20px',
      }}
    >
      <div
        className="glass-card"
        style={{
          width: '100%',
          maxWidth: '560px',
          padding: '28px',
          background: 'rgba(15, 23, 42, 0.95)',
          border: '1px solid rgba(255, 255, 255, 0.12)',
          boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.7)',
        }}
      >
        {/* Header */}
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '20px' }}>
          <div>
            <h2 style={{ fontSize: '1.25rem', fontWeight: 700, color: '#fff' }}>
              Upload Exercise Video
            </h2>
            <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
              Supports MP4, MOV, AVI up to 500MB
            </p>
          </div>
          <button
            onClick={onClose}
            style={{
              background: 'transparent',
              border: 'none',
              color: 'var(--text-muted)',
              cursor: 'pointer',
              padding: '6px',
            }}
          >
            <X size={20} />
          </button>
        </div>

        {/* Dropzone */}
        <div
          onDragOver={(e) => e.preventDefault()}
          onDrop={handleDrop}
          onClick={() => fileInputRef.current?.click()}
          style={{
            border: '2px dashed rgba(16, 185, 129, 0.35)',
            borderRadius: 'var(--radius-lg)',
            padding: '32px 20px',
            textAlign: 'center',
            cursor: 'pointer',
            background: file ? 'rgba(16, 185, 129, 0.04)' : 'rgba(255, 255, 255, 0.02)',
            transition: 'all 0.2s ease',
            marginBottom: '20px',
          }}
        >
          <input
            ref={fileInputRef}
            type="file"
            accept="video/*"
            style={{ display: 'none' }}
            onChange={handleFileChange}
          />
          {file ? (
            <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '8px' }}>
              <Film size={36} color="#10b981" />
              <div style={{ fontWeight: 600, color: '#fff', fontSize: '0.92rem' }}>{file.name}</div>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                {(file.size / (1024 * 1024)).toFixed(1)} MB — Click to change
              </div>
            </div>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '10px' }}>
              <UploadCloud size={40} color="#64748b" />
              <div style={{ fontWeight: 600, color: '#f8fafc', fontSize: '0.95rem' }}>
                Drag & drop video here, or <span style={{ color: '#10b981' }}>browse</span>
              </div>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                Record full body in frame (squat, push-up, curl, shoulder press)
              </div>
            </div>
          )}
        </div>

        {/* Form Options */}
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px', marginBottom: '24px' }}>
          <div>
            <label style={{ display: 'block', fontSize: '0.78rem', color: 'var(--text-secondary)', marginBottom: '6px', fontWeight: 600 }}>
              Exercise Recognition
            </label>
            <select
              value={exerciseOverride}
              onChange={(e) => setExerciseOverride(e.target.value)}
              style={{
                width: '100%',
                padding: '10px 12px',
                borderRadius: 'var(--radius-md)',
                background: 'rgba(0, 0, 0, 0.4)',
                border: '1px solid var(--border-subtle)',
                color: '#fff',
                fontSize: '0.85rem',
                outline: 'none',
              }}
            >
              <option value="">Auto-Detect via ML (Default)</option>
              <option value="squat">Squat</option>
              <option value="push_up">Push-up</option>
              <option value="bicep_curl">Bicep Curl</option>
              <option value="shoulder_press">Shoulder Press</option>
            </select>
          </div>

          <div>
            <label style={{ display: 'block', fontSize: '0.78rem', color: 'var(--text-secondary)', marginBottom: '6px', fontWeight: 600 }}>
              AI Model Pipeline
            </label>
            <select
              value={modelType}
              onChange={(e) => setModelType(e.target.value)}
              style={{
                width: '100%',
                padding: '10px 12px',
                borderRadius: 'var(--radius-md)',
                background: 'rgba(0, 0, 0, 0.4)',
                border: '1px solid var(--border-subtle)',
                color: '#fff',
                fontSize: '0.85rem',
                outline: 'none',
              }}
            >
              <option value="random_forest">Random Forest + XGBoost</option>
              <option value="lstm">Bi-LSTM (Temporal Windows)</option>
            </select>
          </div>
        </div>

        {error && (
          <div
            style={{
              padding: '10px 14px',
              borderRadius: 'var(--radius-md)',
              background: 'rgba(239, 68, 68, 0.1)',
              border: '1px solid rgba(239, 68, 68, 0.3)',
              color: '#f87171',
              fontSize: '0.8rem',
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              marginBottom: '16px',
            }}
          >
            <AlertCircle size={16} />
            <span>{error}</span>
          </div>
        )}

        {/* Submit Button */}
        <button
          className="btn-primary"
          onClick={handleSubmit}
          disabled={loading || !file}
          style={{
            width: '100%',
            padding: '12px',
            opacity: loading || !file ? 0.6 : 1,
            cursor: loading || !file ? 'not-allowed' : 'pointer',
          }}
        >
          {loading ? (
            <>
              <Loader2 size={18} className="animate-spin" />
              <span>Uploading & Initializing Models...</span>
            </>
          ) : (
            <span>Start Biomechanical Analysis</span>
          )}
        </button>
      </div>
    </div>
  );
};
