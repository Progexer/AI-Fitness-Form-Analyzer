import React, { useEffect, useState } from 'react';
import { AnalysisResult } from '../types';
import { api } from '../services/api';
import { Search, Filter, ArrowUpRight, Download, Dumbbell } from 'lucide-react';

interface HistoryPageProps {
  onViewAnalysis: (analysisId: string) => void;
}

export const HistoryPage: React.FC<HistoryPageProps> = ({ onViewAnalysis }) => {
  const [analyses, setAnalyses] = useState<AnalysisResult[]>([]);
  const [filtered, setFiltered] = useState<AnalysisResult[]>([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [exerciseFilter, setExerciseFilter] = useState('all');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.listAnalyses()
      .then((data) => {
        setAnalyses(data);
        setFiltered(data);
      })
      .catch((e) => console.error(e))
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => {
    let list = [...analyses];
    if (exerciseFilter !== 'all') {
      list = list.filter((a) => a.exercise.toLowerCase().includes(exerciseFilter.toLowerCase()));
    }
    if (searchTerm.trim()) {
      const q = searchTerm.toLowerCase();
      list = list.filter((a) => a.exercise.toLowerCase().includes(q) || a.id.toLowerCase().includes(q));
    }
    setFiltered(list);
  }, [searchTerm, exerciseFilter, analyses]);

  const getScoreColor = (score: number) => {
    if (score >= 85) return '#10b981';
    if (score >= 70) return '#f59e0b';
    return '#ef4444';
  };

  return (
    <div style={{ padding: '32px 36px', maxWidth: '1300px', margin: '0 auto' }}>
      <div style={{ marginBottom: '28px' }}>
        <h1 style={{ fontSize: '1.85rem', fontWeight: 800, color: '#fff', marginBottom: '6px' }}>
          Workout History & Telemetry Logs
        </h1>
        <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>
          Browse past computer vision sessions, inspect repetition quality, and export PDF reports.
        </p>
      </div>

      {/* Filter and Search Bar */}
      <div
        className="glass-card"
        style={{
          padding: '16px 20px',
          marginBottom: '24px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          gap: '16px',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px', flex: 1 }}>
          <Search size={18} color="var(--text-muted)" />
          <input
            type="text"
            placeholder="Search by exercise or analysis ID..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            style={{
              background: 'transparent',
              border: 'none',
              color: '#fff',
              fontSize: '0.875rem',
              outline: 'none',
              width: '100%',
            }}
          />
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <Filter size={16} color="var(--text-muted)" />
          <select
            value={exerciseFilter}
            onChange={(e) => setExerciseFilter(e.target.value)}
            style={{
              background: 'rgba(0,0,0,0.4)',
              border: '1px solid var(--border-subtle)',
              borderRadius: 'var(--radius-sm)',
              color: '#fff',
              padding: '6px 12px',
              fontSize: '0.82rem',
              outline: 'none',
            }}
          >
            <option value="all">All Exercises</option>
            <option value="squat">Squat</option>
            <option value="push_up">Push-up</option>
            <option value="bicep_curl">Bicep Curl</option>
            <option value="shoulder_press">Shoulder Press</option>
          </select>
        </div>
      </div>

      {/* Table */}
      <div className="glass-card" style={{ padding: '20px' }}>
        {filtered.length === 0 ? (
          <div style={{ padding: '40px 20px', textAlign: 'center', color: 'var(--text-muted)' }}>
            No sessions match your filter criteria.
          </div>
        ) : (
          <div style={{ overflowX: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left' }}>
              <thead>
                <tr style={{ borderBottom: '1px solid var(--border-subtle)', color: 'var(--text-muted)', fontSize: '0.75rem', textTransform: 'uppercase' }}>
                  <th style={{ padding: '12px 10px' }}>Session ID</th>
                  <th style={{ padding: '12px 10px' }}>Exercise</th>
                  <th style={{ padding: '12px 10px' }}>Model</th>
                  <th style={{ padding: '12px 10px' }}>Reps</th>
                  <th style={{ padding: '12px 10px' }}>Score</th>
                  <th style={{ padding: '12px 10px' }}>Grade</th>
                  <th style={{ padding: '12px 10px' }}>Timestamp</th>
                  <th style={{ padding: '12px 10px', textAlign: 'right' }}>Actions</th>
                </tr>
              </thead>
              <tbody>
                {filtered.map((item) => (
                  <tr
                    key={item.id}
                    style={{
                      borderBottom: '1px solid rgba(255, 255, 255, 0.04)',
                      fontSize: '0.875rem',
                    }}
                  >
                    <td style={{ padding: '14px 10px', fontFamily: 'var(--font-mono)', fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                      {item.id}
                    </td>
                    <td style={{ padding: '14px 10px', fontWeight: 600, color: '#fff', textTransform: 'capitalize' }}>
                      {item.exercise?.replace('_', ' ')}
                    </td>
                    <td style={{ padding: '14px 10px', color: 'var(--text-secondary)', fontSize: '0.8rem' }}>
                      {item.model_used}
                    </td>
                    <td style={{ padding: '14px 10px', fontFamily: 'var(--font-mono)', color: '#38bdf8' }}>
                      {item.total_reps} reps
                    </td>
                    <td style={{ padding: '14px 10px', fontFamily: 'var(--font-mono)', fontWeight: 700, color: getScoreColor(item.overall_score) }}>
                      {item.overall_score}/100
                    </td>
                    <td style={{ padding: '14px 10px' }}>
                      <span className="badge badge-emerald" style={{ fontSize: '0.7rem' }}>
                        {item.grade}
                      </span>
                    </td>
                    <td style={{ padding: '14px 10px', color: 'var(--text-muted)', fontSize: '0.8rem' }}>
                      {item.created_at?.slice(0, 16).replace('T', ' ')}
                    </td>
                    <td style={{ padding: '14px 10px', textAlign: 'right' }}>
                      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'flex-end', gap: '8px' }}>
                        <button
                          className="btn-secondary"
                          onClick={() => onViewAnalysis(item.id)}
                          style={{ padding: '6px 10px', fontSize: '0.75rem' }}
                        >
                          <span>Review</span>
                          <ArrowUpRight size={14} />
                        </button>
                        <button
                          className="btn-secondary"
                          onClick={() => api.downloadPdfReport(item.id, `Report_${item.exercise}_${item.id.slice(0, 6)}.pdf`)}
                          style={{ padding: '6px 10px', fontSize: '0.75rem' }}
                        >
                          <Download size={14} />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};
