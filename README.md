# License Manager

## 快速部署

### 1. 获取部署文件

复制项目根目录的 `docker-compose.yml` 文件到你的部署目录：

```bash
curl -O https://raw.githubusercontent.com/Circle1688/license-manager/refs/heads/master/docker-compose.yml
```

### 2. 准备配置文件

- 准备配置文件`config.json`
  ```bash
  {
    "username":"",
    "password":""
  }
  ```
- 新建文件夹`PEM`，将私钥`private.pem`放置到所属文件夹下，完整示例`PEM/VR Manager/private.pem`，可放置多个类别

### 3. 启动服务

```bash
docker compose -f docker-compose.yml up
```

## 访问信息

- http://localhost:7860

## 常用命令

```bash
# 查看服务状态
docker compose -f docker-compose.yml ps

# 查看日志
docker compose -f docker-compose.yml logs -f

# 停止服务
docker compose -f docker-compose.yml down

# 重启服务
docker compose -f docker-compose.yml restart

# 完全清理（包括数据）
docker compose -f docker-compose.yml down -v
```

## 配置修改

如需修改配置，编辑 `config.json` 文件，然后重启服务：

```bash
docker compose -f docker-compose.yml restart
```
