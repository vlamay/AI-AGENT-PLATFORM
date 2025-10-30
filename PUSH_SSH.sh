#!/bin/bash

echo "╔════════════════════════════════════════════════════════════╗"
echo "║  🚀 AI AGENT PLATFORM - PUSH TO GITHUB VIA SSH           ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

cd /home/devops/Downloads/AI-AGENT-PLATFORM

echo "📋 Твой SSH ключ:"
echo ""
cat ~/.ssh/id_ed25519.pub
echo ""

read -p "Добавил ключ в GitHub? (y/n): " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo ""
    echo "🔧 Настраиваю SSH remote..."
    git remote set-url origin git@github.com:vlamay/AI-AGENT-PLATFORM.git
    
    echo ""
    echo "🚀 Отправляю в GitHub..."
    git push -u origin main
    
    if [ $? -eq 0 ]; then
        echo ""
        echo "✅ Успешно отправлено в GitHub!"
        echo "🌐 Проверь: https://github.com/vlamay/AI-AGENT-PLATFORM"
        echo ""
        echo "📊 Статистика:"
        echo "  • Файлов: $(git ls-files | wc -l)"
        echo "  • Коммитов: $(git rev-list --all --count)"
        echo ""
        echo "🎉 Поздравляю! Проект на GitHub!"
    else
        echo ""
        echo "❌ Ошибка при отправке"
        echo "📋 Проверь:"
        echo "  1. Ключ добавлен в GitHub"
        echo "  2. Репозиторий существует"
        echo "  3. У тебя есть доступ"
    fi
else
    echo ""
    echo "⏸️  Добавь ключ в GitHub и запусти скрипт снова"
    echo "🔗 https://github.com/settings/keys"
fi

