"""
اختبارات وحدة للـ Backend
"""

import pytest
import json
from app import app, db, Call, Message, Order

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    with app.app_context():
        db.create_all()
        yield app.test_client()
        db.session.remove()
        db.drop_all()

def test_health_check(client):
    """اختبار فحص صحة السيرفر"""
    response = client.get('/')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'status' in data
    assert '✅' in data['status']

def test_api_requires_token(client):
    """اختبار حماية API بـ token"""
    response = client.get('/api/stats')
    assert response.status_code == 401

def test_api_with_token(client):
    """اختبار API مع token صحيح"""
    headers = {'Authorization': 'Bearer secret-token'}
    response = client.get('/api/stats', headers=headers)
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'calls' in data
    assert 'orders' in data

def test_create_call(client):
    """اختبار إنشاء مكالمة"""
    with app.app_context():
        call = Call(call_sid='TEST123', caller_phone='+970595206620')
        db.session.add(call)
        db.session.commit()
        
        assert call.id is not None
        assert call.status == 'active'

def test_add_message(client):
    """اختبار إضافة رسالة"""
    with app.app_context():
        call = Call(call_sid='TEST456', caller_phone='+970595206620')
        db.session.add(call)
        db.session.commit()
        
        msg = Message(call_id=call.id, role='user', content='بدي أطلب شاورما')
        db.session.add(msg)
        db.session.commit()
        
        assert msg.id is not None
        assert msg.role == 'user'
        assert len(call.messages) == 1

if __name__ == '__main__':
    pytest.main([__file__, '-v'])
