#!/bin/sh

# Запуск cron и вывод логов
cron && tail -f /var/log/cron.log &

# Запуск основного приложения
python3 /app/bot.py
