/**
 * Dark mode hook with localStorage persistence
 */

import { useEffect, useState } from 'react';

export const useDarkMode = () => {
  const [isDark, setIsDark] = useState(() => {
    // Check localStorage first
    const stored = localStorage.getItem('darkMode');
    if (stored !== null) {
      return stored === 'true';
    }
    // Default to system preference
    return window.matchMedia('(prefers-color-scheme: dark)').matches;
  });

  useEffect(() => {
    // Ensure document element exists
    const root = document.documentElement;
    if (!root) return;

    // Apply or remove dark mode class
    if (isDark) {
      root.classList.add('dark');
      root.style.colorScheme = 'dark';
    } else {
      root.classList.remove('dark');
      root.style.colorScheme = 'light';
    }

    // Persist to localStorage
    localStorage.setItem('darkMode', isDark ? 'true' : 'false');
  }, [isDark]);

  const toggle = () => {
    setIsDark(prev => !prev);
  };

  const setDark = (value: boolean) => {
    setIsDark(value);
  };

  return { isDark, toggle, setDark };
};
