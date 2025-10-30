# 🚀 AI AGENT PLATFORM - START HERE

## ✅ Быстрый старт (5 минут)

### Шаг 1: Проверка системы

```bash
cd /home/devops/Downloads/AI-AGENT-PLATFORM

# Запускаем автоматическую проверку и установку
./scripts/validate_and_start.sh
```

Скрипт автоматически:
- ✅ Проверит Docker и Docker Compose
- ✅ Проверит доступность портов
- ✅ Обнаружит NVIDIA GPU (если установлена)
- ✅ Скачает и запустит все сервисы
- ✅ Установит Ollama модели
- ✅ Протестирует все сервисы

---

### Шаг 2: Проверка работы

После запуска скрипта, откройте в браузере:

- **n8n Workflow UI**: http://localhost:5678
  - Логин: `admin`
  - Пароль: `ai_platform_2024`

- **Grafana Monitoring**: http://localhost:3001
  - Логин: `admin`
  - Пароль: `admin`

---

### Шаг 3: Тест Ollama

```bash
# Проверяем доступные модели
curl http://localhost:11434/api/tags

# Тестируем генерацию (простой запрос)
curl http://localhost:11434/api/generate -d '{
  "model": "llama3.3",
  "prompt": "Why is the sky blue? Answer in one sentence.",
  "stream": false
}'
```

---

## 🎯 Что дальше?

### Вариант A: Использовать n8n (Рекомендуется для non-coders)

**n8n** - это визуальный конструктор для AI workflows. Вместо программирования Python, вы:

1. Откройте n8n: http://localhost:5678
2. Создайте новый workflow
3. Настройте маршрутизацию между AI моделями визуально

**Примеры workflow**:
- 📧 Email обработка → AI анализ
- 💬 Chatbot → роутинг между моделями
- 📊 Analytics → агрегация данных

**Преимущества**:
- ✅ Не нужно писать код
- ✅ Готовые интеграции (Gmail, Slack, Telegram)
- ✅ Визуальная отладка
- ✅ Deployment одной кнопкой

---

### Вариант B: Использовать Python API (Для разработчиков)

Если хотите использовать существующий Python код:

```bash
# Установите зависимости
cd services/orchestrator
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Запустите API
cd app
uvicorn main:app --host 0.0.0.0 --port 8080
```

API будет доступен на: http://localhost:8080

---

### Вариант C: Полный стек (Production)

Если хотите запустить весь проект с всеми микросервисами:

```bash
# Запускаем полный docker-compose
docker compose up -d

# Проверяем статус
docker compose ps
```

**Примечание**: Полный стек требует больше ресурсов (~8GB RAM). Минимальный стек (`docker-compose-minimal.yml`) использует ~2GB.

---

## 📊 Мониторинг и логи

```bash
# Просмотр логов всех сервисов
docker compose -f docker-compose-minimal.yml logs -f

# Просмотр логов конкретного сервиса
docker compose -f docker-compose-minimal.yml logs -f ollama
docker compose -f docker-compose-minimal.yml logs -f n8n

# Проверка использования ресурсов
docker stats
```

---

## 🔧 Полезные команды

```bash
# Остановить все сервисы
docker compose -f docker-compose-minimal.yml down

# Перезапустить сервис
docker compose -f docker-compose-minimal.yml restart ollama

# Удалить все данные (файлы, БД)
docker compose -f docker-compose-minimal.yml down -v

# Установить новую модель Ollama
docker exec -it ai-platform-ollama ollama pull mistral:7b

# Список установленных моделей
docker exec -it ai-platform-ollama ollama list

# Тест модели
docker exec -it ai-platform-ollama ollama run llama3.3 "Explain quantum computing"
```

---

## 🌐 Публичный доступ (Опционально)

Для доступа из интернета используйте **Cloudflare Tunnel** (бесплатно):

```bash
# Установка
curl -L --output cloudflared.deb https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb
sudo dpkg -i cloudflared.deb

# Логин
cloudflared tunnel login

# Создание туннеля
cloudflared tunnel create ai-platform

# Запуск туннеля
cloudflared tunnel --url http://localhost:5678
```

Теперь у вас будет публичный URL типа: `https://your-random-id.trycloudflare.com`

---

## 🐛 Устранение неполадок

### Проблема: Порт 5432 занят
```bash
# Найдите процесс
sudo lsof -i :5432
# Убейте процесс
sudo kill -9 <PID>
```

### Проблема: Docker не запускается
```bash
# Проверьте статус
sudo systemctl status docker
# Запустите Docker
sudo systemctl start docker
```

### Проблема: Ollama не отвечает
```bash
# Проверьте логи
docker logs ai-platform-ollama
# Перезапустите
docker restart ai-platform-ollama
```

### Проблема: Недостаточно памяти
```bash
# Проверьте использование
free -h
# Очистите Docker
docker system prune -a
# Используйте только минимальный стек
docker compose -f docker-compose-minimal.yml up -d
```

---

## 📚 Документация

- **README.md** - Полное описание проекта
- **QUICKSTART.md** - 5-минутный быстрый старт
- **ARCHITECTURE.md** - Техническая архитектура
- **PRODUCT_HUNT_LAUNCH.md** - План запуска на Product Hunt
- **COMPETITIVE_ANALYSIS.md** - Сравнение с Born Digital
- **ZERO_BUDGET_SETUP.md** - Бесплатное развертывание

---

## 🎯 Следующие шаги

1. ✅ **День 1-3**: Запустите минимальный стек, изучите n8n
2. 📧 **День 4-7**: Создайте первый workflow (email processing)
3. 🚀 **День 8-14**: Запустите на Product Hunt
4. 💰 **День 30**: Получите первого платящего клиента

---

## 💡 Советы

- Начните с **n8n** - это самый быстрый способ создать MVP
- Используйте **Ollama local** для 90% запросов (бесплатно)
- Мониторьте использование ресурсов через Grafana
- Регулярно делайте бэкапы PostgreSQL
- Используйте GPU для Ollama (значительно быстрее)

---

## 🆘 Нужна помощь?

- GitHub Issues: https://github.com/vlamay/AI-AGENT-PLATFORM/issues
- Email: support@ai-agent-platform.com
- Discord: (скоро будет)

---

**🚀 Удачи с вашим AI Agent Platform!**

