#!/bin/bash

cd "$(dirname "${BASH_SOURCE[0]}")"
python3 remail.py | tee -a log.txt

