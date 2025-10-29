#!/usr/bin/env bash
set -euo pipefail
DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$DIR"
rm -rf build && mkdir -p build/python
pip install -r requirements.txt -t build/python >/dev/null
cp handler.py build/
cd build && zip -r lambda.zip . >/dev/null
echo "✅ Lambda Criar Pedido empacotada!"
