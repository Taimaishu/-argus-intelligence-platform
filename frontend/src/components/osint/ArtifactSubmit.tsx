/**
 * Artifact submission form
 */

import { useState } from 'react';
import type { FormEvent } from 'react';
import { Search, Loader2, Shield } from 'lucide-react';
import { useOSINTStore } from '../../store/useOSINTStore';

export const ArtifactSubmit = () => {
  const [artifactType, setArtifactType] = useState('ip_address');
  const [value, setValue] = useState('');
  const { submitArtifact, loading } = useOSINTStore();

  const artifactTypes = [
    { value: 'ip_address', label: 'IP Address', placeholder: '192.168.1.1' },
    { value: 'domain', label: 'Domain', placeholder: 'example.com' },
    { value: 'url', label: 'URL', placeholder: 'https://example.com' },
    { value: 'email', label: 'Email', placeholder: 'user@example.com' },
    { value: 'hash', label: 'File Hash', placeholder: 'MD5/SHA1/SHA256' },
    { value: 'cve', label: 'CVE', placeholder: 'CVE-2024-1234' },
  ];

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    if (value.trim()) {
      try {
        await submitArtifact(artifactType, value.trim());
        setValue('');
      } catch (error) {
        console.error('Submit error:', error);
      }
    }
  };

  return (
    <div className="bg-gradient-to-br from-white to-gray-50/50 dark:from-gray-900 dark:to-gray-800/50 border border-gray-200 dark:border-gray-700 rounded-xl p-6 shadow-lg">
      <div className="flex items-center gap-3 mb-6">
        <div className="p-3 bg-gradient-to-br from-blue-100 to-indigo-100 dark:from-blue-900/30 dark:to-indigo-900/30 rounded-xl">
          <Shield className="w-6 h-6 text-blue-600 dark:text-blue-400" />
        </div>
        <div>
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white">Analyze Artifact</h2>
          <p className="text-sm text-gray-600 dark:text-gray-400">Submit IOCs for threat intelligence analysis</p>
        </div>
      </div>

      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Artifact Type
          </label>
          <select
            value={artifactType}
            onChange={(e) => setArtifactType(e.target.value)}
            className="w-full px-4 py-3 border-2 border-gray-300 dark:border-gray-600 rounded-xl bg-white/80 dark:bg-gray-800/80 text-gray-900 dark:text-white focus:ring-4 focus:ring-blue-500/20 dark:focus:ring-blue-400/20 focus:border-blue-500 dark:focus:border-blue-400 backdrop-blur-sm transition-all"
          >
            {artifactTypes.map(type => (
              <option key={type.value} value={type.value}>
                {type.label}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Value
          </label>
          <div className="relative">
            <input
              type="text"
              value={value}
              onChange={(e) => setValue(e.target.value)}
              placeholder={artifactTypes.find(t => t.value === artifactType)?.placeholder}
              className="w-full px-4 py-3 pl-12 border-2 border-gray-300 dark:border-gray-600 rounded-xl bg-white/80 dark:bg-gray-800/80 text-gray-900 dark:text-white focus:ring-4 focus:ring-blue-500/20 dark:focus:ring-blue-400/20 focus:border-blue-500 dark:focus:border-blue-400 backdrop-blur-sm transition-all"
              disabled={loading}
            />
            <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400 dark:text-gray-500" />
          </div>
        </div>

        <button
          type="submit"
          disabled={loading || !value.trim()}
          className="w-full px-6 py-3 bg-gradient-to-r from-blue-600 to-indigo-600 dark:from-blue-500 dark:to-indigo-500 text-white rounded-xl hover:from-blue-700 hover:to-indigo-700 dark:hover:from-blue-600 dark:hover:to-indigo-600 disabled:from-gray-300 disabled:to-gray-400 dark:disabled:from-gray-700 dark:disabled:to-gray-800 disabled:cursor-not-allowed flex items-center justify-center gap-2 shadow-lg hover:shadow-xl transition-all duration-300 transform hover:scale-105 font-medium"
        >
          {loading ? (
            <>
              <Loader2 className="w-5 h-5 animate-spin" />
              Analyzing...
            </>
          ) : (
            <>
              <Shield className="w-5 h-5" />
              Analyze
            </>
          )}
        </button>
      </form>
    </div>
  );
};
