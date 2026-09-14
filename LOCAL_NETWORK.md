# Local Network Deployment Guide

This guide explains how to serve the Training Parser PWA from your laptop to phones on your local network with HTTPS support and full offline functionality.

## Prerequisites

- Python 3.7+ (included in most systems)
- OpenSSL (for generating certificates)
- The laptop and phone must be on the same network

## Quick Start

### 1. Generate SSL Certificates (One-time setup)

```bash
chmod +x scripts/create-ssl-certs.sh
./scripts/create-ssl-certs.sh
```

This creates self-signed certificates in the `certs/` directory. The certificates are valid for 365 days.

**Note:** Self-signed certificates will trigger a security warning in browsers. This is normal and expected for local development.

### 2. Start the HTTPS Server

```bash
python3 scripts/serve-local.py
```

The server will display:
```
==============================================================
Training Parser PWA — Local HTTPS Server
==============================================================

Server running on:
  🔒 https://localhost:8443
  🔒 https://192.168.1.100:8443

To access from another device on your local network:
  📱 https://192.168.1.100:8443

Note: You'll see a security warning (self-signed certificate).
      Click 'Advanced' and 'Proceed anyway' or similar to continue.

First load will cache all necessary files (~30-50 MB).
Subsequent loads work fully offline (no network needed).

Press Ctrl+C to stop the server.
==============================================================
```

### 3. Access from Phone

1. **Copy the URL** from the server output (e.g., `https://192.168.1.100:8443`)
2. **Open it on your phone's browser** (Chrome, Safari, Firefox, etc.)
3. **Accept the security warning** — the certificate is self-signed but safe for local use
4. **Wait for initial load** (~30-50 MB of caches are downloaded)
5. **Close the app** and reopen — it works fully offline now

## How It Works

### HTTPS with Self-Signed Certificates

The `create-ssl-certs.sh` script generates:
- **Self-signed SSL certificate** valid for local IPs and `localhost`
- **2048-bit RSA private key**
- Certificates include Subject Alternative Names (SANs) for:
  - `localhost`
  - `*.local` (mDNS for local domain names)
  - `127.0.0.1` (localhost IP)
  - Your laptop's local IP (e.g., `192.168.1.100`)

HTTPS is required for:
- **Service Workers** — can only be registered over HTTPS (or `localhost`)
- **Offline functionality** — Service Workers cache the entire app for offline use

### Offline-First Architecture

1. **First Load (Connected)**
   - Browser downloads app shell (HTML, CSS, JS) ~1-2 MB
   - Service Worker downloads and caches:
     - Python modules (parser, statistics, ANTLR4 runtime) ~10-15 MB
     - Pyodide runtime (Python in WebAssembly) ~20-30 MB
     - CDN libraries (isomorphic-git, LightningFS) ~2-3 MB
   - Browser caches everything with **cache-first strategy**
   - Total first load: 30-50 MB over network

2. **Subsequent Loads (Offline or Online)**
   - Service Worker serves **everything from cache**
   - No network requests needed
   - App is instant (~100ms load time)
   - Can use for hours or days without network

3. **Cache Strategy**
   - **App shell (HTML, CSS, JS):** Cached, revalidated daily
   - **Service Worker & manifest:** Cached hourly (important for updates)
   - **Python modules:** Cached permanently (updated via cache refresh)
   - **Pyodide runtime:** Cached permanently
   - **New requests:** Cached when available

## Server Configuration

The `serve-local.py` script accepts command-line options:

```bash
# Use default (0.0.0.0:8443)
python3 scripts/serve-local.py

# Custom port
python3 scripts/serve-local.py --port 9443

# Custom certificate location
python3 scripts/serve-local.py --cert mycert.pem --key mykey.pem

# Bind to specific address
python3 scripts/serve-local.py --host 192.168.1.100 --port 8443
```

## Security Considerations

### Self-Signed Certificates

Self-signed certificates are **safe for local development** but:
- ❌ Not trusted by browsers (shows warning)
- ❌ Not valid for public internet
- ✅ Provide encryption for local network traffic
- ✅ Enable Service Workers (required for offline)

### Network Security

The server:
- Runs on your **local network only** (0.0.0.0:8443)
- Is **not exposed to the internet** by default
- Requires explicit firewall rule to reach outside your network
- Has CORS enabled for local development

### To Disable Self-Signed Certificate Warnings

On **Android Chrome:**
1. Open Settings → Site settings → Insecure content
2. Allow insecure content for the site

On **iOS Safari:**
1. Open Settings → General → About
2. Scroll to the TLS certificate
3. Tap it and trust the certificate

## Troubleshooting

### "Cannot connect to server"

- **Check laptop IP:** `hostname -I` (Linux/Mac) or `ipconfig` (Windows)
- **Verify server is running:** Look for "Server running on" message
- **Check firewall:** Ensure port 8443 is not blocked
- **Try localhost:** Access `https://localhost:8443` from the laptop

### "Certificate error / Security warning"

This is **normal and expected** for self-signed certificates. Click:
- Chrome: "Advanced" → "Proceed anyway"
- Firefox: "Advanced" → "Accept the Risk and Continue"
- Safari: "Visit Website"
- Edge: "Details" → "Go on to the webpage"

### "App not loading / Stuck at 'Python runtime loading'"

1. **Check browser console:** Press F12, go to Console tab
2. **Check Network tab:** Verify files are downloading
3. **Hard refresh:** Ctrl+Shift+R (or Cmd+Shift+R on Mac)
4. **Clear cache:**
   - Chrome: Settings → Privacy → Clear browsing data → All time
   - Safari: Develop → Empty Web Storage

### Certificates expired

```bash
# Remove old certificates
rm -rf certs/

# Generate new ones (valid 365 days from now)
./scripts/create-ssl-certs.sh
```

## Using with Git Sync

To enable git sync over local network:

1. In Settings, enter:
   - **Git remote URL:** Your GitHub/GitLab repo
   - **Username:** Your git username
   - **Token:** Personal access token from GitHub/GitLab
   - **Author:** Name for commits

2. The app stores credentials **locally** (not sent anywhere)
3. Commits are pushed via CORS proxy (`cors.isomorphic-git.org`)

## Production Deployment

For public hosting, use:

### GitHub Pages (Free)

```bash
# Build and publish to GitHub Pages
make pwa-build
make pwa-publish
```

Your PWA becomes available at: `https://username.github.io/training-parser-antlr4/`

### Self-Hosted Server

For your own domain, use a proper SSL certificate from a provider:

```bash
# Use production-grade certificates (not self-signed)
python3 scripts/serve-local.py \
  --cert /etc/letsencrypt/live/example.com/fullchain.pem \
  --key /etc/letsencrypt/live/example.com/privkey.pem
```

## Advanced Topics

### Updating the App

The Service Worker caches everything. To update:

1. **Manual cache clear:**
   - Developer Console → Application → Cache → Clear Storage
   - Hard refresh (Ctrl+Shift+R)

2. **Automatic update (Web Manifest):**
   - The manifest.json controls update frequency
   - Service Worker checks every 24 hours

### Monitoring Offline Usage

1. Open DevTools (F12)
2. Go to **Application** → **Service Workers**
3. Check "Offline" checkbox
4. Reload page — app works without network

### Checking Cache Size

1. DevTools → **Application** → **Storage**
2. Shows total cache size (30-50 MB)
3. Lists all cached files

### Logs and Debugging

1. **Browser Console:**
   - Service Worker logs: F12 → Console
   - Filter by level: DEBUG, INFO, WARN, ERROR

2. **Server Logs:**
   - Watch `serve-local.py` output
   - Shows all requests with timestamps

## Performance Tips

### Faster First Load

1. **Ensure good WiFi signal:** Reduces timeout risk
2. **Close other downloads:** Prevents bandwidth contention
3. **Wait for "Loaded N/N files":** Indicates caching complete
4. **Refresh page once:** Ensures all caches are warm

### Offline Performance

1. **Index your workouts:** Keep track of locally stored exercises
2. **Use localStorage:** Automatically persists between sessions
3. **Avoid large files:** App works best with typical workout data

### Network Efficiency

- **First load:** ~50 MB (mostly Pyodide runtime)
- **Subsequent loads:** 0 KB (everything cached)
- **App operations:** <1 KB per parse/statistics call
- **Git sync:** Network used only when pushing to remote

## FAQ

**Q: Can I use this over the internet (not just local network)?**  
A: Not safely with self-signed certificates. For public internet, use GitHub Pages (`make pwa-publish`) or your own domain with proper SSL.

**Q: How long does offline functionality last?**  
A: Forever. Once cached, the app works indefinitely without network. LocalStorage persists data until you clear it.

**Q: Can multiple phones use the same server?**  
A: Yes. The server accepts unlimited connections. Each phone caches independently.

**Q: Does the server need to keep running?**  
A: No. After first load, each phone has full offline functionality. You can stop the server with Ctrl+C.

**Q: How do I update the app on phones?**  
A: Hard refresh (Ctrl+Shift+R) or clear Service Worker cache in browser settings.

**Q: Can I use this without creating certificates?**  
A: Not over network. Certificates are required for HTTPS, which Service Workers demand. Local `localhost` works without HTTPS on some browsers.

## Support

For issues:

1. Check the troubleshooting section above
2. Open browser DevTools (F12) and check Console
3. Review `scripts/create-ssl-certs.sh` for certificate issues
4. Check `scripts/serve-local.py` for server issues
