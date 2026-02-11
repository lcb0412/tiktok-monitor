# TikTok Monitor

TikTok数据监控系统 - 支持视频数据监控、用户数据监控、数据历史记录

## 项目结构

```
tiktok_monitor/
├── api/               # FastAPI REST API
├── core/              # 核心模块
│   ├── config.py     # 配置加载
│   ├── crawler.py    # 爬虫引擎
│   ├── signer.py     # X-Bogus签名
│   └── logger.py     # 日志配置
├── storage/          # 数据存储层
│   ├── database.py   # SQLite数据库连接
│   ├── models.py    # 数据模型
│   └── repositories.py # 数据访问层
├── scheduler/        # 定时任务调度
├── utils/            # 工具函数
├── main.py          # 程序入口
├── config.yaml      # 配置文件
└── requirements.txt # 依赖列表
```

## 快速开始

### 1. 安装依赖

```bash
cd tiktok_monitor
pip install -r requirements.txt
```

### 2. 配置

编辑 `config.yaml` 设置Cookie等参数

### 3. 运行

```bash
cd tiktok_monitor
python main.py
```

API文档: http://localhost:8000/docs

## 功能特性

- 视频数据监控 (播放量、点赞、评论、分享、收藏)
- 用户数据监控 (粉丝数、关注数、总获赞)
- 数据历史记录
- 定时任务调度
- REST API接口
- SQLite轻量级存储

## 技术栈

- Python 3.8+
- FastAPI
- SQLAlchemy + aiosqlite
- aiohttp
- loguru
