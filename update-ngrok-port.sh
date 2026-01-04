#!/bin/bash

# Script tự động: Chạy ngrok tcp 1883 và update MQTT port vào các file ESP32 simulator
# Usage: ./update-ngrok-port.sh
# Script sẽ tự chạy ngrok, lấy port, update files

files=(
    "ESP32-Fan/src/main.cpp"
    "ESP32-Sensor/src/main.cpp"
)

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Kiểm tra ngrok đã cài chưa
if ! command -v ngrok &> /dev/null; then
    echo "❌ ngrok not found! Please install ngrok first."
    echo "   Download: https://ngrok.com/download"
    echo "   Or install via snap: sudo snap install ngrok"
    exit 1
fi

# Kill ngrok cũ nếu đang chạy
if pgrep -x "ngrok" > /dev/null; then
    echo "Stopping existing ngrok process..."
    pkill -f ngrok
    sleep 1
fi

# Chạy ngrok trong background
echo "Starting ngrok tcp 1883..."
ngrok tcp 1883 > /tmp/ngrok.log 2>&1 &
ngrok_pid=$!

# Chờ ngrok khởi động
echo "Waiting for ngrok to start..."
sleep 5

# Kiểm tra ngrok có chạy không
if ! ps -p $ngrok_pid > /dev/null; then
    echo "❌ ngrok failed to start!"
    echo "   Check log: cat /tmp/ngrok.log"
    cat /tmp/ngrok.log
    exit 1
fi

# Lấy port từ ngrok API
max_retries=10
port=""

for ((i=1; i<=max_retries; i++)); do
    response=$(curl -s http://localhost:4040/api/tunnels 2>/dev/null)
    if [ -n "$response" ]; then
        # Parse JSON để lấy port từ public_url - use sed instead of grep
        port=$(echo "$response" | sed -n 's/.*"public_url":"tcp:\/\/[^:]*:\([0-9]*\)".*/\1/p')
        if [ -n "$port" ]; then
            break
        fi
    fi
    echo "   Retry $i/$max_retries..."
    sleep 2
done

if [ -z "$port" ]; then
    echo "Failed to get port from ngrok API!"
    echo "Make sure ngrok is running and try again."
    kill $ngrok_pid 2>/dev/null
    exit 1
fi

echo "Got ngrok port: $port"
echo ""

# Update files
echo "Updating MQTT_PORT in ESP32 files..."

for file in "${files[@]}"; do
    file_path="$script_dir/$file"
    
    if [ -f "$file_path" ]; then
        # Replace MQTT_PORT value using sed
        sed -i "s/const int MQTT_PORT = [0-9]\+;/const int MQTT_PORT = $port;/" "$file_path"
        echo "   $file ✓"
    else
        echo "   Not found: $file ❌"
    fi
done

echo ""
echo "========================================"
echo "   Done!"
echo "   ngrok URL: tcp://0.tcp.ap.ngrok.io:$port"
echo "   MQTT_PORT: $port"
echo "========================================"
echo ""
echo "Next steps:"
echo "   1. Restart Wokwi simulations (Fan, Sensor)"
echo "   2. ngrok is running in background (PID: $ngrok_pid)"
echo "   3. To stop ngrok: kill $ngrok_pid"