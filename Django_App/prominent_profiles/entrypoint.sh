#!/bin/bash
# entrypoint.sh

# Ownership of the mounted volumes for django-user
chown -R django-user:django /app/nlp_processor/media
chown -R django-user:django /app/static

chown -R django-user:django /app

# Switching back to django-user
exec gosu django-user "$@"