/**
 * Utility functions for managing API keys in sessionStorage
 */

const STORAGE_KEY = 'bpmn_api_keys';

/**
 * Get API keys from sessionStorage
 * @returns {Object} Object containing API keys (openai_api_key, anthropic_api_key, etc.)
 */
export function getApiKeys() {
  const stored = sessionStorage.getItem(STORAGE_KEY);
  if (!stored) {
    return {};
  }

  try {
    return JSON.parse(stored);
  } catch (e) {
    console.error('Failed to parse stored API keys', e);
    return {};
  }
}

/**
 * Check if any API keys are stored
 * @returns {boolean}
 */
export function hasApiKeys() {
  const keys = getApiKeys();
  return Object.keys(keys).length > 0;
}

/**
 * Save API keys to sessionStorage
 * @param {Object} keys - Object containing API keys
 */
export function saveApiKeys(keys) {
  sessionStorage.setItem(STORAGE_KEY, JSON.stringify(keys));
}

/**
 * Clear all API keys from sessionStorage
 */
export function clearApiKeys() {
  sessionStorage.removeItem(STORAGE_KEY);
}
