cat > /app/bot/update.sh << 'EOF'
#!/bin/bash
cd /app/bot
git pull origin main
echo "✅ Код обновлён!"
echo "➡️ Перезапусти бота в панели."
EOF

chmod +x /app/bot/update.sh
