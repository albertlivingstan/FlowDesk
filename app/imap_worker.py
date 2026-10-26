"""Optional IMAP polling worker; require a dedicated mailbox/app password. Not required for demo."""
import email
import imaplib
import logging
import os
import time
from email.header import decode_header, make_header
import httpx

logging.basicConfig(level=logging.INFO,format='%(asctime)s %(levelname)s %(message)s')

def decode(value):
    try:return str(make_header(decode_header(value or '')))
    except Exception:return str(value or '')

def text_body(message):
    parts=message.walk() if message.is_multipart() else [message]
    for part in parts:
        if part.get_content_type() != 'text/plain' or part.get_content_disposition()=='attachment':continue
        data=part.get_payload(decode=True) or b''
        return data.decode(part.get_content_charset() or 'utf-8',errors='replace')[:20000]
    return '(No plain text email body)'

def poll_once():
    host=os.environ['IMAP_HOST']; username=os.environ['IMAP_USER']; password=os.environ['IMAP_PASSWORD']
    key=os.environ['API_KEY']; url=os.getenv('FLOWDESK_API_URL','http://127.0.0.1:8000').rstrip('/')
    with imaplib.IMAP4_SSL(host) as mail, httpx.Client(timeout=20) as client:
        mail.login(username,password)
        mail.select('INBOX')
        typ, result=mail.uid('search',None,'UNSEEN')
        if typ!='OK':raise RuntimeError('IMAP search failed')
        for uid in result[0].split()[:50]:
            typ,raw=mail.uid('fetch',uid,'(BODY.PEEK[])')
            if typ!='OK' or not raw or not isinstance(raw[0],tuple):continue
            msg=email.message_from_bytes(raw[0][1])
            sender=email.utils.parseaddr(msg.get('From',''))[1]
            if not sender or '@' not in sender:
                logging.warning('Skipping email UID %s with invalid sender',uid.decode());continue
            external_id=f'{username}:{uid.decode()}'
            payload={'source':'imap','external_id':external_id,'sender':sender,'subject':decode(msg.get('Subject')) or '(No subject)','body':text_body(msg)}
            try:
                response=client.post(url+'/api/tickets',json=payload,headers={'X-API-Key':key});response.raise_for_status()
                mail.uid('store',uid,'+FLAGS','(\\Seen)')
                logging.info('Processed UID %s',uid.decode())
            except Exception:
                logging.exception('Could not process UID %s; left unread for retry',uid.decode())

if __name__=='__main__':
    while True:
        try:poll_once()
        except Exception:logging.exception('IMAP poll failed')
        time.sleep(max(60,int(os.getenv('POLL_SECONDS','120'))))
