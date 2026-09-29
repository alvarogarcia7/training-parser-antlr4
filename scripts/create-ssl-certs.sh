#!/bin/bash
# Generate self-signed SSL certificates for local HTTPS development
# Usage: ./scripts/create-ssl-certs.sh
#
# Strict mode: exit on error, undefined variables, or pipe failures
set -euo pipefail

CERT_DIR="certs"
CERT_FILE="${CERT_DIR}/cert.pem"
KEY_FILE="${CERT_DIR}/key.pem"
DAYS=365

# Verify prerequisites
if ! command -v openssl &> /dev/null; then
    echo "❌ Error: openssl is not installed"
    echo "   On Ubuntu/Debian: sudo apt-get install openssl"
    echo "   On macOS: brew install openssl"
    echo "   On Windows: install OpenSSL or use WSL"
    exit 1
fi

# Verify we can write to current directory
if ! touch .test-write-permission 2>/dev/null; then
    echo "❌ Error: Cannot write to current directory"
    echo "   Run from a directory where you have write permissions"
    exit 1
fi
rm -f .test-write-permission

# Create certs directory
if ! mkdir -p "${CERT_DIR}"; then
    echo "❌ Error: Failed to create ${CERT_DIR} directory"
    exit 1
fi

# Verify directory is writable
if ! touch "${CERT_DIR}/.test-write" 2>/dev/null; then
    echo "❌ Error: Cannot write to ${CERT_DIR} directory"
    exit 1
fi
rm -f "${CERT_DIR}/.test-write"

if [ -f "${CERT_FILE}" ] && [ -f "${KEY_FILE}" ]; then
    echo "✓ Certificates already exist at ${CERT_FILE} and ${KEY_FILE}"
    echo "  To regenerate, delete the certs directory: rm -rf ${CERT_DIR}/"
    exit 0
fi

echo "Generating self-signed SSL certificates for local HTTPS..."
echo "This certificate is for development only and will NOT be trusted by browsers."
echo "You'll need to accept the security warning when connecting."
echo ""

# Get local IP address with fallback (cross-platform: Mac and Linux)
LOCAL_IP=""

# Try hostname -I (Linux)
if command -v hostname &> /dev/null; then
    LOCAL_IP=$(hostname -I 2>/dev/null | awk '{print $1}' || true)
fi

# Try ifconfig (Mac and Linux) - extract inet address using portable sed/awk
if [ -z "$LOCAL_IP" ] && command -v ifconfig &> /dev/null; then
    # Extract first non-loopback inet address (works on both macOS and Linux)
    LOCAL_IP=$(ifconfig 2>/dev/null | grep "inet " | grep -v "127.0.0.1" | head -1 | sed 's/^.*inet \([0-9.]*\).*/\1/' || true)
fi

# Final fallback for systems without hostname/ifconfig
if [ -z "$LOCAL_IP" ]; then
    LOCAL_IP="192.168.1.100"
fi

echo "Local IP address detected: ${LOCAL_IP}"
echo "Certificates will be valid for:"
echo "  - localhost"
echo "  - 127.0.0.1"
echo "  - ${LOCAL_IP}"
echo ""

# Create certificate with Subject Alternative Names
if ! openssl req -x509 -newkey rsa:2048 \
    -keyout "${KEY_FILE}" \
    -out "${CERT_FILE}" \
    -days "${DAYS}" \
    -nodes \
    -subj "/CN=localhost" \
    -addext "subjectAltName=DNS:localhost,DNS:*.local,IP:127.0.0.1,IP:${LOCAL_IP}" 2>&1; then
    echo "❌ Error: Failed to generate certificate"
    rm -f "${CERT_FILE}" "${KEY_FILE}"
    exit 1
fi

# Verify generated files exist and are readable
if [ ! -f "${CERT_FILE}" ]; then
    echo "❌ Error: Certificate file was not created: ${CERT_FILE}"
    exit 1
fi

if [ ! -f "${KEY_FILE}" ]; then
    echo "❌ Error: Key file was not created: ${KEY_FILE}"
    rm -f "${CERT_FILE}"
    exit 1
fi

if [ ! -r "${CERT_FILE}" ] || [ ! -r "${KEY_FILE}" ]; then
    echo "❌ Error: Generated files are not readable"
    exit 1
fi

echo ""
echo "✓ Certificates created successfully!"
echo "  Certificate: ${CERT_FILE} ($(stat -f%z "${CERT_FILE}" 2>/dev/null || stat -c%s "${CERT_FILE}" 2>/dev/null || echo "created") bytes)"
echo "  Private key: ${KEY_FILE} ($(stat -f%z "${KEY_FILE}" 2>/dev/null || stat -c%s "${KEY_FILE}" 2>/dev/null || echo "created") bytes)"
echo ""
echo "Next steps:"
echo "  1. Start the HTTPS server: python3 scripts/serve-local.py"
echo "  2. On your phone, open: https://${LOCAL_IP}:8443"
echo "  3. Accept the security warning (self-signed certificate)"
echo "  4. The app will load and cache everything for offline use"
echo ""
echo "Note: The certificate is valid for ${DAYS} days."
echo "To regenerate: rm -rf ${CERT_DIR}/ && ./scripts/create-ssl-certs.sh"
