import React from 'react';
import { LayoutDashboard, Video, History, Cpu, UserCircle, Zap } from 'lucide-react';

interface SidebarProps {
  activeTab: string;
  setActiveTab: (tab: string) => void;
  onOpenUpload: () => void;
}

export const Sidebar: React.FC<SidebarProps> = ({ activeTab, setActiveTab, onOpenUpload }) => {
  const navItems = [
    { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { id: 'history', label: 'Workout History', icon: History },
    { id: 'models', label: 'AI Models & Viva', icon: Cpu },
    { id: 'profile', label: 'Athlete Profile', icon: UserCircle },
  ];

  return (
    <aside
      style={{
        width: '240px',
        borderRight: '1px solid var(--border-subtle)',
        background: 'rgba(15, 23, 42, 0.4)',
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'space-between',
        padding: '24px 16px',
      }}
    >
      <div>
        {/* Upload Action Button */}
        <button
          className="btn-primary"
          onClick={onOpenUpload}
          style={{
            width: '100%',
            padding: '12px',
            marginBottom: '24px',
            fontSize: '0.875rem',
          }}
        >
          <Zap size={18} />
          <span>New Analysis</span>
        </button>

        {/* Nav Links */}
        <nav style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = activeTab === item.id;
            return (
              <button
                key={item.id}
                onClick={() => setActiveTab(item.id)}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '12px',
                  width: '100%',
                  padding: '10px 14px',
                  borderRadius: 'var(--radius-md)',
                  border: 'none',
                  background: isActive ? 'rgba(16, 185, 129, 0.12)' : 'transparent',
                  color: isActive ? '#34d399' : 'var(--text-secondary)',
                  cursor: 'pointer',
                  fontWeight: isActive ? 600 : 500,
                  fontSize: '0.875rem',
                  transition: 'all 0.18s ease',
                  textAlign: 'left',
                }}
              >
                <Icon size={18} color={isActive ? '#34d399' : 'var(--text-muted)'} />
                <span>{item.label}</span>
              </button>
            );
          })}
        </nav>
      </div>

      {/* Dataset & Viva Badge */}
      <div
        className="glass-card"
        style={{
          padding: '14px',
          background: 'rgba(17, 24, 39, 0.6)',
          borderRadius: 'var(--radius-md)',
        }}
      >
        <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', marginBottom: '4px', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
          Academic AIML viva
        </div>
        <div style={{ fontSize: '0.82rem', fontWeight: 600, color: '#fff' }}>
          4 Exercise Models
        </div>
        <div style={{ fontSize: '0.72rem', color: '#10b981', marginTop: '2px' }}>
          MediaPipe + RF + XGB + LSTM
        </div>
      </div>
    </aside>
  );
};
