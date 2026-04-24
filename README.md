# SMART VOICE RECEPTION AI

نظام استقبال مكالمات ذكي للمطاعم باستخدام AI

## 📁 هيكل المشروع

```
smart-voice-reception-ai/
├── frontend/                          # الواجهة الأمامية
│   ├── SMART VOICE RECEPTION AI.html  # التطبيق كامل (React)
│   └── SMART VOICE RECEPTION AI - Deploy.html  # نسخة مستقلة
│
├── backend/                           # السيرفر
│   ├── app.py                         # الكود الرئيسي
│   ├── requirements.txt               # المكتبات
│   ├── test_app.py                    # الاختبارات
│   ├── setup_db.sh                    # إعداد قاعدة البيانات
│   ├── .env.example                   # قالب الإعدادات
│   ├── .gitignore                     # ملفات غير متابعة
│   ├── Procfile                       # إعدادات Railway
│   └── README.md                      # دليل الـ Backend
│
├── docs/                              # التوثيق
│   ├── SETUP_GUIDE.html               # دليل الإعداد الكامل
│   ├── API_DOCS.md                    # توثيق الـ API
│   └── ARCHITECTURE.md                # العمارة التقنية
│
└── README.md                          # ملف المشروع الرئيسي
```

## 🚀 البدء السريع

### المتطلبات
- Python 3.9+
- PostgreSQL
- حساب OpenAI
- حساب Twilio

### التشغيل المحلي

```bash
# 1. تثبيت المكتبات
pip install -r backend/requirements.txt

# 2. إعداد قاعدة البيانات
bash backend/setup_db.sh

# 3. إنشاء ملف الإعدادات
cp backend/.env.example backend/.env

# 4. التشغيل
python backend/app.py
```

### الواجهة الأمامية
افتح `frontend/SMART VOICE RECEPTION AI.html` مباشرة في المتصفح

## 🔌 الربط مع Twilio

1. استقبل مكالمة على رقم Twilio
2. وجّهها إلى Webhook: `https://your-app.railway.app/call`
3. النظام يستقبل الصوت ويرد تلقائياً

## 📊 قاعدة البيانات

- **Calls**: تفاصيل المكالمات
- **Messages**: سجل المحادثات
- **Orders**: الطلبات والمبيعات

## 🛡️ الأمان

- API محمية بـ Token Bearer
- بيانات الدخول آمنة (متغيرات البيئة)
- CORS مفعّل

## 📄 الترخيص

MIT License

## 📞 الدعم

للمساعدة، افتح Issue على GitHub.
