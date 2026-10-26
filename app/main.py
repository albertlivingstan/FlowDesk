"""FlowDesk Pro — auditable email-to-ticket backend."""
import csv
import hmac
import io
import os
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Literal
from fastapi import Depends, FastAPI, Header, HTTPException, Query
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel, Field
from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text, UniqueConstraint, create_engine, func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, sessionmaker

from .classifier import classify

BASE_DIR = Path(__file__).resolve().parent.parent
DB_URL = os.getenv('DATABASE_URL', 'sqlite:///' + str(BASE_DIR / 'flowdesk.db'))
API_KEY = os.getenv('API_KEY', 'dev-only-change-me')
if os.getenv('APP_ENV', 'development').lower() == 'production' and (API_KEY == 'dev-only-change-me' or len(API_KEY) < 24):
    raise RuntimeError('Set a strong API_KEY in production (24+ chars)')
engine = create_engine(DB_URL, pool_pre_ping=True, connect_args={'check_same_thread':False} if DB_URL.startswith('sqlite') else {})
SessionLocal = sessionmaker(engine, expire_on_commit=False)

class Base(DeclarativeBase): pass
class Ticket(Base):
    __tablename__ = 'tickets'
    __table_args__ = (UniqueConstraint('source', 'external_id', name='uq_source_external'),)
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    source: Mapped[str] = mapped_column(String(40), nullable=False, default='demo')
    external_id: Mapped[str|None] = mapped_column(String(255), nullable=True)
    sender: Mapped[str] = mapped_column(String(254), nullable=False)
    subject: Mapped[str] = mapped_column(String(300), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    category: Mapped[str] = mapped_column(String(80), nullable=False)
    priority: Mapped[str] = mapped_column(String(20), nullable=False)
    assigned_team: Mapped[str] = mapped_column(String(80), nullable=False)
    confidence: Mapped[float] = mapped_column(Float, nullable=False)
    review_required: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default='Open')
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

class Event(Base):
    __tablename__ = 'ticket_events'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    ticket_id: Mapped[int] = mapped_column(ForeignKey('tickets.id', ondelete='CASCADE'), nullable=False, index=True)
    kind: Mapped[str] = mapped_column(String(40), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    actor: Mapped[str] = mapped_column(String(80), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

class TicketInput(BaseModel):
    sender: str = Field(min_length=5, max_length=254, pattern=r'^[^\s@]+@[^\s@]+\.[^\s@]+$')
    subject: str = Field(min_length=1, max_length=300)
    body: str = Field(min_length=1, max_length=20000)
    source: Literal['demo','uipath','imap','api'] = 'demo'
    external_id: str|None = Field(None, max_length=255)

class TicketUpdate(BaseModel):
    status: Literal['Open','In Progress','Resolved','Closed']|None = None
    priority: Literal['Normal','High','Critical']|None = None
    assigned_team: str|None = Field(default=None,min_length=2,max_length=80)
    review_required: bool|None = None

class NoteInput(BaseModel):
    message: str = Field(min_length=1,max_length=4000)
    actor: str = Field(default='Agent',min_length=1,max_length=80)

@asynccontextmanager
async def lifespan(app:FastAPI):
    Base.metadata.create_all(engine)
    yield
app = FastAPI(title='FlowDesk Pro', version='3.0.0', lifespan=lifespan)

def session():
    with SessionLocal() as db:
        yield db

def auth(x_api_key: str|None=Header(default=None)):
    if not x_api_key or not hmac.compare_digest(x_api_key, API_KEY):
        raise HTTPException(status_code=401, detail='Invalid API key')

def data(t:Ticket):
    return {k:getattr(t,k) for k in ['id','sender','subject','body','source','external_id','category','priority','assigned_team','confidence','review_required','status'] } | {'created_at': t.created_at.isoformat(), 'updated_at':t.updated_at.isoformat()}

def log(db:Session, t:Ticket, kind:str, message:str,actor:str='System'):
    db.add(Event(ticket_id=t.id,kind=kind,message=message,actor=actor))

@app.get('/')
def home(): return FileResponse(BASE_DIR / 'static' / 'index.html')
@app.get('/health')
def health(): return {'status':'ok','version':'3.0.0'}

@app.post('/api/tickets', dependencies=[Depends(auth)],status_code=201)
def create_ticket(payload:TicketInput, db:Session=Depends(session)):
    if payload.source != 'demo' and not payload.external_id:
        raise HTTPException(422,'external_id is required for automated sources')
    if payload.external_id:
        existing = db.scalar(select(Ticket).where(Ticket.source==payload.source,Ticket.external_id==payload.external_id))
        if existing: return {'ticket':data(existing),'duplicate':True}
    classification = classify(payload.subject,payload.body)
    t=Ticket(**payload.model_dump(),**classification)
    db.add(t)
    try:
        db.flush()
        log(db,t,'created',f'Ticket created from {payload.source}; assigned to {t.assigned_team}')
        db.commit()
    except IntegrityError:
        db.rollback()
        existing=db.scalar(select(Ticket).where(Ticket.source==payload.source,Ticket.external_id==payload.external_id))
        if existing: return {'ticket':data(existing),'duplicate':True}
        raise
    return {'ticket':data(t),'duplicate':False}

@app.get('/api/tickets',dependencies=[Depends(auth)])
def list_tickets(status:str|None=None,category:str|None=None,priority:str|None=None,q:str|None=Query(None,max_length=120),page:int=Query(1,ge=1),size:int=Query(25,ge=1,le=100),db:Session=Depends(session)):
    stmt=select(Ticket)
    if status: stmt=stmt.where(Ticket.status==status)
    if category: stmt=stmt.where(Ticket.category==category)
    if priority: stmt=stmt.where(Ticket.priority==priority)
    if q: stmt=stmt.where(Ticket.subject.ilike('%'+q+'%') | Ticket.sender.ilike('%'+q+'%'))
    count=db.scalar(select(func.count()).select_from(stmt.subquery())) or 0
    rows=db.scalars(stmt.order_by(Ticket.created_at.desc(),Ticket.id.desc()).offset((page-1)*size).limit(size)).all()
    return {'items':[data(t) for t in rows],'total':count,'page':page,'size':size}

@app.get('/api/tickets/{ticket_id}',dependencies=[Depends(auth)])
def get_ticket(ticket_id:int,db:Session=Depends(session)):
    t=db.get(Ticket,ticket_id)
    if not t: raise HTTPException(404,'Ticket not found')
    ev=db.scalars(select(Event).where(Event.ticket_id==ticket_id).order_by(Event.id.desc())).all()
    return {'ticket':data(t),'events':[{'id':e.id,'kind':e.kind,'message':e.message,'actor':e.actor,'created_at':e.created_at.isoformat()} for e in ev]}

@app.patch('/api/tickets/{ticket_id}',dependencies=[Depends(auth)])
def update_ticket(ticket_id:int,payload:TicketUpdate,db:Session=Depends(session)):
    t=db.get(Ticket,ticket_id)
    if not t: raise HTTPException(404,'Ticket not found')
    changes=[]
    for key,value in payload.model_dump(exclude_unset=True).items():
        if value is None: continue
        old=getattr(t,key)
        if old!=value:
            setattr(t,key,value)
            changes.append(f'{key}: {old} → {value}')
    if changes:
        t.updated_at=datetime.now(timezone.utc)
        log(db,t,'updated','; '.join(changes),'Agent')
    db.commit()
    return data(t)

@app.post('/api/tickets/{ticket_id}/notes',dependencies=[Depends(auth)],status_code=201)
def add_note(ticket_id:int,payload:NoteInput,db:Session=Depends(session)):
    t=db.get(Ticket,ticket_id)
    if not t: raise HTTPException(404,'Ticket not found')
    log(db,t,'note',payload.message,payload.actor)
    db.commit()
    return {'ok':True}

@app.get('/api/stats',dependencies=[Depends(auth)])
def stats(db:Session=Depends(session)):
    group=lambda column:dict(db.execute(select(column,func.count()).group_by(column)).all())
    return {'total':db.scalar(select(func.count(Ticket.id))) or 0,
        'by_status':group(Ticket.status),'by_priority':group(Ticket.priority),
        'by_category':group(Ticket.category),'needs_review':db.scalar(select(func.count()).select_from(Ticket).where(Ticket.review_required.is_(True))) or 0}

@app.get('/api/export.csv',dependencies=[Depends(auth)])
def export_csv(db:Session=Depends(session)):
    output=io.StringIO()
    writer=csv.writer(output)
    writer.writerow(['ID','Created','Sender','Subject','Category','Priority','Status','Team','Confidence','Review'])
    for t in db.scalars(select(Ticket).order_by(Ticket.id.desc()).limit(10000)):
        writer.writerow([t.id,t.created_at.isoformat(),t.sender,t.subject,t.category,t.priority,t.status,t.assigned_team,t.confidence,t.review_required])
    output.seek(0)
    return StreamingResponse(iter([output.getvalue()]),media_type='text/csv',headers={'Content-Disposition':'attachment; filename="flowdesk_tickets.csv"'})


@app.get('/api/analytics', dependencies=[Depends(auth)])
def analytics(days:int=Query(30,ge=7,le=365), db:Session=Depends(session)):
    """Charts reflect actual stored ticket records, not simulated measurements."""
    from collections import Counter, defaultdict
    from datetime import timedelta
    today=datetime.now(timezone.utc).date()
    start=today-timedelta(days=days-1)
    records=db.scalars(select(Ticket).order_by(Ticket.created_at.asc())).all()
    rows=[t for t in records if t.created_at.date()>=start]
    dates=[(start+timedelta(days=i)).isoformat() for i in range(days)]
    incoming=Counter(t.created_at.date().isoformat() for t in rows)
    completed=Counter(t.updated_at.date().isoformat() for t in rows if t.status in ('Resolved','Closed'))
    hours=Counter(t.created_at.hour for t in rows)
    teams=Counter(t.assigned_team for t in rows)
    statuses=Counter(t.status for t in rows)
    priorities=Counter(t.priority for t in rows)
    cats=Counter(t.category for t in rows)
    conf=[t.confidence for t in rows]
    # SLA is a demonstration proxy based on age of unresolved tickets, not an actual contractual SLA.
    now=datetime.now(timezone.utc)
    aging=[t for t in rows if t.status not in ('Resolved','Closed')]
    def age_hours(t):
        d=t.created_at.replace(tzinfo=timezone.utc) if t.created_at.tzinfo is None else t.created_at
        return (now-d).total_seconds()/3600
    thresholds={'Critical':4,'High':12,'Normal':48}
    overdue=sum(age_hours(t)>thresholds.get(t.priority,48) for t in aging)
    return {'period_days':days,'data_source':'persisted_tickets','volume':[{'date':d,'incoming':incoming[d],'completed':completed[d]} for d in dates],
       'hourly':[{'hour':h,'count':hours[h]} for h in range(24)],
       'teams':dict(teams),'statuses':dict(statuses),'priorities':dict(priorities),'categories':dict(cats),
       'total_period':len(rows),'mean_confidence':round(sum(conf)/len(conf),3) if conf else None,
       'low_confidence':sum(t.review_required for t in rows),'open_backlog':len(aging),
       'sla_proxy_overdue':overdue,'sla_proxy_threshold_hours':thresholds,
       'resolved_count':sum(t.status in ('Resolved','Closed') for t in rows),
       'note':'SLA proxy counts unresolved items older than local demonstration thresholds; resolution timestamp is not separately stored.'}
