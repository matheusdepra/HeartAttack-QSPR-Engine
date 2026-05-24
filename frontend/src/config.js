const env = import.meta.env;

const API_PORT = env.VITE_API_PORT || '5555';
const API_PREFIX = env.VITE_API_PREFIX || '/api';
const STATIC_PREFIX = env.VITE_STATIC_PREFIX || '/plots';
const LOCAL_API_HOST = env.VITE_LOCAL_API_HOST || 'http://localhost';
const STORAGE_USER_KEY = env.VITE_STORAGE_USER_KEY || 'cardio_user';
const APP_NAME = env.VITE_APP_NAME || 'CardioQSPR';
const APP_SHORT_NAME = env.VITE_APP_SHORT_NAME || 'CQ';
const APP_VERSION = env.VITE_APP_VERSION || 'v1.0';

const getApiHost = () => {
  const explicitHost = env.VITE_API_HOST;
  if (explicitHost) {
    return explicitHost.replace(/\/$/, '');
  }

  const { hostname, protocol, port } = window.location;
  const isLocal = hostname === 'localhost' || hostname === '127.0.0.1';

  if (isLocal) {
    return `${LOCAL_API_HOST.replace(/\/$/, '')}:${API_PORT}`;
  }

  const hasPort = port && port !== '80' && port !== '443';
  if (hasPort) {
    return `${protocol}//${hostname}:${API_PORT}`;
  }

  return `${protocol}//${hostname}`;
};

export const API_HOST = getApiHost();
export const API_BASE = `${API_HOST}${API_PREFIX}`;
export const API_STATIC = `${API_HOST}${STATIC_PREFIX}`;
export const USER_STORAGE_KEY = STORAGE_USER_KEY;
export const FRONTEND_APP_NAME = APP_NAME;
export const FRONTEND_APP_SHORT_NAME = APP_SHORT_NAME;
export const FRONTEND_APP_VERSION = APP_VERSION;
