#!/bin/bash
set -e

echo ">>> Instalando ffmpeg..."
apt-get update -qq && apt-get install -y -qq ffmpeg

echo ">>> Instalando dependencias Python..."
pip install -r requirements.txt

echo ">>> Build completado."
