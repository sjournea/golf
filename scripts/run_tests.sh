#!/usr/bin/env bash 
cmd="python -m unittest discover -s test"

while [ "$1" != "" ]; do
  cmd="$cmd $1"
  shift
done

#echo $cmd
$cmd

#if [ "$1" != "" ]; then
#  echo "Testing pattern $1 only."
#  python -m unittest discover -s test -p "$1"
#else
#  python -m unittest discover -s test
#fi
