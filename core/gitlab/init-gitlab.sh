#!/bin/bash

# Load .env if it exists
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
fi

# Wait for GitLab to start
echo "Waiting for GitLab to be ready..."
until curl -s https://${GITLAB_HOST}:${GITLAB_PORT}//users/sign_in >/dev/null; do
    sleep 5
done

# Create default user if it doesn't exist
GITLAB_USER="${GITLAB_USER:-admin}"
GITLAB_PASSWORD="${GITLAB_PASSWORD:-password123}"
GITLAB_EMAIL="${GITLAB_EMAIL:-admin@example.com}"

docker exec -i mastercompose-gitlab gitlab-rails runner "
unless User.exists?(username: '${GITLAB_USER}')
    User.create!(username: '${GITLAB_USER}', email: '${GITLAB_EMAIL}', name: 'Admin User', password: '${GITLAB_PASSWORD}', password_confirmation: '${GITLAB_PASSWORD}', admin: true)
end
"
echo "GitLab user '${GITLAB_USER}' created or already exists."
