#!/bin/bash
# entrypoint.sh

# Change ownership of the mounted volumes to django-user
chown -R django-user:django /app/nlp_processor/media
chown -R django-user:django /app/static
chown -R django-user:django /app

# Write permission for the django-user (to save/delete etc)
chmod -R u+w /app/nlp_processor/media
chmod -R u+w /app/static
chmod -R u+w /app

# Switching back to django-user
exec gosu django-user "$@"
