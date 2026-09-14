#!/bin/bash
# Generate self-signed SSL certificates for local HTTPS development
# Usage: ./scripts/create-ssl-certs.sh

set -e

CERT_DIR="certs"
CERT_FILE="${CERT_DIR}/cert.pem"
KEY_FILE="${CERT_DIR}/key.pem"
DAYS=365

mkdir -p "${CERT_DIR}"

if [ -f "${CERT_FILE}" ] && [ -f "${KEY_FILE}" ]; then
    echo "✓ Certificates already exist at ${CERT_FILE} and ${KEY_FILE}"
    echo "  To regenerate, delete the certs directory: rm -rf ${CERT_DIR}/"
    exit 0
fi

echo "Generating self-signed SSL certificates for local HTTPS..."
echo "This certificate is for development only and will NOT be trusted by browsers."
echo "You'll need to accept the security warning when connecting."
echo ""

# Get local IP address
LOCAL_IP=$(hostname -I | awk '{print $1}')
if [ -z "$LOCAL_IP" ]; then
    LOCAL_IP=$(ifconfig | grep -m1 "inet " | grep -oP '(?<=inet )\d+\.\d+\.\d+\.\d+')
fi

if [ -z "$LOCAL_IP" ]; then
    LOCAL_IP="192.168.1.100"  # fallback
fi

echo "Local IP address detected: ${LOCAL_IP}"
echo "Certificates will be valid for:"
echo "  - localhost"
echo "  - 127.0.0.1"
echo "  - ${LOCAL_IP}"
echo ""

# Create certificate with Subject Alternative Names
openssl req -x509 -newkey rsa:2048 \
    -keyout "${KEY_FILE}" \
    -out "${CERT_FILE}" \
    -days "${DAYS}" \
    -nodes \
    -subj "/CN=localhost" \
    -addext "subjectAltName=DNS:localhost,DNS:*.local,IP:127.0.0.1,IP:${LOCAL_IP}"

echo ""
echo "✓ Certificates created successfully!"
echo "  Certificate: ${CERT_FILE}"
echo "  Private key: ${KEY_FILE}"
echo ""
echo "Next steps:"
echo "  1. Start the HTTPS server: python3 scripts/serve-local.py"
echo "  2. On your phone, open: https://${LOCAL_IP}:8443"
echo "  3. Accept the security warning (self-signed certificate)"
echo "  4. The app will load and cache everything for offline use"
echo ""
echo "Note: The certificate is valid for ${DAYS} days."
echo "To regenerate: rm -rf ${CERT_DIR}/ && ./scripts/create-ssl-certs.sh"
