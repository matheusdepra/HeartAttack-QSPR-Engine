// Dynamic host resolution for seamless local development and multi-user OCI deployments
const getApiHost = () => {
  const { hostname, protocol } = window.location;
  
  // If local development, talk to localhost:8000
  if (hostname === 'localhost' || hostname === '127.0.0.1') {
    return 'http://localhost:8000';
  }
  
  // If running directly on OCI using ports (Vite on 5173, backend on 8000)
  const hasPort = window.location.port && window.location.port !== '80' && window.location.port !== '443';
  if (hasPort) {
    return `${protocol}//${hostname}:8000`;
  }
  
  // If Nginx reverse proxy is set up to route requests via port 80/443 without specifying port
  return `${protocol}//${hostname}`;
};

export const API_HOST = getApiHost();
export const API_BASE = `${API_HOST}/api`;
export const API_STATIC = `${API_HOST}/plots`;
