# 🤖 SMART VOICE RECEPTION AI — Backend
## نظام استقبال مكالمات ذكي مع قاعدة بيانات

---

## 🆕 التحديثات الجديدة

✅ **قاعدة بيانات PostgreSQL**
- جدول Calls — تفاصيل المكالمات
- جدول Messages — السجل الكامل للمحادثات
- جدول Orders — الطلبات والبيانات

✅ **API محسّنة**
- حماية بـ Token
- معالجة الأخطاء الشاملة
- إحصائيات وتقارير

✅ **Logging شامل**
- تسجيل كل حدث
- ملف `app.log` لكل الأحداث

✅ **Unit Tests**
- اختبارات تلقائية
- تغطية جميع الـ Endpoints

---

## 🚀 التشغيل المحلي

### 1. إعداد قاعدة البيانات

```bash
# على macOS
brew install postgresql
brew services start postgresql

# أو شغّل السكريبت
bash setup_db.sh
```

### 2. إعداد البيئة

```bash
cp .env.example .env
# ثم عدّل .env بمفاتيحك الحقيقية
```

### 3. تثبيت والتشغيل

```bash
pip install -r requirements.txt
python app.py
```

---

## 🧪 تشغيل الاختبارات

```bash
pip install pytest
pytest test_app.py -v
```

---

## 📊 API Endpoints

| Endpoint | Method | حماية | الوظيفة |
|----------|--------|-------|--------|
| `/` | GET | ❌ | فحص السيرفر |
| `/call` | POST | ❌ | استقبال مكالمة |
| `/respond` | POST | ❌ | رد الزبون |
| `/api/orders` | GET | ✅ | جميع الطلبات |
| `/api/orders/:id` | GET | ✅ | تفاصيل طلب |
| `/api/orders/:id/status` | PUT | ✅ | تحديث الحالة |
| `/api/calls/:id` | GET | ✅ | تفاصيل مكالمة |
| `/api/stats` | GET | ✅ | إحصائيات |

### مثال على الطلب محمي:

```bash
curl https://your-app.railway.app/api/stats \
  -H "Authorization: Bearer your-secret-token"
```

---

## 🗄️ نموذج قاعدة البيانات

### Calls
```
id: CALL-xxx
call_sid: من Twilio
caller_phone: +970595206620
status: active/completed/failed
started_at: datetime
ended_at: datetime
duration: ثواني
mood: سعيد/محايد/مستاء
messages: [Message]
order: Order (واحد لواحد)
```

### Messages
```
id: int
call_id: FK → Calls
role: user/assistant
content: النص
timestamp: datetime
confidence: float (0-1)
```

### Orders
```
id: ORD-xxx
call_id: FK → Calls
phone: رقم الزبون
address: عنوان التوصيل
items: JSON [{name, qty, price}]
total: السعر النهائي
discount: الخصم
status: active/preparing/ready/delivered/cancelled
```

---

## 🔧 خطوات النشر على Railway

### 1. ربط GitHub

```bash
git init
git add .
git commit -m "Add PostgreSQL and improved API"
git remote add origin https://github.com/USERNAME/smart-voice-ai.git
git push -u origin main
```

### 2. إعداد Railway

```
1. روح railway.app
2. New Project → Deploy from GitHub
3. اختر الـ Repo
4. Variables:
   DATABASE_URL: سيُعيّن تلقائياً من Railway
   OPENAI_API_KEY: مفتاحك
   ... باقي المفاتيح
```

### 3. تشغيل Migrations

```bash
# في Railway Console
python
from app import app, db
with app.app_context():
    db.create_all()
```

---

## 📝 Logging

كل الأحداث تُحفظ في `app.log`:

```
2026-04-24 15:32:10 - app - INFO - [CALL_RECEIVED] {"call_sid": "CA123", "caller": "+970595206620"}
2026-04-24 15:32:15 - app - INFO - [MESSAGE_EXCHANGE] {"call_id": "CALL-abc123", "user": "بدي أطلب...", "ai": "تمام..."}
2026-04-24 15:33:20 - app - INFO - [ORDER_UPDATED] {"order_id": "ORD-ABC123", "status": "ready"}
```

---

## 🆘 Troubleshooting

**PostgreSQL لا يعمل:**
```bash
# تحقق من التثبيت
psql --version

# أعد التشغيل
brew services restart postgresql
```

**API بدون token:**
```bash
# أضف Header
Authorization: Bearer your-secret-token
```

**الصوت لا يعمل:**
- تحقق من OPENAI_API_KEY
- تحقق من رصيد OpenAI

---

## 📞 الدعم

أي مشكلة؟ افتح issue على GitHub.
