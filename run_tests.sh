#!/usr/bin/env bash 
if [ "$1" != "" ]; then
  echo "Testing pattern $1 only."
  python -m unittest discover -s test -p "$1"
else
  python -m unittest discover -s test
fi
