#!/bin/sh
set -eu

TESTS_FLD=$(CDPATH= cd "$(dirname "$0")" && pwd -P)
ENV_DOCKER_PATH="$TESTS_FLD/.env.docker"

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

#
# docker compose -f "$COMPOSE_TEST_FILE" up -d rescale-onlykey

# export TEST_FILE="test_hash_manager.py"
# docker compose -f "$COMPOSE_TEST_FILE" run --rm tester

# export TEST_FILE="test_dag_hash_manager.py"
# docker compose -f "$COMPOSE_TEST_FILE" run --rm tester

# docker compose -f "$COMPOSE_TEST_FILE" down

#
# docker compose -f "$COMPOSE_TEST_FILE" up -d rescale-auth

# export TEST_FILE="test_rescalenode_authentication.py"
# docker compose -f "$COMPOSE_TEST_FILE" run --rm tester

# docker compose -f "$COMPOSE_TEST_FILE" down