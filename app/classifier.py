"""Transparent, offline rules baseline; upgrade to trained NLP after collecting labelled data."""
import re

RULES = {
    'Access & Login': ('password', 'login', 'log in', 'sign in', 'locked out', 'otp', 'account access', 'reset'),
    'Billing': ('invoice', 'bill', 'charged', 'refund', 'payment', 'subscription', 'transaction'),
    'Technical Support': ('error', 'crash', 'bug', 'broken', 'not working', 'exception', 'outage', 'server'),
    'Order & Delivery': ('shipment', 'delivery', 'delivered', 'order', 'tracking', 'parcel'),
}
TEAM = {'Access & Login': 'IT Helpdesk', 'Billing': 'Finance', 'Technical Support': 'Engineering',
        'Order & Delivery': 'Operations', 'General': 'Customer Support'}
URGENT = ('urgent', 'critical', 'production down', 'data breach', 'security incident', 'system down', 'p0')
HIGH = ('asap', 'cannot access', 'unable to', 'failed', 'immediately', 'blocked')

def classify(subject: str, body: str) -> dict:
    text = f'{subject} {body}'.lower()
    scores = {category: sum(bool(re.search(r'(?<!\w)' + re.escape(word) + r'(?!\w)', text)) for word in words)
              for category, words in RULES.items()}
    category = max(scores, key=scores.get) if any(scores.values()) else 'General'
    priority = 'Critical' if any(word in text for word in URGENT) else ('High' if any(word in text for word in HIGH) else 'Normal')
    confidence = round(min(0.95, 0.5 + scores.get(category, 0) * 0.15), 2) if category != 'General' else 0.25
    return {'category': category, 'priority': priority, 'assigned_team': TEAM[category], 'confidence': confidence,
            'review_required': confidence < 0.6}
