# 🧱 More Components You Can Disable

### 1. **Mail System (if you don't need password recovery emails)**

```ruby
gitlab_rails['smtp_enable'] = false
gitlab_rails['gitlab_email_enabled'] = false
```

### 2. **Container Registry (if you store Docker images elsewhere or don’t use it)**

```ruby
registry['enable'] = false
```

### 3. **GitLab Pages (for static site hosting, usually off by default)**

```ruby
pages_external_url 'http://example.com'
gitlab_pages['enable'] = false
```

### 4. **Mattermost (GitLab’s chat, long gone but the stub may still exist)**

```ruby
mattermost_external_url 'http://example.com'
mattermost['enable'] = false
```

### 5. **Monitoring and Metrics (extra collectors you don’t need)**

You already disabled most, but you can go further:

```ruby
node_exporter['enable'] = false
redis_exporter['enable'] = false
postgres_exporter['enable'] = false
```

### 6. **GitLab Workhorse (reverse proxy)**

Keep this *enabled* — it’s essential — but limit concurrency:

```ruby
gitlab_workhorse['prometheus_listen_addr'] = nil
```

This disables Workhorse’s own metrics endpoint (saves a bit of RAM).

### 7. **Logrotate (if you handle logs outside GitLab or don’t care)**

```ruby
logrotate['enable'] = false
```

### 8. **Unicorn (legacy web server)**

GitLab now uses Puma, but this ensures Unicorn stays off:

```ruby
unicorn['enable'] = false
```

### 9. **Geo / Secondary Site Replication**

If you’re not running multiple GitLab nodes:

```ruby
geo_secondary['enable'] = false
```

### 10. **Backups Scheduler**

You can disable automatic backups if you back up `/var/opt/gitlab` manually:

```ruby
gitlab_rails['backup_keep_time'] = 0
```

### 11. **LDAP / OmniAuth (if not using external login)**

```ruby
gitlab_rails['ldap_enabled'] = false
gitlab_rails['omniauth_enabled'] = false
```

---

## 🪶 Example of the Expanded Minimal Setup

Here's what your block would look like after adding all safe lightweight options:

```yaml
environment:
  GITLAB_OMNIBUS_CONFIG: |
    external_url 'http://${ZT_ADDRS}/${GITLAB_SERVER_NAME}'
    gitlab_rails['gitlab_relative_url_root'] = '/${GITLAB_SERVER_NAME}'
    gitlab_rails['gitlab_shell_ssh_port'] = 22
    gitlab_rails['allowed_hosts'] = ['${ZT_ADDRS}']
    gitlab_rails['time_zone'] = 'UTC'

    nginx['listen_port'] = 80
    nginx['listen_https'] = false

    # Web server tuning
    puma['worker_processes'] = 1
    puma['threads_min'] = 1
    puma['threads_max'] = 2

    # Background jobs
    sidekiq['max_concurrency'] = 2

    # Disable unused features
    gitlab_ci['enable'] = false
    registry['enable'] = false
    gitlab_pages['enable'] = false
    mattermost['enable'] = false
    prometheus_monitoring['enable'] = false
    grafana['enable'] = false
    alertmanager['enable'] = false
    gitlab_exporter['enable'] = false
    node_exporter['enable'] = false
    redis_exporter['enable'] = false
    postgres_exporter['enable'] = false
    logrotate['enable'] = false
    unicorn['enable'] = false
    geo_secondary['enable'] = false

    # Lighten Postgres
    postgresql['max_worker_processes'] = 2
    postgresql['shared_buffers'] = "128MB"

    # Disable email if not needed
    gitlab_rails['smtp_enable'] = false
    gitlab_rails['gitlab_email_enabled'] = false

    # Disable external auth if unused
    gitlab_rails['ldap_enabled'] = false
    gitlab_rails['omniauth_enabled'] = false
```