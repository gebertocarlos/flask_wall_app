#!/usr/bin/env bash
# exit on error
set -o errexit

pip install -r requirements.txt

# JSON dosyasını oluştur (eğer yoksa)
if [ ! -f posts.json ]; then
    echo "[]" > posts.json
fi

# static klasörünü oluştur (eğer yoksa)
mkdir -p static 