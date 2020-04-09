#!/bin/bash
# ADD ME TO CRON
# e.g.
# */5 * * * * /opt/remailer-pop3-smtp/remail.sh

cd $(dirname ${BASH_SOURCE[0]})
python3 remail.py | tee -a log.txt

