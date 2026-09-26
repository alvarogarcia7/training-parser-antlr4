#!/usr/bin/env node
/**
 * Simple git HTTP server with CORS support
 * Serves git repositories with smart HTTP protocol
 */

const http = require('http');
const { execSync, spawn } = require('child_process');
const path = require('path');
const url = require('url');
const fs = require('fs');

const GIT_REPO_ROOT = '/tmp/git-server';
const PORT = 8888;

const server = http.createServer((req, res) => {
  // Add CORS headers to all responses
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, HEAD, OPTIONS, PUT, DELETE');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Authorization, Accept');
  res.setHeader('Access-Control-Max-Age', '86400');

  // Handle preflight requests
  if (req.method === 'OPTIONS') {
    res.writeHead(200);
    res.end();
    return;
  }

  console.log(`[git-http] ${req.method} ${req.url}`);

  const parsedUrl = url.parse(req.url);
  const pathname = parsedUrl.pathname;

  // Route git operations
  if (pathname.match(/\.git\/(info\/refs|git-upload-pack|git-receive-pack)/)) {
    handleGitRequest(req, res, pathname);
  } else if (pathname === '/' || pathname === '') {
    res.writeHead(200, { 'Content-Type': 'text/plain' });
    res.end('Git HTTP Server - Available repositories:\n- /test-repo.git\n');
  } else {
    res.writeHead(404, { 'Content-Type': 'text/plain' });
    res.end('Not Found: ' + pathname);
  }
});

function handleGitRequest(req, res, pathname) {
  try {
    // Extract repo name and git path
    const match = pathname.match(/^\/(.+?\.git)(\/.*)?$/);
    if (!match) {
      res.writeHead(404);
      res.end('Not found');
      return;
    }

    const repoName = match[1];
    const gitPath = match[2] || '';
    const repoPath = path.join(GIT_REPO_ROOT, repoName);

    // Security: prevent path traversal
    if (!path.resolve(repoPath).startsWith(GIT_REPO_ROOT)) {
      res.writeHead(403);
      res.end('Forbidden');
      return;
    }

    // Verify repo exists
    if (!fs.existsSync(repoPath)) {
      res.writeHead(404);
      res.end('Repository not found');
      return;
    }

    // Set up environment for git-http-backend
    const env = Object.assign({}, process.env, {
      REQUEST_METHOD: req.method,
      PATH_INFO: '/' + repoName + gitPath,
      QUERY_STRING: url.parse(req.url).query || '',
      CONTENT_TYPE: req.headers['content-type'] || 'application/octet-stream',
      CONTENT_LENGTH: req.headers['content-length'] || '0',
      GIT_PROJECT_ROOT: GIT_REPO_ROOT,
      GIT_HTTP_EXPORT_ALL: '1',
      REMOTE_USER: 'anonymous',
    });

    // Run git-http-backend
    const proc = spawn('git', ['http-backend'], { env, cwd: GIT_REPO_ROOT });

    let gitOutput = Buffer.alloc(0);
    let gitError = '';

    proc.stdout.on('data', (chunk) => {
      gitOutput = Buffer.concat([gitOutput, chunk]);
    });

    proc.stderr.on('data', (chunk) => {
      gitError += chunk.toString();
    });

    // Forward request body to git-http-backend
    req.on('data', (chunk) => {
      proc.stdin.write(chunk);
    });

    req.on('end', () => {
      proc.stdin.end();
    });

    proc.on('close', (code) => {
      if (gitError) {
        console.error(`[git-http] Git error: ${gitError}`);
      }

      // Parse git-http-backend response
      const responseStr = gitOutput.toString('utf8');
      const headerEnd = responseStr.indexOf('\r\n\r\n');

      if (headerEnd !== -1) {
        const gitHeaders = responseStr.substring(0, headerEnd);
        const gitBody = gitOutput.slice(headerEnd + 4);

        // Parse git headers and set response
        const lines = gitHeaders.split('\r\n');
        let statusCode = 200;
        const resHeaders = {};

        for (const line of lines) {
          if (line.startsWith('Status: ')) {
            statusCode = parseInt(line.substring(8));
          } else if (line.includes(':')) {
            const [key, val] = line.split(': ', 2);
            resHeaders[key.toLowerCase()] = val;
          }
        }

        res.writeHead(statusCode, resHeaders);
        res.end(gitBody);
      } else {
        // No valid git response
        res.writeHead(200, { 'Content-Type': 'application/x-git-upload-pack-result' });
        res.end(gitOutput);
      }
    });

  } catch (err) {
    console.error(`[git-http] Error: ${err.message}`);
    res.writeHead(500, { 'Content-Type': 'text/plain' });
    res.end('Internal Server Error: ' + err.message);
  }
}

server.listen(PORT, '0.0.0.0', () => {
  console.log(`\n✅ Git HTTP Server running on http://localhost:${PORT}`);
  console.log(`📁 Repository root: ${GIT_REPO_ROOT}`);
  console.log(`📦 Available at: http://localhost:${PORT}/test-repo.git\n`);
  console.log('Usage:');
  console.log('  git clone http://localhost:8888/test-repo.git');
  console.log('  or from PWA with CORS proxy:');
  console.log('  http://localhost:8081/http://localhost:8888/test-repo.git\n');
});

server.on('error', (err) => {
  if (err.code === 'EADDRINUSE') {
    console.error(`❌ Port ${PORT} already in use`);
  } else {
    console.error(`❌ Server error: ${err.message}`);
  }
  process.exit(1);
});
