#!/bin/bash

# 能源化工新闻分析系统 - 快速启动脚本

echo "=========================================="
echo "能源化工新闻分析系统 - 快速启动"
echo "=========================================="
echo ""

# 检查Docker是否安装
if ! command -v docker &> /dev/null; then
    echo "错误: Docker未安装，请先安装Docker"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "错误: Docker Compose未安装，请先安装Docker Compose"
    exit 1
fi

echo "检查环境..."
echo "Docker版本: $(docker --version)"
echo "Docker Compose版本: $(docker-compose --version)"
echo ""

# 创建必要的目录
echo "创建数据目录..."
mkdir -p data/postgres
mkdir -p data/mongodb
mkdir -p data/redis
mkdir -p data/elasticsearch
mkdir -p logs

echo ""
echo "启动服务..."
echo "=========================================="

# 启动所有服务
docker-compose up -d

echo ""
echo "等待服务启动..."
echo "=========================================="

# 等待服务启动
sleep 10

# 检查服务状态
echo ""
echo "检查服务状态..."
echo "=========================================="

docker-compose ps

echo ""
echo "=========================================="
echo "服务启动完成！"
echo "=========================================="
echo ""
echo "访问地址:"
echo "  - 前端界面: http://localhost"
echo "  - API文档: http://localhost:8000/docs"
echo "  - 后端API: http://localhost:8000"
echo ""
echo "默认数据库连接:"
echo "  - PostgreSQL: localhost:5432"
echo "  - MongoDB: localhost:27017"
echo "  - Redis: localhost:6379"
echo "  - Elasticsearch: localhost:9200"
echo ""
echo "查看日志:"
echo "  docker-compose logs -f [service_name]"
echo ""
echo "停止服务:"
echo "  docker-compose down"
echo ""
echo "=========================================="
