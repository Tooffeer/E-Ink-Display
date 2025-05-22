#!/bin/bash

echo "🔧 Setting up the ePaper Spotify Display project..."

# Update and install system packages
sudo apt update
sudo apt install -y python3 python3-pip python3-venv git

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Install Waveshare drivers (example for 2.13" HAT)
if [ ! -d "waveshare_epd" ]; then
  git clone https://github.com/waveshare/e-Paper
  cp -r e-Paper/RaspberryPi_JetsonNano/python/lib/waveshare_epd .
fi

# Make main.py executable (optional)
chmod +x main.py

echo "✅ Setup complete. Run with: source venv/bin/activate && python main.py"
