#!/bin/bash

# Start a timer for watching for user LDAP updates
# Use the combined scheduler/worker config since this is not a production environment
sh -c 'cd app && celery -A poll_user_status worker -B' &

# Start the main application
fastapi run app/app.py --port 80 &

wait
