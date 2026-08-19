# Master Compose

## Network setup

### Nginx TLS

Generate cert

```shell
mkdir -p ./network/nginx/ssl

openssl req \
  -x509 \
  -nodes \
  -newkey rsa:2048 \
  -keyout ./network/nginx/ssl/privkey.pem \
  -out ./network/nginx/ssl/fullchain.pem \
  -days 365 \
  -subj "/CN=mastercompose.com"
```

### Zerotier

#### Zerotier fix files and port

```shell
sudo chmod -R a+rw ./network/zerotier
sudo find ./network/zerotier -type d -exec chmod a+rx {} \;

sudo chmod +x ./network/zerotier/change-zt-port.sh
./network/zerotier/change-zt-port.sh
```

### RUN Network

```shell
docker compose -f docker-compose.network.yml up -d
```

### Zerotier Network ID

```shell
docker exec -it mastercompose-zerotier zerotier-cli join <NETWORK_ID>
```

Authorized member on my.zerotier.com/network/<NETWORK_ID>

you need to config the **ZT_ADDRS** on `.env` otherwize it won´t work

## Core

### Permissions

```shell
sudo chown -R 100000:100000 ./core
```

### Backrest

#### set users

```shell
sudo chmod +x ./core/backrest/config/make_users.sh
sudo ./core/backrest/config/make_users.sh
```

### Forgejo folders
"
mkdir -p core/forgejo/data/registry
mkdir -p core/forgejo/data/git/lfs
mkdir -p core/forgejo/data/gitea/avatars
mkdir -p core/forgejo/data/gitea/repo-avatars

sudo chown -R 1000:1000 core/forgejo/data
"

### start core

```shell
docker compose -f docker-compose.core.yml up -d
```

### Forgejo user

```shell
docker exec -u 1000 -it mastercompose-forgejo /usr/local/bin/gitea admin user create \
  --username SrPatsu21 \
  --password ADMIN \
  --email paulosergiopierdona@gmail.com \
  --admin \
  --must-change-password=true
```
