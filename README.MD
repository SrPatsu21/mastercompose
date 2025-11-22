# Master Compose

Set up almost everything to devops

| Component     | Purpose                                                    | Notes                                                                                                                         |
| ------------- | ---------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------- |
| **Forgejo**   | DevOps platform (repositories, CI/CD, user management, UI) | Self‑hosted; runs in Docker; can be accessed via your VPN (ZeroTier) for remote collaborators.                                |
| **ZeroTier**  | VPN / overlay network                                      | Handles NAT/firewall issues, allows collaborators to access GitLab & Portus without opening ports to the public Internet.     |
| **Backrest**  | Backup solution with UI                                    | Automates backups of GitLab volumes, Portus volumes, and optionally other data; supports rotation policies (local and cloud). |
| **nginx**     | Reverse Proxy                                              | Open source reverse proxy server for HTTP, HTTPS, SMTP, POP3, and IMAP protocols.                                             |

[ZeroTier VPN]
        |
[NGINX Proxy Manager (UI + reverse proxy)]
        |
+-------+--------+--------+
|       |        |        |
GitLab  Portus  Backrest  ...

## Network setup

### Permissions

```shell
sudo chown -R 100000:100000 ./network/nginx
sudo chown -R 100000:100000 ./network/cloudflared
```

### NGINX

```shell
sudo chmod +x ./network/nginx/*.sh
```

#### generate cert for ssl

```shell
./network/nginx/ssl-dhparams.pem.sh
```

#### generate cert for containers

```shell
./network/nginx/generate-dummy-certs.sh
```

### Cloudflare login

```shell
sudo mkdir -p ./network/cloudflared
sudo chmod 755 -R ./network/cloudflared
docker run -it --rm -v ./network/cloudflared:/home/nonroot/.cloudflared cloudflare/cloudflared:latest tunnel login
sudo docker run -it --rm -v ./network/cloudflared:/home/nonroot/.cloudflared cloudflare/cloudflared:latest tunnel create my-tunel
docker exec -it mastercompose-cloudflared cloudflared tunnel route dns my-tunel paulosergio.pierdona.nom.br
```

no A, AAAA if u use tunel

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
