export const API_BASE = ""; // Relative to the hosted page (e.g., http://localhost:8000/)

export const api = {
  get: async (url, userId) => {
    const headers = {};
    if (userId) headers['X-User-Id'] = userId;

    const res = await fetch(`${API_BASE}${url}`, { headers });
    if (!res.ok) throw new Error(`API Error: ${res.statusText}`);
    return res.json();
  },

  post: async (url, body, userId) => {
    const headers = { 'Content-Type': 'application/json' };
    if (userId) headers['X-User-Id'] = userId;

    const res = await fetch(`${API_BASE}${url}`, {
      method: 'POST',
      headers,
      body: JSON.stringify(body)
    });
    if (!res.ok) throw new Error(`API Error: ${res.statusText}`);
    return res.json();
  },

  put: async (url, body, userId) => {
    const headers = { 'Content-Type': 'application/json' };
    if (userId) headers['X-User-Id'] = userId;

    const res = await fetch(`${API_BASE}${url}`, {
      method: 'PUT',
      headers,
      body: JSON.stringify(body)
    });
    if (!res.ok) throw new Error(`API Error: ${res.statusText}`);
    return res.json();
  },

  patch: async (url, userId) => {
      const headers = {};
      if (userId) headers['X-User-Id'] = userId;
      const res = await fetch(`${API_BASE}${url}`, {
          method: 'PATCH',
          headers
      });
      if (!res.ok) throw new Error(`API Error: ${res.statusText}`);
      return res; // Might not return JSON
  }
};
