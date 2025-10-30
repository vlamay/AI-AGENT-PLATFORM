# 🤖 LM Studio Integration Guide

## 📋 Что такое LM Studio?

**LM Studio** - это графический интерфейс для локальных LLM с встроенным API сервером, альтернатива Ollama.

**Преимущества LM Studio:**
- ✅ Графический интерфейс для управления моделями
- ✅ Поддержка GGUF/GGML форматов
- ✅ Простой UI для загрузки и переключения моделей
- ✅ Встроенный OpenAI-совместимый API
- ✅ Поддержка CUDA для NVIDIA GPU

---

## 🚀 Шаг 1: Запуск LM Studio API

### Вариант A: Через графический интерфейс

1. **Откройте LM Studio** (уже запущен)

2. **Включите Local Server**:
   - Найдите раздел "Local Server" в боковой панели
   - Нажмите "Start Server"
   - Выберите порт (по умолчанию 1234)
   - Запустите сервер

3. **Выберите модель**:
   - Загрузите нужную модель из библиотеки
   - Переключите на неё в интерфейсе

### Вариант B: Через командную строку

```bash
# Если LM Studio установлен как AppImage
/opt/LM-Studio.AppImage --server 1234

# Или если установлен через apt/flatpak
lm-studio --server 1234
```

---

## 🧪 Шаг 2: Тестирование LM Studio API

### Проверка доступности

```bash
# Тест API
curl http://localhost:1234/v1/models

# Должен вернуть список моделей
```

### Тест генерации

```bash
curl http://localhost:1234/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "local-model",
    "messages": [{"role": "user", "content": "Hello!"}],
    "temperature": 0.7
  }'
```

---

## 🔧 Шаг 3: Интеграция в проект

### Вариант A: Замена Ollama на LM Studio

Создайте новый `docker-compose-lm-studio.yml`:

```yaml
version: '3.8'

services:
  # ============================================
  # LM Studio вместо Ollama
  # ============================================
  
  # Примечание: LM Studio должен запускаться
  # на хосте (не в Docker), так как это GUI приложение
  
  # ============================================
  # FastAPI Orchestrator с поддержкой LM Studio
  # ============================================
  api:
    build:
      context: ./services/orchestrator
      dockerfile: Dockerfile
    container_name: ai-platform-api-lm
    ports:
      - "8080:8080"
    environment:
      - LM_STUDIO_ENDPOINT=http://host.docker.internal:1234
      - OLLAMA_ENDPOINT=http://ollama:11434
      - PREFERRED_LLM=lm_studio  # Использовать LM Studio как основной
    extra_hosts:
      - "host.docker.internal:host-gateway"
    volumes:
      - ./services/orchestrator/app:/app
    depends_on:
      - postgres
      - redis
    restart: unless-stopped

  # Остальные сервисы остаются без изменений
  postgres:
    image: postgres:16-alpine
    container_name: ai-platform-db
    environment:
      POSTGRES_DB: ai_platform
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres_secure_pass_2024
    ports:
      - "5433:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    container_name: ai-platform-redis
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    restart: unless-stopped

  n8n:
    image: n8nio/n8n:latest
    container_name: ai-platform-n8n
    ports:
      - "5679:5678"
    environment:
      - N8N_BASIC_AUTH_ACTIVE=true
      - N8N_BASIC_AUTH_USER=admin
      - N8N_BASIC_AUTH_PASSWORD=ai_platform_2024
    volumes:
      - n8n_data:/home/node/.n8n
    restart: unless-stopped

volumes:
  postgres_data:
  redis_data:
  n8n_data:
```

---

### Вариант B: Гибридное использование (LM Studio + Ollama)

Обновите `main_enhanced.py` для поддержки обоих:

```python
import os
import httpx
from typing import Optional

# Environment variables
OLLAMA_ENDPOINT = os.getenv("OLLAMA_ENDPOINT", "http://localhost:11434")
LM_STUDIO_ENDPOINT = os.getenv("LM_STUDIO_ENDPOINT", "http://localhost:1234")

class HybridModelRouter:
    """Router с поддержкой Ollama и LM Studio"""
    
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=120.0)
        self.preferred_llm = os.getenv("PREFERRED_LLM", "ollama")  # ollama, lm_studio, auto
    
    async def call_local_llm(
        self,
        prompt: str,
        model_name: Optional[str] = None,
        **kwargs
    ) -> dict:
        """Вызов локального LLM (Ollama или LM Studio)"""
        
        # Автоматический выбор или принудительный
        if self.preferred_llm == "auto":
            # Проверить доступность
            ollama_available = await self._check_service(OLLAMA_ENDPOINT)
            lm_studio_available = await self._check_service(LM_STUDIO_ENDPOINT)
            
            if lm_studio_available:
                return await self._call_lm_studio(prompt, model_name, **kwargs)
            elif ollama_available:
                return await self._call_ollama(prompt, model_name, **kwargs)
            else:
                raise Exception("No local LLM service available")
        
        elif self.preferred_llm == "lm_studio":
            return await self._call_lm_studio(prompt, model_name, **kwargs)
        else:
            return await self._call_ollama(prompt, model_name, **kwargs)
    
    async def _check_service(self, endpoint: str) -> bool:
        """Проверка доступности сервиса"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{endpoint}/v1/models", timeout=2.0)
                return response.status_code == 200
        except:
            return False
    
    async def _call_lm_studio(
        self,
        prompt: str,
        model: Optional[str],
        **kwargs
    ) -> dict:
        """Вызов LM Studio API"""
        url = f"{LM_STUDIO_ENDPOINT}/v1/chat/completions"
        
        payload = {
            "model": model or "local-model",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": kwargs.get("temperature", 0.7),
            "max_tokens": kwargs.get("max_tokens", 2000),
        }
        
        try:
            response = await self.client.post(url, json=payload)
            response.raise_for_status()
            data = response.json()
            
            return {
                "response": data["choices"][0]["message"]["content"],
                "tokens": data.get("usage", {}).get("total_tokens", 0),
                "model": data.get("model", "lm-studio"),
            }
        except httpx.HTTPError as e:
            raise Exception(f"LM Studio error: {e}")
    
    async def _call_ollama(self, prompt: str, model: Optional[str], **kwargs) -> dict:
        """Вызов Ollama API"""
        url = f"{OLLAMA_ENDPOINT}/api/generate"
        
        payload = {
            "model": model or "llama3.1:8b",
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": kwargs.get("temperature", 0.7),
                "num_predict": kwargs.get("max_tokens", 2000),
            }
        }
        
        try:
            response = await self.client.post(url, json=payload)
            response.raise_for_status()
            data = response.json()
            
            return {
                "response": data.get("response", ""),
                "tokens": data.get("eval_count", 0),
                "model": data.get("model", "ollama"),
            }
        except httpx.HTTPError as e:
            raise Exception(f"Ollama error: {e}")
```

---

## 📊 Шаг 4: Настройка n8n workflow

В n8n добавьте HTTP Request node для LM Studio:

```json
{
  "name": "LM Studio LLM",
  "type": "n8n-nodes-base.httpRequest",
  "parameters": {
    "url": "http://localhost:1234/v1/chat/completions",
    "method": "POST",
    "authentication": "none",
    "sendBody": true,
    "specifyBody": "json",
    "jsonBody": "={\n  \"model\": \"local-model\",\n  \"messages\": [{\"role\": \"user\", \"content\": \"{{ $json.body.prompt }}\"}],\n  \"temperature\": 0.7,\n  \"max_tokens\": 2000\n}",
    "options": {}
  },
  "position": [250, 300]
}
```

---

## 🎯 Сравнение: LM Studio vs Ollama

| Feature | LM Studio | Ollama |
|---------|-----------|--------|
| **UI** | ✅ GUI приложение | ❌ CLI only |
| **API** | ✅ OpenAI-compatible | ✅ Custom API |
| **Установка моделей** | ✅ Через UI | ⚠️ Команда ollama pull |
| **GPU Support** | ✅ CUDA | ✅ CUDA |
| **Docker** | ❌ Нет (GUI) | ✅ Есть |
| **Production** | ⚠️ Для dev | ✅ Да |

**Рекомендация:**
- **Локальная разработка**: LM Studio (удобный UI)
- **Production/Сервер**: Ollama (легковесный, Docker-friendly)

---

## 🔄 Гибридная архитектура

```
┌────────────────────────────────────────┐
│  Production (Онлайн)                   │
├────────────────────────────────────────┤
│  ASUS TUF Laptop                       │
│                                        │
│  ┌──────────────┐  ┌──────────────┐   │
│  │ LM Studio    │  │ Ollama       │   │
│  │ (Dev mode)   │  │ (Production) │   │
│  │ Port 1234    │  │ Port 11434   │   │
│  └──────┬───────┘  └──────┬───────┘   │
│         │                  │           │
│         └────────┬─────────┘           │
│                  ▼                     │
│         ┌─────────────────┐            │
│         │ FastAPI Router  │            │
│         │ Auto-detect     │            │
│         │ preferred LLM   │            │
│         └─────────────────┘            │
│                                        │
│  Smart routing:                        │
│  • Code tasks → LM Studio              │
│  • Chat tasks → Ollama                 │
│  • Fallback между ними                 │
└────────────────────────────────────────┘
```

---

## 🚀 Быстрая настройка

### 1. Включите LM Studio API

В LM Studio:
- Local Server → Start Server
- Порт: 1234
- Проверьте: `curl http://localhost:1234/v1/models`

### 2. Обновите переменные окружения

```bash
# В .env файле
PREFERRED_LLM=lm_studio
LM_STUDIO_ENDPOINT=http://localhost:1234
```

### 3. Перезапустите API

```bash
docker restart ai-platform-api
```

### 4. Тест

```bash
curl -X POST http://localhost:8080/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Write Python hello world",
    "task_type": "code"
  }'
```

---

## 📝 Примеры использования

### Python клиент

```python
import httpx

async def test_lm_studio():
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:1234/v1/chat/completions",
            json={
                "model": "local-model",
                "messages": [{"role": "user", "content": "Hello!"}]
            }
        )
        print(response.json())

# import asyncio; asyncio.run(test_lm_studio())
```

### REST API

```bash
# Список моделей
curl http://localhost:1234/v1/models

# Chat completion
curl -X POST http://localhost:1234/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "local-model",
    "messages": [{"role": "user", "content": "Say hi"}]
  }'
```

---

## ✅ Checklist

- [ ] LM Studio запущен
- [ ] Local Server включен (порт 1234)
- [ ] Модель загружена в LM Studio
- [ ] API тест пройден: `curl http://localhost:1234/v1/models`
- [ ] Интеграция в FastAPI (если нужно)
- [ ] n8n workflow обновлён
- [ ] Тест полного стека

---

**Преимущества интеграции LM Studio:**

1. **Удобный GUI** для разработки и тестирования
2. **Гибридность** - можно переключаться между LM Studio и Ollama
3. **Совместимость** - OpenAI API format
4. **Мощность** - лучшая поддержка больших моделей

**Идеальный сценарий:**
- **Разработка**: LM Studio (GUI удобен для экспериментов)
- **Production**: Ollama (Docker, легковесный)

