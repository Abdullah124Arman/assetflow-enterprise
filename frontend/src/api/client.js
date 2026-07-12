export class APIError extends Error {
  constructor(code, message, details) {
    super(message);
    this.name = 'APIError';
    this.code = code;
    this.details = details;
  }
}

export const xmlRequest = async (method, endpoint, xmlBody = null, token = null) => {
  const headers = {
    'Accept': 'application/xml',
  };

  if (xmlBody) {
    headers['Content-Type'] = 'application/xml';
  }

  // Fallback to local storage if token not provided directly
  const authToken = token || localStorage.getItem('assetflow_token');
  if (authToken) {
    headers['Authorization'] = `Bearer ${authToken}`;
  }

  const baseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api';
  
  const options = {
    method,
    headers,
  };

  if (xmlBody) {
    options.body = xmlBody;
  }

  const response = await fetch(`${baseUrl}${endpoint}`, options);
  const text = await response.text();
  
  if (!text) return null;

  // Parse XML response securely
  const parser = new DOMParser();
  const xmlDoc = parser.parseFromString(text, "application/xml");
  
  // Check for parse errors
  const parseError = xmlDoc.getElementsByTagName("parsererror");
  if (parseError.length > 0) {
    throw new Error("Invalid XML response from server");
  }

  // Check for standard error envelope: <response><error><code>...</code><message>...</message><details>...</details></error></response>
  const errorNode = xmlDoc.querySelector('response > error');
  if (errorNode) {
    const code = errorNode.querySelector('code')?.textContent || 'UNKNOWN_ERROR';
    const message = errorNode.querySelector('message')?.textContent || 'An error occurred';
    const details = errorNode.querySelector('details')?.textContent || '';
    throw new APIError(code, message, details);
  }

  if (!response.ok) {
    throw new Error(`HTTP Error ${response.status}: ${response.statusText}`);
  }

  return xmlDoc;
};

export const api = {
  get: (endpoint) => xmlRequest('GET', endpoint),
  post: (endpoint, xmlString) => xmlRequest('POST', endpoint, xmlString),
  put: (endpoint, xmlString) => xmlRequest('PUT', endpoint, xmlString),
  delete: (endpoint) => xmlRequest('DELETE', endpoint),
};

