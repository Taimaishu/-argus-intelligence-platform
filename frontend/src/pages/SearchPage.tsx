/**
 * Search page
 */

import { SearchInterface } from '../components/search/SearchInterface';

export const SearchPage = () => {
  return (
    <div className="space-y-8">
      <div>
        <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">Intelligence Search</h2>
        <p className="text-gray-600 dark:text-gray-400">
          AI-powered semantic search across your entire intelligence library
        </p>
      </div>

      <SearchInterface />
    </div>
  );
};
