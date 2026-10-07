import React, { useState } from 'react';
import { User, Award, Dumbbell, Target, Shield, Save } from 'lucide-react';

export const ProfilePage: React.FC = () => {
  const [fullName, setFullName] = useState('Athlete Demo');
  const [goal, setGoal] = useState('Hypertrophy & Form Perfection');
  const [level, setLevel] = useState('intermediate');
  const [saved, setSaved] = useState(false);

  const handleSave = (e: React.FormEvent) => {
    e.preventDefault();
    setSaved(true);
    setTimeout(() => setSaved(false), 2500);
  };

  return (
    <div style={{ padding: '32px 36px', maxWidth: '900px', margin: '0 auto' }}>
      <div style={{ marginBottom: '28px' }}>
        <h1 style={{ fontSize: '1.85rem', fontWeight: 800, color: '#fff', marginBottom: '6px' }}>
          Athlete Profile & Biomechanical Goals
        </h1>
        <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>
          Configure movement baselines, target joint angle tolerances, and training experience levels.
        </p>
      </div>

      <div className="glass-card" style={{ padding: '32px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '20px', marginBottom: '32px' }}>
          <div
            style={{
              width: '72px',
              height: '72px',
              borderRadius: '50%',
              background: 'linear-gradient(135deg, #10b981 0%, #06b6d4 100%)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              boxShadow: '0 8px 24px var(--accent-primary-glow)',
            }}
          >
            <User size={36} color="#fff" />
          </div>
          <div>
            <h2 style={{ fontSize: '1.3rem', fontWeight: 700, color: '#fff' }}>{fullName}</h2>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginTop: '4px' }}>
              <span className="badge badge-emerald">Verified Athlete</span>
              <span className="badge badge-cyan">Demo Student Viva</span>
            </div>
          </div>
        </div>

        <form onSubmit={handleSave}>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px', marginBottom: '24px' }}>
            <div>
              <label style={{ display: 'block', fontSize: '0.8rem', color: 'var(--text-secondary)', marginBottom: '6px', fontWeight: 600 }}>
                Full Name
              </label>
              <input
                type="text"
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
                style={{
                  width: '100%',
                  padding: '10px 14px',
                  borderRadius: 'var(--radius-md)',
                  background: 'rgba(0, 0, 0, 0.4)',
                  border: '1px solid var(--border-subtle)',
                  color: '#fff',
                  fontSize: '0.88rem',
                  outline: 'none',
                }}
              />
            </div>

            <div>
              <label style={{ display: 'block', fontSize: '0.8rem', color: 'var(--text-secondary)', marginBottom: '6px', fontWeight: 600 }}>
                Experience Level
              </label>
              <select
                value={level}
                onChange={(e) => setLevel(e.target.value)}
                style={{
                  width: '100%',
                  padding: '10px 14px',
                  borderRadius: 'var(--radius-md)',
                  background: 'rgba(0, 0, 0, 0.4)',
                  border: '1px solid var(--border-subtle)',
                  color: '#fff',
                  fontSize: '0.88rem',
                  outline: 'none',
                }}
              >
                <option value="beginner">Beginner (Permissive tolerances)</option>
                <option value="intermediate">Intermediate (Standard biomechanical angles)</option>
                <option value="advanced">Advanced / Powerlifter (Strict lockout & depth)</option>
              </select>
            </div>
          </div>

          <div style={{ marginBottom: '32px' }}>
            <label style={{ display: 'block', fontSize: '0.8rem', color: 'var(--text-secondary)', marginBottom: '6px', fontWeight: 600 }}>
              Primary Fitness Objective
            </label>
            <input
              type="text"
              value={goal}
              onChange={(e) => setGoal(e.target.value)}
              style={{
                width: '100%',
                padding: '10px 14px',
                borderRadius: 'var(--radius-md)',
                background: 'rgba(0, 0, 0, 0.4)',
                border: '1px solid var(--border-subtle)',
                color: '#fff',
                fontSize: '0.88rem',
                outline: 'none',
              }}
            />
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '14px' }}>
            <button type="submit" className="btn-primary" style={{ padding: '10px 22px' }}>
              <Save size={16} />
              <span>Update Profile</span>
            </button>
            {saved && (
              <span style={{ fontSize: '0.85rem', color: '#10b981', fontWeight: 500 }}>
                Profile settings successfully saved!
              </span>
            )}
          </div>
        </form>
      </div>
    </div>
  );
};
