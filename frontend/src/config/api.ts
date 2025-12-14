/**
 * Centralized API configuration
 * Uses relative URLs in development (proxied by Vite) or absolute URL from env var in production
 */

export const API_CONFIG = {
  BASE_URL: import.meta.env.VITE_API_URL || '',
  ENDPOINTS: {
    // Documents
    DOCUMENTS: '/api/documents',
    DOCUMENTS_UPLOAD: '/api/documents/upload',

    // Search
    SEARCH: '/api/search',

    // Chat
    CHAT_SESSIONS: '/api/chat/sessions',

    // OSINT
    OSINT_ARTIFACTS: '/api/osint/artifacts',
    OSINT_ANALYZE: '/api/osint/analyze',
    OSINT_EXTRACT: '/api/osint/extract',
    OSINT_SCRAPE: '/api/osint/scrape',
    OSINT_STATS: '/api/osint/stats',

    // Canvas
    CANVAS: '/api/canvas',

    // Patterns
    PATTERNS_NETWORK: '/api/patterns/network',
    PATTERNS_CLUSTER: '/api/patterns/cluster',
    PATTERNS_INSIGHTS: '/api/patterns/insights',

    // Models
    MODELS_PROVIDERS_STATUS: '/api/models/providers/status',
    MODELS_OLLAMA_LIST: '/api/models/ollama/list',
    MODELS_OLLAMA_PULL: '/api/models/ollama/pull',

    // Health
    HEALTH: '/health',
  }
};

/**
 * Get full URL for an endpoint
 */
export const getApiUrl = (endpoint: string): string => {
  return `${API_CONFIG.BASE_URL}${endpoint}`;
};
