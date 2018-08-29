#!/usr/bin/env bash 
python -m unittest discover -s test 2> golfunit.log
echo $?
