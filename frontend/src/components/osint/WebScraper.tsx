/**
 * Web scraping component
 */

import { useState } from 'react';
import type { FormEvent } from 'react';
import { Globe, Loader2, Mail, Phone, Hash, Code, Image as ImageIcon, Link as LinkIcon } from 'lucide-react';

export const WebScraper = () => {
  const [url, setUrl] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    if (!url.trim()) return;

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const response = await fetch('http://localhost:8000/api/osint/scrape', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url: url.trim() })
      });

      if (!response.ok) throw new Error('Scraping failed');

      const data = await response.json();
      setResult(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to scrape URL');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Scrape Form */}
      <div className="bg-gradient-to-br from-white to-gray-50/50 dark:from-gray-900 dark:to-gray-800/50 border border-gray-200 dark:border-gray-700 rounded-xl p-6 shadow-lg">
        <div className="flex items-center gap-3 mb-6">
          <div className="p-3 bg-gradient-to-br from-green-100 to-emerald-100 dark:from-green-900/30 dark:to-emerald-900/30 rounded-xl">
            <Globe className="w-6 h-6 text-green-600 dark:text-green-400" />
          </div>
          <div>
            <h2 className="text-2xl font-bold text-gray-900 dark:text-white">Web Scraper</h2>
            <p className="text-sm text-gray-600 dark:text-gray-400">Extract intelligence from any website</p>
          </div>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="relative">
            <input
              type="url"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              placeholder="https://example.com"
              className="w-full px-4 py-3 pl-12 border-2 border-gray-300 dark:border-gray-600 rounded-xl bg-white/80 dark:bg-gray-800/80 text-gray-900 dark:text-white focus:ring-4 focus:ring-green-500/20 dark:focus:ring-green-400/20 focus:border-green-500 dark:focus:border-green-400 backdrop-blur-sm transition-all"
              disabled={loading}
            />
            <Globe className="absolute left-4 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400 dark:text-gray-500" />
          </div>

          <button
            type="submit"
            disabled={loading || !url.trim()}
            className="w-full px-6 py-3 bg-gradient-to-r from-green-600 to-emerald-600 dark:from-green-500 dark:to-emerald-500 text-white rounded-xl hover:from-green-700 hover:to-emerald-700 dark:hover:from-green-600 dark:hover:to-emerald-600 disabled:from-gray-300 disabled:to-gray-400 dark:disabled:from-gray-700 dark:disabled:to-gray-800 disabled:cursor-not-allowed flex items-center justify-center gap-2 shadow-lg hover:shadow-xl transition-all duration-300 transform hover:scale-105 font-medium"
          >
            {loading ? (
              <>
                <Loader2 className="w-5 h-5 animate-spin" />
                Scraping...
              </>
            ) : (
              <>
                <Globe className="w-5 h-5" />
                Scrape Website
              </>
            )}
          </button>
        </form>
      </div>

      {/* Error */}
      {error && (
        <div className="bg-gradient-to-r from-red-50 to-rose-50 dark:from-red-900/20 dark:to-rose-900/20 border border-red-200 dark:border-red-800 rounded-xl p-4 text-red-800 dark:text-red-400">
          {error}
        </div>
      )}

      {/* Results */}
      {result && (
        <div className="space-y-4">
          {/* Basic Info */}
          <div className="bg-gradient-to-br from-white to-gray-50/50 dark:from-gray-900 dark:to-gray-800/50 border border-gray-200 dark:border-gray-700 rounded-xl p-6 shadow-lg">
            <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-4">Page Information</h3>

            {result.title && (
              <div className="mb-3">
                <span className="text-sm font-medium text-gray-500 dark:text-gray-400">Title:</span>
                <p className="text-lg font-semibold text-gray-900 dark:text-white">{result.title}</p>
              </div>
            )}

            {result.description && (
              <div className="mb-3">
                <span className="text-sm font-medium text-gray-500 dark:text-gray-400">Description:</span>
                <p className="text-gray-700 dark:text-gray-300">{result.description}</p>
              </div>
            )}

            <div className="flex flex-wrap gap-2 mt-4">
              <span className="px-3 py-1 bg-blue-100 dark:bg-blue-900/30 text-blue-800 dark:text-blue-300 rounded-full text-sm">
                Status: {result.status_code}
              </span>
              {result.word_count && (
                <span className="px-3 py-1 bg-purple-100 dark:bg-purple-900/30 text-purple-800 dark:text-purple-300 rounded-full text-sm">
                  {result.word_count} words
                </span>
              )}
            </div>
          </div>

          {/* Technologies */}
          {result.technologies && result.technologies.length > 0 && (
            <div className="bg-gradient-to-br from-white to-gray-50/50 dark:from-gray-900 dark:to-gray-800/50 border border-gray-200 dark:border-gray-700 rounded-xl p-6 shadow-lg">
              <div className="flex items-center gap-2 mb-4">
                <Code className="w-5 h-5 text-indigo-600 dark:text-indigo-400" />
                <h3 className="text-lg font-bold text-gray-900 dark:text-white">Technologies Detected</h3>
              </div>
              <div className="flex flex-wrap gap-2">
                {result.technologies.map((tech: string, i: number) => (
                  <span key={i} className="px-3 py-1 bg-indigo-100 dark:bg-indigo-900/30 text-indigo-800 dark:text-indigo-300 rounded-full text-sm font-medium">
                    {tech}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Emails & Phones */}
          {((result.emails && result.emails.length > 0) || (result.phones && result.phones.length > 0)) && (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {result.emails && result.emails.length > 0 && (
                <div className="bg-gradient-to-br from-white to-gray-50/50 dark:from-gray-900 dark:to-gray-800/50 border border-gray-200 dark:border-gray-700 rounded-xl p-6 shadow-lg">
                  <div className="flex items-center gap-2 mb-3">
                    <Mail className="w-5 h-5 text-blue-600 dark:text-blue-400" />
                    <h3 className="text-lg font-bold text-gray-900 dark:text-white">Emails ({result.emails.length})</h3>
                  </div>
                  <div className="space-y-1">
                    {result.emails.slice(0, 10).map((email: string, i: number) => (
                      <code key={i} className="block text-sm text-gray-700 dark:text-gray-300 font-mono">{email}</code>
                    ))}
                  </div>
                </div>
              )}

              {result.phones && result.phones.length > 0 && (
                <div className="bg-gradient-to-br from-white to-gray-50/50 dark:from-gray-900 dark:to-gray-800/50 border border-gray-200 dark:border-gray-700 rounded-xl p-6 shadow-lg">
                  <div className="flex items-center gap-2 mb-3">
                    <Phone className="w-5 h-5 text-green-600 dark:text-green-400" />
                    <h3 className="text-lg font-bold text-gray-900 dark:text-white">Phones ({result.phones.length})</h3>
                  </div>
                  <div className="space-y-1">
                    {result.phones.slice(0, 10).map((phone: string, i: number) => (
                      <code key={i} className="block text-sm text-gray-700 dark:text-gray-300 font-mono">{phone}</code>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Social Media */}
          {result.social_media && Object.keys(result.social_media).length > 0 && (
            <div className="bg-gradient-to-br from-white to-gray-50/50 dark:from-gray-900 dark:to-gray-800/50 border border-gray-200 dark:border-gray-700 rounded-xl p-6 shadow-lg">
              <div className="flex items-center gap-2 mb-4">
                <Hash className="w-5 h-5 text-pink-600 dark:text-pink-400" />
                <h3 className="text-lg font-bold text-gray-900 dark:text-white">Social Media</h3>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                {Object.entries(result.social_media).map(([platform, urls]: [string, any]) => (
                  <div key={platform} className="p-3 bg-gray-50 dark:bg-gray-800 rounded-lg">
                    <p className="font-semibold text-gray-900 dark:text-white capitalize mb-1">{platform}</p>
                    {urls.slice(0, 3).map((url: string, i: number) => (
                      <a key={i} href={url} target="_blank" rel="noopener noreferrer" className="block text-sm text-blue-600 dark:text-blue-400 hover:underline truncate">
                        {url}
                      </a>
                    ))}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Links & Images Stats */}
          <div className="grid grid-cols-2 gap-4">
            {result.links && (
              <div className="bg-gradient-to-br from-white to-gray-50/50 dark:from-gray-900 dark:to-gray-800/50 border border-gray-200 dark:border-gray-700 rounded-xl p-6 shadow-lg text-center">
                <LinkIcon className="w-8 h-8 text-blue-600 dark:text-blue-400 mx-auto mb-2" />
                <p className="text-3xl font-bold text-gray-900 dark:text-white">{result.links.length}</p>
                <p className="text-sm text-gray-600 dark:text-gray-400">Links Found</p>
              </div>
            )}

            {result.images && (
              <div className="bg-gradient-to-br from-white to-gray-50/50 dark:from-gray-900 dark:to-gray-800/50 border border-gray-200 dark:border-gray-700 rounded-xl p-6 shadow-lg text-center">
                <ImageIcon className="w-8 h-8 text-purple-600 dark:text-purple-400 mx-auto mb-2" />
                <p className="text-3xl font-bold text-gray-900 dark:text-white">{result.images.length}</p>
                <p className="text-sm text-gray-600 dark:text-gray-400">Images Found</p>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};
