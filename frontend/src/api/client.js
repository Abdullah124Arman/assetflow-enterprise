import { XMLBuilder, XMLParser } from 'fast-xml-parser';

const BASE_URL = 'http://localhost:8000/api';

const parser = new XMLParser({
  ignoreAttributes: false,
  parseTagValue: true
});

const builder = new XMLBuilder({
  ignoreAttributes: false,
  format: true
});

/**
 * Converts a JavaScript object into an XML string.
 * @param {string} rootTag - The root XML tag (e.g., 'User', 'Asset')
 * @param {object} data - The JSON data to convert
 */
export const buildXMLPayload = (rootTag, data) => {
  const obj = { [rootTag]: data };
  return builder.build(obj);
};

async function xmlFetch(endpoint, options = {}) {
  const url = `${BASE_URL}${endpoint}`;
  
  const headers = {
    'Accept': 'application/xml',
    ...options.headers,
  };

  const token = localStorage.getItem('assetflow_token');
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  if (options.body) {
    headers['Content-Type'] = 'application/xml';
  }

  try {
    const response = await fetch(url, {
      ...options,
      headers,
    });

    const text = await response.text();
    
    if (!text) return null;

    const json = parser.parse(text);
    
    if (!response.ok) {
      throw new Error(json.Error?.message || `HTTP Error ${response.status}`);
    }
    
    return json;
  } catch (error) {
    console.error(`API Error on ${endpoint}:`, error);
    throw error;
  }
}

export const api = {
  get: (endpoint) => xmlFetch(endpoint, { method: 'GET' }),
  post: (endpoint, xmlString) => xmlFetch(endpoint, { method: 'POST', body: xmlString }),
  put: (endpoint, xmlString) => xmlFetch(endpoint, { method: 'PUT', body: xmlString }),
  delete: (endpoint) => xmlFetch(endpoint, { method: 'DELETE' }),
};
