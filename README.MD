# Master Compose

Set up almost everything to devops

| Component     | Purpose                                                    | Notes                                                                                                                         |
| ------------- | ---------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------- |
| **GitLab‑CE** | DevOps platform (repositories, CI/CD, user management, UI) | Self‑hosted; runs in Docker; can be accessed via your VPN (ZeroTier) for remote collaborators.                                |
| **Portus**    | Container image registry (private Docker registry with UI) | Stores your Docker images locally; can integrate with GitLab CI/CD for builds.                                                |
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
./network/nginx/generate-dummy-certs.sh
```
