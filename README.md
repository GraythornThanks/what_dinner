## 今晚吃什么

本项目是一个用于学习如何使用客户端对接WEB API的项目

### 技术栈

- FastAPI
- PostgreSQL

### 如何运行

#### 使用docker（推荐）

1. 拉取仓库

```bash
git clone https://github.com/GraythornThanks/what_dinner.git
cd what_dinner
```

2. 配置环境变量

创建.env文件，复制.env.example中的内容到.env文件中

3. 运行docker-compose

```bash
docker-compose up -d
```

> 常见问题：拉取镜像失败，请配置docker镜像

```bash
cat <<-EOF > /etc/docker/daemon.json 
{
  "registry-mirrors": [
  	"https://docker.xuanyuan.me"
  	]
}
EOF
systemctl daemon-reload
systemctl restart docker
```

#### 直接本地运行

archlinux

```bash
sudo pacman -S uv
uv venv
source .venv/bin/activate
uv sync
uvicorn main:app --host 0.0.0.0 --port 8000
```
