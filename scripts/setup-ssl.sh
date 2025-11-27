#!/bin/bash

set -e

echo "Setting up SSL certificates..."

mkdir -p ssl

if [ -f "ssl/key.pem" ] && [ -f "ssl/cert.pem" ]; then
    echo "SSL certificates already exist."
    exit 0
fi

openssl req -x509 -newkey rsa:4096 -nodes \
    -out ssl/cert.pem \
    -keyout ssl/key.pem \
    -days 365 \
    -subj "/C=JP/ST=Tokyo/L=Tokyo/O=Development/CN=localhost"

chmod 600 ssl/key.pem
chmod 644 ssl/cert.pem

echo "SSL certificates generated: ssl/cert.pem, ssl/key.pem"
