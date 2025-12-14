/**
 * Header component
 */

import { Link } from 'react-router-dom';
import { Search, Moon, Sun, MessageSquare, Shield, Network, Sparkles } from 'lucide-react';
import { useDarkMode } from '../../hooks/useDarkMode';

export const Header = () => {
  const { isDark, toggle } = useDarkMode();

  return (
    <header className="bg-gradient-to-r from-blue-600 to-indigo-600 dark:from-blue-900 dark:to-indigo-900 shadow-lg">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          <div className="flex items-center space-x-3">
            <div className="p-2 bg-white/10 rounded-lg backdrop-blur-sm">
              <Shield className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-xl font-bold text-white">
                Argus
              </h1>
              <p className="text-xs text-white/70 -mt-1">Intelligence Platform</p>
            </div>
          </div>

          <nav className="flex items-center space-x-2">
            <Link
              to="/"
              className="px-4 py-2 rounded-lg text-sm font-medium text-white/90 hover:text-white hover:bg-white/10 backdrop-blur-sm transition-all"
            >
              Documents
            </Link>
            <Link
              to="/search"
              className="px-4 py-2 rounded-lg text-sm font-medium text-white/90 hover:text-white hover:bg-white/10 backdrop-blur-sm flex items-center gap-2 transition-all"
            >
              <Search className="w-4 h-4" />
              Search
            </Link>
            <Link
              to="/osint"
              className="px-4 py-2 rounded-lg text-sm font-medium text-white/90 hover:text-white hover:bg-white/10 backdrop-blur-sm flex items-center gap-2 transition-all"
            >
              <Shield className="w-4 h-4" />
              OSINT
            </Link>
            <Link
              to="/canvas"
              className="px-4 py-2 rounded-lg text-sm font-medium text-white/90 hover:text-white hover:bg-white/10 backdrop-blur-sm flex items-center gap-2 transition-all"
            >
              <Network className="w-4 h-4" />
              Canvas
            </Link>
            <Link
              to="/patterns"
              className="px-4 py-2 rounded-lg text-sm font-medium text-white/90 hover:text-white hover:bg-white/10 backdrop-blur-sm flex items-center gap-2 transition-all"
            >
              <Sparkles className="w-4 h-4" />
              Patterns
            </Link>
            <Link
              to="/chat"
              className="px-4 py-2 rounded-lg text-sm font-medium text-white/90 hover:text-white hover:bg-white/10 backdrop-blur-sm flex items-center gap-2 transition-all"
            >
              <MessageSquare className="w-4 h-4" />
              Chat
            </Link>
            <button
              onClick={toggle}
              className="p-2 rounded-lg text-white/90 hover:text-white hover:bg-white/10 backdrop-blur-sm ml-2 transition-all"
              aria-label="Toggle dark mode"
            >
              {isDark ? <Sun className="w-5 h-5" /> : <Moon className="w-5 h-5" />}
            </button>
          </nav>
        </div>
      </div>
    </header>
  );
};
