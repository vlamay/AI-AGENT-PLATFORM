# 🚀 ЗАПУСК СЕЙЧАС - ПОШАГОВАЯ ИНСТРУКЦИЯ

## ⚡ 1. Быстрый запуск (3 команды)

```bash
cd /home/devops/Downloads/AI-AGENT-PLATFORM
chmod +x QUICK_DEPLOY.sh
./QUICK_DEPLOY.sh
```

**Подождите 5-10 минут** пока скачаются образы и установятся модели.

---

## 📊 2. Проверка статуса

```bash
# Проверьте контейнеры
docker ps

# Должны увидеть:
# - ai-platform-ollama
# - ai-platform-postgres  
# - ai-platform-redis
# - ai-platform-n8n
# - ai-platform-grafana

# Тест Ollama
curl http://localhost:11434/api/tags
```

---

## 🌐 3. Откройте в браузере

- **n8n**: http://localhost:5678
  - Login: `admin`
  - Password: `ai_platform_2024`

- **Grafana**: http://localhost:3001
  - Login: `admin`
  - Password: `admin`

---

## 🧪 4. Тест AI генерации

```bash
# Тест Ollama (простой запрос)
curl -X POST http://localhost:11434/api/generate \
  -d '{"model":"llama3.3","prompt":"Say hello","stream":false}'
```

---

## 🔧 5. Если что-то не работает

```bash
# Посмотреть логи
docker compose -f docker-compose-minimal.yml logs -f ollama

# Перезапустить сервис
docker compose -f docker-compose-minimal.yml restart ollama

# Остановить всё
docker compose -f docker-compose-minimal.yml down

# Запустить заново
docker compose -f docker-compose-minimal.yml up -d
```

---

## 📝 Что дальше?

1. Создайте первый n8n workflow (см. START_HERE.md)
2. Настройте Cloudflare Tunnel для публичного доступа
3. Протестируйте на разных типах задач
4. Запустите на Reddit/HN

---

**🎉 Готово! Запускайте ./QUICK_DEPLOY.sh**

