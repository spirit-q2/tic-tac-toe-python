#!/bin/bash

# usage: ./lint.sh [-f]

ARGS="--check --diff"

if [ "$1" = "-f" ]; then
  ARGS=""
fi

black ${ARGS} --exclude "migrations|\.venv" --line-length 120 .
