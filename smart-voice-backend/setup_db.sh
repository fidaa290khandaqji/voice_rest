#!/bin/bash
# سكريبت لإعداد قاعدة البيانات محلياً

# تثبيت PostgreSQL (إذا لم يكن مثبتاً)
# macOS:
# brew install postgresql
# 
# Ubuntu:
# sudo apt-get install postgresql

# بدء خدمة PostgreSQL
# macOS: brew services start postgresql
# Ubuntu: sudo service postgresql start

# إنشاء قاعدة البيانات
psql -U postgres -c "CREATE DATABASE smart_voice_db;"
psql -U postgres -c "CREATE USER smart_voice WITH PASSWORD 'password';"
psql -U postgres -c "ALTER ROLE smart_voice SET client_encoding TO 'utf8';"
psql -U postgres -c "ALTER ROLE smart_voice SET default_transaction_isolation TO 'read committed';"
psql -U postgres -c "ALTER ROLE smart_voice SET default_transaction_deferrable TO on;"
psql -U postgres -c "ALTER ROLE smart_voice SET timezone TO 'UTC';"
psql -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE smart_voice_db TO smart_voice;"

echo "✅ تم إعداد قاعدة البيانات بنجاح!"
echo "DATABASE_URL=postgresql://smart_voice:password@localhost:5432/smart_voice_db"
