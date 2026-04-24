# API Documentation

## المصادقة

جميع الـ API endpoints (ما عدا `/call` و `/respond`) تحتاج:

```
Authorization: Bearer YOUR_API_TOKEN
```

## Endpoints

### 📞 المكالمات

#### استقبال مكالمة
```
POST /call
Content-Type: application/x-www-form-urlencoded

من Twilio (تلقائي)
CallSid, From, ...
```

#### معالجة الرد
```
POST /respond
Content-Type: application/x-www-form-urlencoded

SpeechResult, Confidence, CallSid
```

### 📋 الطلبات

#### جميع الطلبات
```
GET /api/orders
Authorization: Bearer TOKEN

Response:
[
  {
    "id": "ORD-ABC123",
    "phone": "+970595206620",
    "address": "رام الله - البيرة",
    "items": [...],
    "total": 45,
    "discount": 5,
    "status": "preparing",
    "created_at": "2026-04-24T15:32:10",
    "updated_at": "2026-04-24T15:33:20"
  }
]
```

#### طلب محدد
```
GET /api/orders/:order_id
Authorization: Bearer TOKEN
```

#### تحديث حالة الطلب
```
PUT /api/orders/:order_id/status
Authorization: Bearer TOKEN
Content-Type: application/json

{
  "status": "ready",
  "notes": "الطلب جاهز للتوصيل"
}
```

### 📞 المكالمات

#### تفاصيل مكالمة
```
GET /api/calls/:call_id
Authorization: Bearer TOKEN

Response:
{
  "id": "CALL-abc123",
  "call_sid": "CA...",
  "caller_phone": "+970595206620",
  "status": "completed",
  "started_at": "2026-04-24T15:32:00",
  "ended_at": "2026-04-24T15:34:30",
  "duration": 150,
  "messages": [
    {"role": "user", "content": "بدي أطلب...", "timestamp": "..."},
    {"role": "assistant", "content": "تمام...", "timestamp": "..."}
  ]
}
```

### 📊 الإحصائيات

```
GET /api/stats
Authorization: Bearer TOKEN

Response:
{
  "calls": {"total": 247, "today": 38},
  "orders": {"total": 200, "today": 32},
  "revenue": {"total": 8420, "today": 1340}
}
```

### ❤️ فحص السيرفر

```
GET /
(بدون Authorization)

Response:
{
  "status": "✅ النظام يعمل",
  "restaurant": "مطعم الزيتون الذهبي",
  "database": "✅",
  "timestamp": "2026-04-24T15:35:00"
}
```

## أكواد الأخطاء

- `200`: نجاح ✅
- `401`: بدون تصريح (Token مفقود أو خاطئ)
- `404`: الموارد غير موجودة
- `500`: خطأ السيرفر
