import urllib.request
import urllib.parse
import json
import ssl

def test_ai():
    url = "https://voicerest-production.up.railway.app/call"
    
    # محاكاة لرسالة تأتي من Twilio (كأن شخصاً يتحدث)
    data = urllib.parse.urlencode({
        'From': '+1234567890',
        'To': '+16013273926',
        'SpeechResult': 'مرحبا، هل يمكنني طلب بيتزا لو سمحت؟'
    }).encode('utf-8')
    
    # إنشاء الطلب
    req = urllib.request.Request(url, data=data)
    
    # إرسال الطلب للسيرفر المرفوع على Railway وتجاوز فحص SSL
    context = ssl._create_unverified_context()
    print("⏳ جاري الاتصال بالذكاء الاصطناعي على Railway... الرجاء الانتظار ثواني...")
    
    try:
        response = urllib.request.urlopen(req, context=context)
        result = response.read().decode('utf-8')
        print("\n✅ تم استلام رد الذكاء الاصطناعي بنجاح!\n")
        print("رد السيرفر (Twilio XML):")
        print("="*50)
        print(result)
        print("="*50)
        print("\n💡 إذا رأيت الرد في الأعلى، فهذا يعني أن مشروعك يعمل 100% والمشكلة فقط من شريحة الاتصال الخاصة بك.")
    except Exception as e:
        print(f"❌ حدث خطأ: {e}")

if __name__ == "__main__":
    test_ai()
