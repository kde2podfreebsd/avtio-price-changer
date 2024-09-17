#!/bin/bash
export PYTHONPATH="${PYTHONPATH}"
/usr/bin/supervisord -n -c /etc/supervisor/conf.d/supervisord.conf