# Master Compose

Set up almost everything to devops

| Component     | Purpose                                                    | Notes                                                                                                                         |
| ------------- | ---------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------- |
| **GitLab‑CE** | DevOps platform (repositories, CI/CD, user management, UI) | Self‑hosted; runs in Docker; can be accessed via your VPN (ZeroTier) for remote collaborators.                                |
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

## generate cert

```shell
sudo chmod +x ./network/nginx/*.sh
```

### for ssl

```shell
./network/nginx/ssl-dhparams.pem.sh
```

### for containers

```shell
./network/nginx/generate-dummy-certs.sh
```

## Zerotier fix files

```shell
sudo chmod -R a+r ./network/zerotier
sudo find ./network/zerotier -type d -exec chmod a+rx {} \;
```
