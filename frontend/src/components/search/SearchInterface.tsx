/**
 * Search interface component
 */

import { useState } from 'react';
import type { FormEvent } from 'react';
import { Search, Loader2, FileText, TrendingUp } from 'lucide-react';
import { useSearchStore } from '../../store/useSearchStore';

export const SearchInterface = () => {
  const [inputValue, setInputValue] = useState('');
  const { results, loading, error, search } = useSearchStore();

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    if (inputValue.trim()) {
      search(inputValue.trim());
    }
  };

  return (
    <div className="space-y-6">
      {/* Search Form */}
      <form onSubmit={handleSubmit} className="w-full">
        <div className="relative group">
          <input
            type="text"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            placeholder="Search across all documents..."
            className="w-full px-5 py-4 pl-14 pr-4 text-lg border-2 border-gray-300 dark:border-gray-700 rounded-xl focus:ring-4 focus:ring-blue-500/20 dark:focus:ring-blue-400/20 focus:border-blue-500 dark:focus:border-blue-400 bg-white/80 dark:bg-gray-900/80 backdrop-blur-sm text-gray-900 dark:text-white shadow-lg transition-all duration-300"
            disabled={loading}
          />
          <div className="absolute left-4 top-1/2 transform -translate-y-1/2 p-2 bg-gradient-to-br from-blue-100 to-indigo-100 dark:from-blue-900/30 dark:to-indigo-900/30 rounded-lg">
            <Search className="w-5 h-5 text-blue-600 dark:text-blue-400" />
          </div>

          {loading && (
            <div className="absolute right-4 top-1/2 transform -translate-y-1/2">
              <div className="absolute inset-0 bg-blue-500/20 rounded-full animate-ping" />
              <Loader2 className="w-6 h-6 text-blue-600 dark:text-blue-400 animate-spin" />
            </div>
          )}
        </div>

        <button
          type="submit"
          disabled={loading || !inputValue.trim()}
          className="mt-4 px-8 py-3 bg-gradient-to-r from-blue-600 to-indigo-600 dark:from-blue-500 dark:to-indigo-500 text-white rounded-xl hover:from-blue-700 hover:to-indigo-700 dark:hover:from-blue-600 dark:hover:to-indigo-600 disabled:from-gray-300 disabled:to-gray-400 dark:disabled:from-gray-700 dark:disabled:to-gray-800 disabled:cursor-not-allowed transition-all duration-300 shadow-lg hover:shadow-xl font-medium transform hover:scale-105"
        >
          {loading ? 'Searching...' : 'Search'}
        </button>
      </form>

      {/* Error */}
      {error && (
        <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4 text-red-800 dark:text-red-400">
          {error}
        </div>
      )}

      {/* Results */}
      {results && (
        <div className="space-y-4">
          <div className="flex items-center justify-between text-sm text-gray-600 dark:text-gray-400">
            <span>
              Found <strong>{results.total_results}</strong> result{results.total_results !== 1 ? 's' : ''}
              {' '}for "<strong>{results.query}</strong>"
            </span>
            <span className="text-xs">
              Model: {results.embedding_model}
            </span>
          </div>

          {results.results.length === 0 ? (
            <div className="text-center py-12 text-gray-500 dark:text-gray-400">
              <Search className="w-16 h-16 mx-auto mb-4 text-gray-300 dark:text-gray-700" />
              <p className="text-lg">No results found</p>
              <p className="text-sm">Try a different search query</p>
            </div>
          ) : (
            <div className="space-y-4">
              {results.results.map((result) => (
                <div
                  key={`${result.document_id}-${result.chunk_index}`}
                  className="group bg-gradient-to-br from-white to-gray-50/50 dark:from-gray-900 dark:to-gray-800/50 border border-gray-200 dark:border-gray-700 rounded-xl p-5 shadow-lg hover:shadow-2xl dark:hover:shadow-gray-900/50 transition-all duration-300 transform hover:scale-[1.01] backdrop-blur-sm"
                >
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex items-center space-x-3">
                      <div className="p-2 bg-gradient-to-br from-blue-100 to-indigo-100 dark:from-blue-900/30 dark:to-indigo-900/30 rounded-lg">
                        <FileText className="w-5 h-5 text-blue-600 dark:text-blue-400" />
                      </div>
                      <h3 className="font-semibold text-gray-900 dark:text-white">
                        {result.document_title}
                      </h3>
                    </div>

                    <div className="flex items-center gap-1.5 px-3 py-1.5 bg-gradient-to-r from-green-100 to-emerald-100 dark:from-green-900/30 dark:to-emerald-900/30 rounded-full">
                      <TrendingUp className="w-4 h-4 text-green-600 dark:text-green-400" />
                      <span className="text-sm font-semibold text-green-700 dark:text-green-300">{(result.relevance_score * 100).toFixed(1)}%</span>
                    </div>
                  </div>

                  <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">
                    {result.document_filename}
                  </p>

                  <p className="text-gray-800 dark:text-gray-300 leading-relaxed">
                    ...{result.snippet}...
                  </p>

                  <div className="mt-2 text-xs text-gray-500 dark:text-gray-400">
                    Chunk {result.chunk_index + 1}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Initial State */}
      {!results && !loading && !error && (
        <div className="text-center py-12 text-gray-500 dark:text-gray-400">
          <Search className="w-16 h-16 mx-auto mb-4 text-gray-300 dark:text-gray-700" />
          <p className="text-lg">Start searching</p>
          <p className="text-sm">Enter a query to search across all your documents</p>
        </div>
      )}
    </div>
  );
};
