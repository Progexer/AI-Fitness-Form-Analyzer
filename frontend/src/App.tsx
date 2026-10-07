import React, { useState } from 'react';
import { Navbar } from './components/Navbar';
import { Sidebar } from './components/Sidebar';
import { UploadModal } from './components/UploadModal';
import { DashboardPage } from './pages/DashboardPage';
import { AnalysisPage } from './pages/AnalysisPage';
import { HistoryPage } from './pages/HistoryPage';
import { ModelsPage } from './pages/ModelsPage';
import { ProfilePage } from './pages/ProfilePage';

export const App: React.FC = () => {
  const [activeTab, setActiveTab] = useState<string>('dashboard');
  const [isUploadOpen, setIsUploadOpen] = useState<boolean>(false);
  const [selectedAnalysisId, setSelectedAnalysisId] = useState<string | null>(null);

  const handleAnalysisStarted = (analysisId: string) => {
    setSelectedAnalysisId(analysisId);
    setActiveTab('analysis');
  };

  const handleViewAnalysis = (analysisId: string) => {
    setSelectedAnalysisId(analysisId);
    setActiveTab('analysis');
  };

  const handleBackToDashboard = () => {
    setSelectedAnalysisId(null);
    setActiveTab('dashboard');
  };

  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column', background: 'var(--bg-main)' }}>
      {/* Top Navbar */}
      <Navbar activeTab={activeTab} />

      <div style={{ display: 'flex', flex: 1 }}>
        {/* Left Sidebar */}
        <Sidebar
          activeTab={activeTab}
          setActiveTab={(tab) => {
            if (tab !== 'analysis') setSelectedAnalysisId(null);
            setActiveTab(tab);
          }}
          onOpenUpload={() => setIsUploadOpen(true)}
        />

        {/* Main Content Area */}
        <main style={{ flex: 1, overflowY: 'auto' }}>
          {activeTab === 'dashboard' && (
            <DashboardPage
              onOpenUpload={() => setIsUploadOpen(true)}
              onViewAnalysis={handleViewAnalysis}
            />
          )}

          {activeTab === 'analysis' && selectedAnalysisId && (
            <AnalysisPage
              analysisId={selectedAnalysisId}
              onBack={handleBackToDashboard}
            />
          )}

          {activeTab === 'history' && (
            <HistoryPage onViewAnalysis={handleViewAnalysis} />
          )}

          {activeTab === 'models' && <ModelsPage />}

          {activeTab === 'profile' && <ProfilePage />}
        </main>
      </div>

      {/* Video Upload Modal */}
      <UploadModal
        isOpen={isUploadOpen}
        onClose={() => setIsUploadOpen(false)}
        onAnalysisStarted={handleAnalysisStarted}
      />
    </div>
  );
};

export default App;
