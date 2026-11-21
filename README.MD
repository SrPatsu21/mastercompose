# Master Compose

1. create and adjust .env

2. Set secrets

```shell
mkdir -p secrets

touch \
  secrets/forgejo_db_password.txt \
  secrets/forgejo_mailer_password.txt \
  secrets/ai_gateway_key.txt
```

```shell
openssl rand -hex 32 | sed 's/^/sk-/' > secrets/ai_gateway_key.txt
```

```shell
chmod 600 secrets/*.txt
```

## Network setup

### Nginx TLS

### Generate cert

```shell
mkdir -p ./network/nginx/ssl

openssl req \
  -x509 \
  -nodes \
  -newkey rsa:2048 \
  -keyout ./network/nginx/ssl/privkey.pem \
  -out ./network/nginx/ssl/fullchain.pem \
  -days 365 \
  -subj "/CN=localhost" \
  -addext "subjectAltName=DNS:localhost,IP:127.0.0.1,IP:10.147.18.1,IP:192.168.80.105"
```

Obs: change for your IPs

#### Update your certs

```shell
sudo cp ./network/nginx/ssl/fullchain.pem /etc/ca-certificates/trust-source/anchors/forgejo-local.crt
sudo update-ca-trust
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
docker compose up -d
```

### Zerotier Network ID

```shell
docker exec -it mastercompose-zerotier zerotier-cli join <NETWORK_ID>
```

Authorized member on my.zerotier.com/network/<NETWORK_ID>

you need to config the **ZT_ADDRS** on `.env` otherwize it won´t work

## Apps

### Forgejo

#### Forgejo user

```shell
docker exec -u 1000 -it mastercompose-forgejo /usr/local/bin/gitea admin user create \
  --username SrPatsu21 \
  --password ADMIN \
  --email paulosergiopierdona@gmail.com \
  --admin \
  --must-change-password=true
```

#### ssh key

```shell
ssh-keygen -t ed25519 -C "forgejo" -f ~/.ssh/forgejo_ed25519
eval "$(ssh-agent -s)"
ssh-add -l
cat ~/.ssh/forgejo_ed25519.pub
```

#### Runner

Create the Runner directories:

```shell
mkdir -p apps/forgejo/runner/data
mkdir -p apps/forgejo/runner/docker
```

Set the correct ownership and permissions for the Runner data directory.

The Runner container runs as UID/GID `1000:1000`, so it needs ownership of the mounted `/data` directory.

```shell
sudo chown -R 1000:1000 apps/forgejo/runner/data
sudo chmod -R u+rwX apps/forgejo/runner/data

sudo chown -R 1000:1000 apps/forgejo/data/actions_log apps/forgejo/data/actions_artifacts

sudo chown -R 1000:1000 apps/forgejo/data/packages
sudo chmod -R u+rwX apps/forgejo/data/packages
```

Use `config.example.yml` as an example to create the `config.yml` file for the Runner.

Add the Nginx certificate to the Runner environment, in the same file that defines `FORGEJO_TOKEN`. Jobs use it to verify TLS instead of disabling verification:

```shell
echo "FORGEJO_CA_B64=$(base64 -w0 network/nginx/ssl/fullchain.pem)" >> apps/forgejo/runner/data/.env
```

Renew this value whenever the certificate is regenerated.

After configuring the Runner, start the services:

```shell
docker compose -f apps/docker-compose.forgejo.yml up -d
```

#### Forgejo Actions

Create a workflow directory inside your repository:

```shell
mkdir -p .forgejo/workflows
```

Add your workflow files (`.yml`) inside `.forgejo/workflows/`.

The AI review workflow needs a repository secret named `AI_GATEWAY_KEY`
(Repository → Settings → Actions → Secrets). Use the value from:

```shell
cat secrets/ai_gateway_key.txt
```

##### Conteiner for Actions

- Basic CI

```shell
docker build --platform linux/amd64 -t 10.147.18.1/srpatsu21/basic-ci-img:ubuntu-24.04 .forgejo/docker/basic_ci
docker push 10.147.18.1/srpatsu21/basic-ci-img:ubuntu-24.04
```

- AI review image

```shell
docker build --platform linux/amd64 -t 10.147.18.1/srpatsu21/ai-review-img:ubuntu-24.04 .forgejo/docker/ai_review
docker push 10.147.18.1/srpatsu21/ai-review-img:ubuntu-24.04
``` 

### Jellyfin

```shell
docker compose -f apps/docker-compose.jellyfin.yml up -d
```

```shell
mkdir -p apps/jellyfin/
sudo chown -R 1000:1000 apps/jellyfin/
```

### AI

#### WebSearch

Create directories for persistent data:

```shell
mkdir -p apps/ai/searxng/config
mkdir -p apps/ai/searxng/cache
mkdir -p apps/ai/searxng/valkey
```

Create the local configuration files from their examples:

```shell
cp apps/ai/searxng/config/settings.yml.example apps/ai/searxng/config/settings.yml
cp apps/ai/searxng/config/limiter.toml.example apps/ai/searxng/config/limiter.toml
```

Generate the SearXNG secret key:

```shell
openssl rand -hex 32
```

Set the generated key in `apps/ai/searxng/config/settings.yml`.

SearXNG configuration (`settings.yml`):

```yaml
use_default_settings: true

general:
  debug: false
  instance_name: "MasterCompose Search"
  contact_url: "mailto:admin@example.com"

search:
  safe_search: 1
  autocomplete: ""
  formats:
    - html
    - json

server:
  secret_key: "YOUR_GENERATED_SECRET_KEY"
  limiter: true
  image_proxy: true

valkey:
  url: valkey://172.20.0.24:6379/0
```

Replace the contact address and secret key with your own values.

SearXNG limiter configuration (`limiter.toml`):

```toml
[botdetection]

ipv4_prefix = 32
ipv6_prefix = 48

trusted_proxies = [
    '127.0.0.0/8',
    '::1'
]

[botdetection.ip_limit]

filter_link_local = false
link_token = false

[botdetection.ip_lists]

pass_ip = [
    '172.20.0.0/16'
]

block_ip = []

pass_searxng_org = true
```

The `trusted_proxies` list must contain only trusted reverse proxies.

The `pass_ip` list allows unrestricted access from the specified IP addresses or networks, bypassing bot detection. The example allows the entire internal Docker network. Only use this configuration if all containers on that network are trusted.

SearXNG uses Valkey for rate limiting and both services communicate through their static IPs.

Persistent data is stored locally in the project:

- `apps/ai/searxng/config`
- `apps/ai/searxng/cache`
- `apps/ai/searxng/valkey`

#### Permissions

Ensure the configuration files are readable by the SearXNG container:

```shell
sudo chown -R $USER:$(id -gn) apps/ai/searxng/config

chmod 755 apps/ai/searxng/config
chmod 644 apps/ai/searxng/config/settings.yml
chmod 644 apps/ai/searxng/config/limiter.toml
```

The example files can be versioned without exposing local configuration or secrets.

#### Start

```shell
docker compose -f apps/docker-compose.ai.yml up -d
```

#### Check

```shell
docker compose -f apps/docker-compose.ai.yml ps
```

#### Ollama

```shell
docker exec -it mastercompose-ollama ollama --version

docker exec -it mastercompose-ollama ollama pull glm4

docker exec -it mastercompose-ollama ollama list

docker exec -it mastercompose-ollama ollama run glm4
```

#### OpenWebUI

Access Open WebUI at:

`http://${AI_WEBUI_IP}:30020`

If no model is available, configure the LiteLLM connection under Admin Panel → Settings → Connections → OpenAI API Connections.

- API URL: `http://${AI_IP}:${AI_GATEWAY_PORT}`
- API Key: the key configured in LiteLLM (`ai_gateway_key`).

#### Web Search

On Open WebUI, go to Admin Panel → Settings → Web Search.

Configure:

- Enable Web Search = Enabled
- Web Search Engine = `searxng`
- SearXNG Query URL = `http://${SEARXNG_IP}:8080/search?q=<query>&format=json`
- Search Result Count = `5`
- Concurrent Requests = `5`

Save the configuration.

Enable Web Search in the tools menu of the conversation when you want to use web search.

#### WebSearch Check

Test SearXNG from the Docker network using its static IP:

```shell
docker run --rm \
  --network mastercompose_internal \
  curlimages/curl:latest \
  -fsS \
  "http://${SEARXNG_IP}:8080/search?q=teste&format=json"
```

The expected response is JSON containing search results.

##### Cline

Configure the LiteLLM provider using the following Base URL: `https://<zerotier ip>:8444/v1`

The api key is on: `secrets/ai_gateway_key.txt`
