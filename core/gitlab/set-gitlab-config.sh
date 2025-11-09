#!/bin/bash
set -e

# Load .env if it exists
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
fi

GITLAB_RB="./core/gitlab/config/gitlab.rb"

echo ">>> Applying config for GitLab on $GITLAB_RB"

# Write dynamic config using env expansion
cat > "$GITLAB_RB" <<EOF
external_url 'http://${ZT_ADDRS}/${GITLAB_SERVER_NAME}'
gitlab_rails['gitlab_relative_url_root'] = '/${GITLAB_SERVER_NAME}'
gitlab_rails['gitlab_shell_ssh_port'] = 22
gitlab_rails['gitlab_rails_allowed_hosts'] = ['${ZT_ADDRS}']

# Nginx
nginx['listen_port'] = 80
nginx['listen_https'] = false
nginx['worker_processes'] = 1
nginx['worker_connections'] = 512

# Timezone
gitlab_rails['time_zone'] = 'UTC'

# Puma web server
puma['worker_processes'] = 1
puma['threads_min'] = 1
puma['threads_max'] = 2

# Background jobs
sidekiq['max_concurrency'] = 2

# Disable nonessential services
prometheus_monitoring['enable'] = false
alertmanager['enable'] = false
gitlab_exporter['enable'] = false
mattermost_external_url nil
registry_external_url nil
pages_external_url nil

# Postgres tuning
postgresql['shared_buffers'] = '128MB'
postgresql['max_worker_processes'] = 2

# Redis memory tuning
redis['maxmemory_policy'] = 'allkeys-lru'
redis['maxmemory'] = '128mb'

# Disable unused project features
gitlab_rails['gitlab_default_projects_features_builds'] = false
gitlab_rails['gitlab_default_projects_features_container_registry'] = false
gitlab_rails['gitlab_default_projects_features_wiki'] = false
gitlab_rails['gitlab_default_projects_features_issues'] = false
gitlab_rails['gitlab_default_projects_features_merge_requests'] = false

# Logging (reduce disk usage)
logging['logrotate_frequency'] = "daily"
logging['svlogd_size'] = 1000000
logging['svlogd_num'] = 5
EOF

echo ">>> Configuration written to $GITLAB_RB"
echo ">>> Executing reconfigure inside container..."
docker exec -it mastercompose-gitlab gitlab-ctl reconfigure
echo ">>> Done!"