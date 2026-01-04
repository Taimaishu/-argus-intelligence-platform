/**
 * Main layout component
 */

import type { ReactNode } from 'react';
import { useState, useEffect } from 'react';
import { Header } from './Header';
import { SetupWizard } from '../setup/SetupWizard';

interface MainLayoutProps {
  children: ReactNode;
}

export const MainLayout = ({ children }: MainLayoutProps) => {
  const [showSetup, setShowSetup] = useState(false);

  useEffect(() => {
    // Check if setup has been completed
    const setupCompleted = localStorage.getItem('setup_completed');

    // Check if user has any API keys configured
    const hasOpenAI = localStorage.getItem('api_key_openai');
    const hasAnthropic = localStorage.getItem('api_key_anthropic');

    // Show setup if not completed and no API keys configured
    if (!setupCompleted && !hasOpenAI && !hasAnthropic) {
      setShowSetup(true);
    }
  }, []);

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 via-blue-50/30 to-indigo-50/30 dark:from-gray-950 dark:via-blue-950/20 dark:to-indigo-950/20">
      <Header />
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {children}
      </main>

      {showSetup && <SetupWizard onClose={() => setShowSetup(false)} />}
    </div>
  );
};
