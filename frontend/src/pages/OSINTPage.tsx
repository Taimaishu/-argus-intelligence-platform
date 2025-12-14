/**
 * OSINT investigation page
 */

import { useState } from 'react';
import { Shield, Globe } from 'lucide-react';
import { ArtifactSubmit } from '../components/osint/ArtifactSubmit';
import { ArtifactList } from '../components/osint/ArtifactList';
import { WebScraper } from '../components/osint/WebScraper';

export const OSINTPage = () => {
  const [activeTab, setActiveTab] = useState<'artifacts' | 'scraper'>('artifacts');

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white">OSINT Operations</h1>
        <p className="mt-2 text-gray-600 dark:text-gray-400">
          Comprehensive intelligence gathering: threat analysis, web reconnaissance, and artifact investigation
        </p>
      </div>

      {/* Tabs */}
      <div className="flex gap-2 border-b-2 border-gray-200 dark:border-gray-700">
        <button
          onClick={() => setActiveTab('artifacts')}
          className={`px-6 py-3 font-medium transition-all ${
            activeTab === 'artifacts'
              ? 'text-blue-600 dark:text-blue-400 border-b-2 border-blue-600 dark:border-blue-400 -mb-0.5'
              : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white'
          }`}
        >
          <div className="flex items-center gap-2">
            <Shield className="w-5 h-5" />
            Artifact Analysis
          </div>
        </button>

        <button
          onClick={() => setActiveTab('scraper')}
          className={`px-6 py-3 font-medium transition-all ${
            activeTab === 'scraper'
              ? 'text-green-600 dark:text-green-400 border-b-2 border-green-600 dark:border-green-400 -mb-0.5'
              : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white'
          }`}
        >
          <div className="flex items-center gap-2">
            <Globe className="w-5 h-5" />
            Web Scraper
          </div>
        </button>
      </div>

      {/* Content */}
      {activeTab === 'artifacts' ? (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-1">
            <ArtifactSubmit />
          </div>

          <div className="lg:col-span-2">
            <div className="bg-gradient-to-br from-white to-gray-50/50 dark:from-gray-900 dark:to-gray-800/50 border border-gray-200 dark:border-gray-700 rounded-xl p-6 shadow-lg">
              <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-4">Analyzed Artifacts</h2>
              <ArtifactList />
            </div>
          </div>
        </div>
      ) : (
        <WebScraper />
      )}
    </div>
  );
};
