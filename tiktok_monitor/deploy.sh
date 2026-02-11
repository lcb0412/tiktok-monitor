#!/bin/bash
# TikTok Monitor 部署脚本

set -e

echo "🚀 开始部署 TikTok Monitor..."

# 检查Python版本
python3 --version || { echo "❌ Python3 未安装"; exit 1; }

# 创建工作目录
WORK_DIR="/opt/tiktok-monitor"
sudo mkdir -p $WORK_DIR
sudo chown $USER:$USER $WORK_DIR

# 拉取最新代码
cd $WORK_DIR
if [ -d ".git" ]; then
    git pull origin main
else
    git clone https://github.com/lcb0412/tiktok-monitor.git .
fi

# 创建必要目录
mkdir -p data logs

# 安装依赖
pip3 install -r requirements.txt

# 配置Cookie
if [ ! -f ".env" ]; then
    echo "COOKIE=" > .env
    echo "请编辑 .env 文件设置Cookie"
fi

# 创建systemd服务
cat > tiktok-monitor.service << EOF
[Unit]
Description=TikTok Monitor Service
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=$WORK_DIR
ExecStart=/usr/bin/python3 $WORK_DIR/main.py
Restart=always
Environment=TIKTOK_MONITOR_CONFIG=$WORK_DIR/config.yaml

[Install]
WantedBy=multi-user.target
EOF

sudo cp tiktok-monitor.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable tiktok-monitor
sudo systemctl restart tiktok-monitor

echo "✅ 部署完成!"
echo "📊 API文档: http://你的服务器IP:8000/docs"
echo "📝 日志: tail -f $WORK_DIR/logs/app.log"
