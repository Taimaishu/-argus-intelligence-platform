/**
 * API Key utilities - Manage API keys from localStorage
 */

export interface ApiKeys {
  openai?: string;
  anthropic?: string;
  google?: string;
  unsplash?: string;
  pexels?: string;
}

/**
 * Get all API keys from localStorage
 */
export const getApiKeys = (): ApiKeys => {
  return {
    openai: localStorage.getItem('api_key_openai') || undefined,
    anthropic: localStorage.getItem('api_key_anthropic') || undefined,
    google: localStorage.getItem('api_key_google') || undefined,
    unsplash: localStorage.getItem('api_key_unsplash') || undefined,
    pexels: localStorage.getItem('api_key_pexels') || undefined,
  };
};

/**
 * Get a specific API key
 */
export const getApiKey = (provider: string): string | undefined => {
  return localStorage.getItem(`api_key_${provider}`) || undefined;
};

/**
 * Set an API key
 */
export const setApiKey = (provider: string, key: string): void => {
  if (key) {
    localStorage.setItem(`api_key_${provider}`, key);
  } else {
    localStorage.removeItem(`api_key_${provider}`);
  }
};

/**
 * Clear all API keys (useful for live USB when session ends)
 */
export const clearAllApiKeys = (): void => {
  const keys = ['openai', 'anthropic', 'google', 'unsplash', 'pexels'];
  keys.forEach(key => {
    localStorage.removeItem(`api_key_${key}`);
  });
  localStorage.removeItem('setup_completed');
};

/**
 * Check if any API keys are configured
 */
export const hasAnyApiKeys = (): boolean => {
  const keys = getApiKeys();
  return !!(keys.openai || keys.anthropic || keys.google || keys.unsplash || keys.pexels);
};

/**
 * Get API keys as headers for fetch requests
 */
export const getApiKeyHeaders = (): Record<string, string> => {
  const keys = getApiKeys();
  const headers: Record<string, string> = {};

  if (keys.openai) {
    headers['X-OpenAI-Key'] = keys.openai;
  }
  if (keys.anthropic) {
    headers['X-Anthropic-Key'] = keys.anthropic;
  }
  if (keys.google) {
    headers['X-Google-Key'] = keys.google;
  }
  if (keys.unsplash) {
    headers['X-Unsplash-Key'] = keys.unsplash;
  }
  if (keys.pexels) {
    headers['X-Pexels-Key'] = keys.pexels;
  }

  return headers;
};
