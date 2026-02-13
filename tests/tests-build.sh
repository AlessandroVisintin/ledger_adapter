#!/bin/sh
set -eu

TESTS_FLD=$(CDPATH= cd "$(dirname "$0")" && pwd -P)
ENV_DOCKER_PATH="$TESTS_FLD/.env.docker"

if [ -f "$ENV_DOCKER_PATH" ]; then
    printf '%s\n' "Loading configuration from $ENV_DOCKER_PATH"
    set -a
    . "$ENV_DOCKER_PATH"
    set +a
else
    printf '%s\n' "ERROR: No .env file found at $ENV_DOCKER_PATH" >&2
    exit 1
fi

docker compose -f "$COMPOSE_BUILD_FILE" build