// Base HTTP client — single source of truth for API_BASE and fetch wrapper.
import { API_BASE, API_HOST } from '../config';

export { API_BASE, API_HOST };

/**
 * Generic fetch wrapper with JSON handling and unified error format.
 * Throws an Error with the server's `detail` message on non-2xx responses.
 */
async function request(path, options = {}) {
  const url = `${API_BASE}${path}`;
  const res = await fetch(url, {
    headers: { 'Content-Type': 'application/json', ...options.headers },
    ...options,
  });

  if (!res.ok) {
    let detail = `HTTP ${res.status}`;
    try {
      const body = await res.json();
      detail = body.detail || detail;
    } catch (_) { /* ignore parse error */ }
    throw new Error(detail);
  }

  // 204 No Content — return null
  if (res.status === 204) return null;
  return res.json();
}

export const api = {
  get:    (path)         => request(path, { method: 'GET' }),
  post:   (path, body)   => request(path, { method: 'POST',   body: JSON.stringify(body) }),
  put:    (path, body)   => request(path, { method: 'PUT',    body: JSON.stringify(body) }),
  delete: (path)         => request(path, { method: 'DELETE' }),
};
