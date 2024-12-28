#!/bin/bash
# exit on error
set -o errexit

# Python sürümünü kontrol et ve kur
python3 -m pip install --upgrade pip

# Bağımlılıkları yükle
pip install -r requirements.txt

# JSON dosyasını oluştur (eğer yoksa)
if [ ! -f posts.json ]; then
    echo "[]" > posts.json
fi

# static klasörünü oluştur (eğer yoksa)
mkdir -p static 