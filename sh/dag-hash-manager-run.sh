#!/bin/sh
set -eu

ROOT_FLD=$(CDPATH= cd "$(dirname "$0")/.." && pwd -P)
ENV_DOCKER_PATH="$ROOT_FLD/.env.docker"

if [ -f "$ENV_DOCKER_PATH" ]; then
    echo "Loading configuration from $ENV_DOCKER_PATH"
    set -a
    . "$ENV_DOCKER_PATH"
    set +a
else
    echo "ERROR: No .env file found at $ENV_DOCKER_PATH" >&2
    exit 1
fi

export NODE_URL="http://$BESU_NODE_IP:$BESU_NODE_PORT"
export P2P_DISCOVERY="$BESU_NODE_IP"

docker compose -f "$COMPOSE_TEST_FILE" up -d rescale-onlykey

docker compose -f "$COMPOSE_TEST_FILE" run --rm tester \
  "pip install -e /app/module --no-deps -q \
   && python /app/module/examples/dag_hash_manager.py"

docker compose -f "$COMPOSE_TEST_FILE" down
