#!/bin/bash

set -e  # Остановить выполнение при любой ошибке

log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') $1"
}

run_or_fail() {
    description="$1"
    shift
    command_output=$(mktemp)
    if "$@" >"$command_output" 2>&1; then
        log "✅ $description успешно выполнено."
        rm "$command_output"
    else
        log "❌ $description завершилось с ошибкой:"
        cat "$command_output"
        rm "$command_output"
        exit 1
    fi
}

log "🔄 Обновление кода из Git..."
run_or_fail "Git pull" git pull

log "🔄 Синхронизация uv..."
run_or_fail "uv sync" uv sync

log "🛠️ Применение миграций..."
run_or_fail "Миграции Django" uv run manage.py migrate

log "📦 Сборка статических файлов..."
run_or_fail "Collectstatic Django" uv run manage.py collectstatic --noinput

log "🔁 Перезапуск сервисов..."
run_or_fail "Перезапуск gunicorn" sudo systemctl restart gunicorn
run_or_fail "Перезапуск celery hard" sudo systemctl restart hard
run_or_fail "Перезапуск celery fast" sudo systemctl restart fast
run_or_fail "Перезапуск celery-beat" sudo systemctl restart celery-beat