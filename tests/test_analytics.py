import os
os.environ["API_KEY"] = "test-secret"
from fastapi.testclient import TestClient
from app.main import app,API_KEY

def test_analytics_contract():
    with TestClient(app) as c:
        h={'X-API-Key':API_KEY}
        bad=c.get('/api/analytics')
        assert bad.status_code==401
        res=c.get('/api/analytics?days=7',headers=h)
        assert res.status_code==200
        data=res.json()
        assert len(data['volume'])==7
        assert len(data['hourly'])==24
        assert data['data_source']=='persisted_tickets'
        assert 'sla_proxy_overdue' in data
        assert c.get('/api/analytics?days=2',headers=h).status_code==422
