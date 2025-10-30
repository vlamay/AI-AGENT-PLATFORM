# ⚡ Быстрый старт с LM Studio

## 🎯 У вас уже есть LM Studio!

**Статус**: ✅ LM Studio запущен  
**Что нужно**: Включить API сервер

---

## 📋 3 простых шага

### Шаг 1: Запустите Local Server в LM Studio

1. Откройте LM Studio (уже запущен)
2. В боковой панели найдите **"Local Server"**
3. Нажмите **"Start Server"**
4. Выберите порт (по умолчанию: 1234)
5. Нажмите **"Start"**

**Готово!** LM Studio API теперь слушает на порту 1234.

---

### Шаг 2: Проверьте API

```bash
# Проверка доступности
curl http://localhost:1234/v1/models

# Должен вернуть список моделей в JSON
```

Если видите список моделей → ✅ API работает!

---

### Шаг 3: Протестируйте

```bash
# Тест генерации
curl -X POST http://localhost:1234/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "local-model",
    "messages": [{"role": "user", "content": "Say hello!"}],
    "temperature": 0.7
  }'
```

---

## 🔄 Интеграция с проектом

### Использование в n8n

В n8n добавьте HTTP Request node:

**URL**: `http://localhost:1234/v1/chat/completions`

**Method**: POST

**Body** (JSON):
```json
{
  "model": "local-model",
  "messages": [{"role": "user", "content": "{{ $json.body.prompt }}"}],
  "temperature": 0.7
}
```

---

## 🚀 Преимущества LM Studio

✅ **Графический интерфейс** - управление через UI  
✅ **Легкая загрузка моделей** - клик для установки  
✅ **OpenAI-совместимый API** - стандартный формат  
✅ **CUDA поддержка** - использует NVIDIA GPU  
✅ **Switching моделей** - переключение одной кнопкой  

---

## 📊 LM Studio vs Ollama

| Task | LM Studio | Ollama |
|------|-----------|--------|
| Управление моделями | ✅ GUI | ❌ CLI |
| API для кода | ✅ Да | ✅ Да |
| Production deploy | ⚠️ Нужен GUI | ✅ Docker |
| Удобство для dev | ✅ Отлично | ⚠️ Средне |

---

## 🎯 Рекомендация

**Для вашего случая (разработка на ASUS TUF laptop):**

✅ **Используйте LM Studio** как основной LLM  
✅ **Держите Ollama** как backup (уже запущен)  
✅ **Переключайтесь** между ними в зависимости от задачи  

**Пример:**
- **Dev/Тестирование**: LM Studio (UI удобен)
- **Production**: Ollama (Docker deployment)

---

## 🔗 Полезные ссылки

**LM Studio Docs**: https://lmstudio.ai/docs  
**API Reference**: http://localhost:1234/docs (после запуска сервера)

---

**Готово! Теперь у вас работают оба: LM Studio + Ollama** 🎉

