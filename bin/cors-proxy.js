#!/usr/bin/env node
/**
 * Simple CORS proxy for development
 * Usage: node cors-proxy.js
 * Proxy URL format: http://localhost:8081/http://example.com/path
 */

const http = require('http');
const https = require('https');
const url = require('url');

const PORT = 8081;

const server = http.createServer((req, res) => {
  // Add CORS headers
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, HEAD, OPTIONS, PUT, DELETE');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Authorization, Accept');
  res.setHeader('Access-Control-Max-Age', '86400');

  if (req.method === 'OPTIONS') {
    res.writeHead(200);
    res.end();
    return;
  }

  // Extract target URL from request path
  const pathname = req.url.substring(1); // Remove leading /
  if (!pathname.startsWith('http://') && !pathname.startsWith('https://')) {
    res.writeHead(400, { 'Content-Type': 'text/plain' });
    res.end('CORS Proxy\n\nUsage: /' + 'http://example.com/path');
    return;
  }

  console.log(`[CORS] ${req.method} ${pathname}`);

  // Parse target URL
  let targetUrl;
  try {
    targetUrl = new URL(pathname);
  } catch (e) {
    res.writeHead(400, { 'Content-Type': 'text/plain' });
    res.end('Invalid URL: ' + pathname);
    return;
  }

  // Prepare headers
  const reqHeaders = { ...req.headers };
  delete reqHeaders['host'];

  // Choose HTTP or HTTPS
  const client = targetUrl.protocol === 'https:' ? https : http;

  // Make request to target
  const options = {
    method: req.method,
    headers: reqHeaders,
  };

  const proxyReq = client.request(targetUrl, options, (proxyRes) => {
    // Forward response headers (except hop-by-hop headers)
    const skipHeaders = ['connection', 'content-encoding', 'content-length', 'transfer-encoding'];
    const resHeaders = {};

    for (const [key, value] of Object.entries(proxyRes.headers)) {
      if (!skipHeaders.includes(key.toLowerCase())) {
        resHeaders[key] = value;
      }
    }

    // Add CORS headers
    resHeaders['Access-Control-Allow-Origin'] = '*';

    res.writeHead(proxyRes.statusCode, resHeaders);
    proxyRes.pipe(res);
  });

  proxyReq.on('error', (err) => {
    console.error(`[CORS] Error: ${err.message}`);
    res.writeHead(502, { 'Content-Type': 'text/plain' });
    res.end(`Proxy error: ${err.message}`);
  });

  // Forward request body
  req.pipe(proxyReq);
});

server.listen(PORT, 'localhost', () => {
  console.log(`\n✅ CORS Proxy listening on http://localhost:${PORT}`);
  console.log(`📌 Format: http://localhost:${PORT}/http://target.com/path`);
  console.log(`   Example: http://localhost:${PORT}/http://localhost:8888/test-repo.git/info/refs\n`);
});

server.on('error', (err) => {
  if (err.code === 'EADDRINUSE') {
    console.error(`❌ Port ${PORT} already in use`);
  } else {
    console.error(`❌ Error: ${err.message}`);
  }
  process.exit(1);
});
