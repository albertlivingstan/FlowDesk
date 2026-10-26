import os
import tempfile
from pathlib import Path

p=Path(tempfile.mkdtemp())/'test.db'
os.environ['DATABASE_URL']='sqlite:///'+str(p)
os.environ['API_KEY']='test-secret'
from fastapi.testclient import TestClient
from app.main import app

client=TestClient(app)
H={'X-API-Key':'test-secret'}
P={'sender':'alex@example.org','subject':'Urgent: cannot log in','body':'Password reset is not working','source':'uipath','external_id':'msg-001'}

def test_security_and_health():
    assert client.get('/health').status_code==200
    assert client.get('/api/tickets').status_code==401

def test_ticket_lifecycle():
    with TestClient(app) as c:
        r=c.post('/api/tickets',json=P,headers=H)
        assert r.status_code==201,r.text
        t=r.json()['ticket'];id=t['id'];assert t['priority']=='Critical';assert t['category']=='Access & Login'
        r2=c.post('/api/tickets',json=P,headers=H)
        assert r2.json()['duplicate'] is True
        listing=c.get('/api/tickets',headers=H).json()
        assert listing['total']==1
        assert c.patch(f'/api/tickets/{id}',headers=H,json={'status':'Resolved'}).json()['status']=='Resolved'
        assert c.post(f'/api/tickets/{id}/notes',headers=H,json={'message':'Issue fixed'}).status_code==201
        assert len(c.get(f'/api/tickets/{id}',headers=H).json()['events'])==3
        assert 'Urgent' in c.get('/api/export.csv',headers=H).text
        assert c.get('/api/stats',headers=H).json()['total']==1

def test_validation():
    with TestClient(app) as c:
        assert c.post('/api/tickets',headers=H,json={**P,'sender':'bad'}).status_code==422
        assert c.post('/api/tickets',headers=H,json={**P,'external_id':None}).status_code==422
        assert c.patch('/api/tickets/99999',headers=H,json={'status':'Closed'}).status_code==404
