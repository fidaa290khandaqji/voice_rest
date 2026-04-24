"""
╔══════════════════════════════════════════════════════════════╗
║         SMART VOICE RECEPTION AI — السيرفر محسّن              ║
║         مع قاعدة بيانات PostgreSQL + API محسّنة             ║
╚══════════════════════════════════════════════════════════════╝
"""

import os, json, tempfile, uuid, requests, logging
from datetime import datetime, timedelta
from functools import wraps
from flask import Flask, request, Response, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
from flask_cors import CORS
from twilio.twiml.voice_response import VoiceResponse, Gather
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()  # إضافة تحميل ملف .env

# ── إعداد logging ──────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ── إعداد التطبيق ──────────────────────────────────────────────
app = Flask(__name__, static_folder="static")
CORS(app)

# قاعدة البيانات
# قاعدة البيانات
DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///local_dev.db")

# تجاهل إعداد قاعدة البيانات الافتراضي في ملف .env إذا لم يتم تغييره (لضمان عمل SQLite)
if DATABASE_URL == "postgresql://postgres:password@localhost:5432/smart_voice_db":
    DATABASE_URL = "sqlite:///local_dev.db"

if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
RESTAURANT_NAME = os.environ.get("RESTAURANT_NAME", "مطعم الزيتون الذهبي")

RESTAURANT_PROMPT = f"""
أنت مساعد صوتي ذكي لـ "{RESTAURANT_NAME}".
قواعد المحادثة:
- تتحدث بالعربية فقط، أسلوب ودود ومختصر
- ردودك جملتين أو ثلاثة كحد أقصى
- تستقبل طلبات التوصيل والاستفسارات

المنيو:
- شاورما دجاج: 14₪
- شاورما لحم: 18₪
- فلافل صحن: 8₪
- حمص: 6₪
- مندي دجاج: 35₪
- برغر لحم: 20₪
- بطاطا مقلية: 5₪
- مشروبات: 4₪

سياسة التوصيل:
- التوصيل مجاني للطلبات فوق 30₪
- رسوم توصيل 5₪ للطلبات الأقل
- وقت التوصيل 45-60 دقيقة

عند اكتمال الطلب، قل: "تم تسجيل طلبك"
"""

# ══════════════════════════════════════════════════════════════
# MODELS — نماذج قاعدة البيانات
# ══════════════════════════════════════════════════════════════

class Call(db.Model):
    """نموذج المكالمة"""
    __tablename__ = "calls"
    
    id = db.Column(db.String(50), primary_key=True, default=lambda: f"CALL-{uuid.uuid4().hex[:8]}")
    call_sid = db.Column(db.String(100), unique=True, nullable=False)
    caller_phone = db.Column(db.String(20), nullable=False)
    status = db.Column(db.String(20), default="active")  # active, completed, failed
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    ended_at = db.Column(db.DateTime)
    duration = db.Column(db.Integer, default=0)  # بالثواني
    mood = db.Column(db.String(20))  # سعيد، محايد، مستاء
    ai_model = db.Column(db.String(20), default="gpt-4o")
    
    # العلاقات
    messages = db.relationship("Message", backref="call", lazy=True, cascade="all, delete-orphan")
    order = db.relationship("Order", backref="call", uselist=False)
    
    def to_dict(self):
        return {
            "id": self.id,
            "call_sid": self.call_sid,
            "caller_phone": self.caller_phone,
            "status": self.status,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "ended_at": self.ended_at.isoformat() if self.ended_at else None,
            "duration": self.duration,
            "mood": self.mood,
        }


class Message(db.Model):
    """نموذج الرسالة (الحوار)"""
    __tablename__ = "messages"
    
    id = db.Column(db.Integer, primary_key=True)
    call_id = db.Column(db.String(50), db.ForeignKey("calls.id"), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # user, assistant
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    confidence = db.Column(db.Float, default=1.0)  # لـ speech-to-text
    
    def to_dict(self):
        return {
            "role": self.role,
            "content": self.content,
            "timestamp": self.timestamp.isoformat(),
            "confidence": self.confidence
        }


class Order(db.Model):
    """نموذج الطلب"""
    __tablename__ = "orders"
    
    id = db.Column(db.String(50), primary_key=True, default=lambda: f"ORD-{uuid.uuid4().hex[:6].upper()}")
    call_id = db.Column(db.String(50), db.ForeignKey("calls.id"), unique=True)
    phone = db.Column(db.String(20), nullable=False)
    address = db.Column(db.String(255))
    items = db.Column(db.JSON)  # [{name, quantity, price}]
    total = db.Column(db.Float, default=0)
    discount = db.Column(db.Float, default=0)
    status = db.Column(db.String(20), default="active")  # active, preparing, ready, delivered, cancelled
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    notes = db.Column(db.Text)
    
    def to_dict(self):
        return {
            "id": self.id,
            "phone": self.phone,
            "address": self.address,
            "items": self.items,
            "total": self.total,
            "discount": self.discount,
            "status": self.status,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "notes": self.notes
        }


# ══════════════════════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════════════════════

def log_event(event_type: str, data: dict):
    """تسجيل الأحداث"""
    logger.info(f"[{event_type}] {json.dumps(data, ensure_ascii=False)}")

def token_required(f):
    """حماية API بـ token"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get("Authorization")
        if not token or token != f"Bearer {os.environ.get('API_TOKEN', 'secret-token')}":
            return jsonify({"error": "Unauthorized"}), 401
        return f(*args, **kwargs)
    return decorated

def get_gpt_response(history: list) -> str:
    """الحصول على رد من GPT-4"""
    messages = [{"role": "system", "content": RESTAURANT_PROMPT}] + history[-10:]
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            max_tokens=150,
            temperature=0.7
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        logger.error(f"GPT Error: {str(e)}")
        return "عذراً، حدثت مشكلة تقنية. حاول مرة أخرى من فضلك."

def text_to_speech(text: str) -> str:
    """تحويل النص لصوت"""
    os.makedirs("static/audio", exist_ok=True)
    provider = os.environ.get("TTS_PROVIDER", "openai")
    filename = f"{uuid.uuid4().hex}.mp3"
    filepath = f"static/audio/{filename}"
    
    try:
        if provider == "elevenlabs":
            voice_id = os.environ["ELEVENLABS_VOICE_ID"]
            api_key = os.environ["ELEVENLABS_API_KEY"]
            r = requests.post(
                f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}",
                headers={"xi-api-key": api_key, "Content-Type": "application/json"},
                json={
                    "text": text,
                    "model_id": "eleven_multilingual_v2",
                    "voice_settings": {"stability": 0.55, "similarity_boost": 0.80}
                },
                timeout=15
            )
            with open(filepath, "wb") as f:
                f.write(r.content)
        else:
            response = client.audio.speech.create(model="tts-1", voice="shimmer", input=text)
            response.stream_to_file(filepath)
        
        base_url = os.environ.get("BASE_URL", "http://localhost:5000")
        return f"{base_url}/static/audio/{filename}"
    except Exception as e:
        logger.error(f"TTS Error: {str(e)}")
        return ""

# ══════════════════════════════════════════════════════════════
# ROUTES
# ══════════════════════════════════════════════════════════════

@app.route("/", methods=["GET"])
def health():
    """فحص صحة السيرفر"""
    try:
        db.session.execute(text("SELECT 1"))
        db_status = "✅"
    except:
        db_status = "❌"
    
    return jsonify({
        "status": "✅ النظام يعمل",
        "restaurant": RESTAURANT_NAME,
        "database": db_status,
        "timestamp": datetime.utcnow().isoformat()
    })

@app.route("/call", methods=["POST"])
def handle_incoming_call():
    """استقبال المكالمة من Twilio"""
    call_sid = request.form.get("CallSid", "")
    caller = request.form.get("From", "unknown")
    
    # إنشاء سجل المكالمة
    call = Call(call_sid=call_sid, caller_phone=caller)
    db.session.add(call)
    db.session.commit()
    
    log_event("CALL_RECEIVED", {"call_sid": call_sid, "caller": caller, "db_id": call.id})
    
    welcome = f"أهلاً وسهلاً، {RESTAURANT_NAME}، معك المساعد الذكي. كيف أقدر أساعدك؟"
    audio_url = text_to_speech(welcome)
    
    resp = VoiceResponse()
    gather = Gather(
        input="speech", action="/respond", language="ar-SA",
        speech_timeout="auto", enhanced="true", timeout=8
    )
    if audio_url:
        gather.play(audio_url)
    resp.append(gather)
    resp.redirect("/no_input")
    
    return Response(str(resp), mimetype="text/xml")

@app.route("/respond", methods=["POST"])
def process_response():
    """معالجة رد الزبون"""
    call_sid = request.form.get("CallSid", "")
    speech_text = request.form.get("SpeechResult", "").strip()
    confidence = float(request.form.get("Confidence", 0))
    
    call = Call.query.filter_by(call_sid=call_sid).first()
    if not call:
        return _error_response("لم أتمكن من العثور على المكالمة")
    
    # حفظ رسالة الزبون
    msg_user = Message(call_id=call.id, role="user", content=speech_text, confidence=confidence)
    db.session.add(msg_user)
    
    if not speech_text or confidence < 0.3:
        ai_text = "لم أفهم، ممكن تعيد من فضلك؟"
    else:
        # جلب السجل الكامل
        history = [{"role": m.role, "content": m.content} for m in call.messages]
        history.append({"role": "user", "content": speech_text})
        ai_text = get_gpt_response(history)
    
    # حفظ رد الـ AI
    msg_ai = Message(call_id=call.id, role="assistant", content=ai_text)
    db.session.add(msg_ai)
    db.session.commit()
    
    log_event("MESSAGE_EXCHANGE", {"call_id": call.id, "user": speech_text, "ai": ai_text})
    
    audio_url = text_to_speech(ai_text)
    resp = VoiceResponse()
    
    # إذا انتهت المكالمة
    if "تم تسجيل طلبك" in ai_text:
        if audio_url:
            resp.play(audio_url)
        call.status = "completed"
        call.ended_at = datetime.utcnow()
        call.duration = int((call.ended_at - call.started_at).total_seconds())
        db.session.commit()
        resp.hangup()
    else:
        gather = Gather(
            input="speech", action="/respond", language="ar-SA",
            speech_timeout="auto", timeout=8
        )
        if audio_url:
            gather.play(audio_url)
        resp.append(gather)
        resp.redirect("/no_input")
    
    return Response(str(resp), mimetype="text/xml")

@app.route("/no_input", methods=["POST"])
def no_input():
    """لا يوجد صوت من الزبون"""
    resp = VoiceResponse()
    gather = Gather(
        input="speech", action="/respond", language="ar-SA", speech_timeout="auto"
    )
    audio_url = text_to_speech("هل أنت موجود؟ كيف أقدر أساعدك؟")
    if audio_url:
        gather.play(audio_url)
    resp.append(gather)
    resp.hangup()
    return Response(str(resp), mimetype="text/xml")

def _error_response(msg):
    resp = VoiceResponse()
    resp.say(msg, language="ar")
    resp.hangup()
    return Response(str(resp), mimetype="text/xml")

# ═══════════════════════════════════════════════════════════════
# API — لوحة التحكم
# ═══════════════════════════════════════════════════════════════

@app.route("/api/orders", methods=["GET"])
@token_required
def get_orders():
    """جميع الطلبات"""
    orders = Order.query.order_by(Order.created_at.desc()).all()
    return jsonify([o.to_dict() for o in orders])

@app.route("/api/orders/<order_id>", methods=["GET"])
@token_required
def get_order(order_id):
    """تفاصيل طلب"""
    order = Order.query.get_or_404(order_id)
    return jsonify(order.to_dict())

@app.route("/api/orders/<order_id>/status", methods=["PUT"])
@token_required
def update_order_status(order_id):
    """تحديث حالة الطلب"""
    order = Order.query.get_or_404(order_id)
    data = request.get_json()
    order.status = data.get("status", order.status)
    order.notes = data.get("notes", order.notes)
    db.session.commit()
    log_event("ORDER_UPDATED", {"order_id": order_id, "status": order.status})
    return jsonify(order.to_dict())

@app.route("/api/calls/<call_id>", methods=["GET"])
@token_required
def get_call(call_id):
    """تفاصيل مكالمة"""
    call = Call.query.get_or_404(call_id)
    data = call.to_dict()
    data["messages"] = [m.to_dict() for m in call.messages]
    return jsonify(data)

@app.route("/api/stats", methods=["GET"])
@token_required
def get_stats():
    """إحصائيات"""
    today = datetime.utcnow().date()
    
    total_calls = Call.query.count()
    today_calls = Call.query.filter(Call.started_at >= datetime.combine(today, datetime.min.time())).count()
    
    total_orders = Order.query.count()
    today_orders = Order.query.filter(Order.created_at >= datetime.combine(today, datetime.min.time())).count()
    
    total_revenue = db.session.query(db.func.sum(Order.total)).scalar() or 0
    today_revenue = db.session.query(db.func.sum(Order.total)).filter(
        Order.created_at >= datetime.combine(today, datetime.min.time())
    ).scalar() or 0
    
    return jsonify({
        "calls": {"total": total_calls, "today": today_calls},
        "orders": {"total": total_orders, "today": today_orders},
        "revenue": {"total": float(total_revenue), "today": float(today_revenue)}
    })

# ══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        logger.info(f"🚀 {RESTAURANT_NAME} — السيرفر يعمل على http://0.0.0.0:5000")
    app.run(host="0.0.0.0", port=5000, debug=False)
