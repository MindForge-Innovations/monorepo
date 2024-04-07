#!/bin/bash

# Function to handle termination signals
handle_sigterm() {
    echo "SIGTERM signal received, shutting down..."
    # Gracefully stop your services here. For example:
    # kill -SIGTERM "$child_pid"
    exit 0
}

# Trap SIGTERM, SIGINT, and other relevant signals
# SIGINT is caught to handle Ctrl+C during manual execution
trap 'handle_sigterm' SIGTERM SIGINT

# Start the original entrypoint script in the background
#--log-config ${CHROMA_LOG_CONFIG}
/docker_entrypoint.sh --workers ${CHROMA_WORKERS} --host ${CHROMA_HOST_ADDR} --port ${CHROMA_HOST_PORT} --proxy-headers  --timeout-keep-alive ${CHROMA_TIMEOUT_KEEP_ALIVE} &
child_pid=$!

# Wait for ChromaDB to be available
while ! timeout 1 bash -c 'cat < /dev/null > /dev/tcp/localhost/8000'; do
  sleep 1
done

# Run the Python script to initialize the vector store
python /chroma/vector_store.py

# Wait for the background process to finish
wait "$child_pid"
