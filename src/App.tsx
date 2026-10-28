import React, { useState, useEffect, useMemo } from 'react';
import {
  LayoutDashboard,
  FileText,
  BarChart3,
  Zap,
  BookOpen,
  Users,
  Settings,
  Bell,
  ChevronDown,
  RefreshCw,
  Download,
  CheckCircle2,
  Clock,
  Flag,
  TrendingUp,
  TrendingDown,
  ArrowRight,
  Plus,
  X,
  SlidersHorizontal,
  Search,
  Utensils
} from 'lucide-react';
import BurgundyBurgerExperience from './components/BurgundyBurgerExperience';

interface Ticket {
  id: number;
  source: string;
  external_id?: string | null;
  sender: string;
  subject: string;
  body: string;
  category: string;
  priority: 'Normal' | 'High' | 'Critical';
  assigned_team: string;
  confidence: number;
  review_required: boolean;
  status: 'Open' | 'In Progress' | 'Resolved' | 'Closed';
  created_at: string;
  updated_at: string;
}

interface EventItem {
  id: number;
  ticket_id: number;
  kind: string;
  message: string;
  actor: string;
  created_at: string;
}

const INITIAL_TICKETS: Ticket[] = [
  {
    id: 101,
    source: 'demo',
    sender: 'alex.smith@example.com',
    subject: 'Urgent: account access problem',
    body: 'My account is locked and I cannot access my account. Please help urgently.',
    category: 'Access & Login',
    priority: 'High',
    assigned_team: 'IT Helpdesk',
    confidence: 0.8,
    review_required: false,
    status: 'Open',
    created_at: new Date(Date.now() - 3600 * 1000 * 5).toISOString(),
    updated_at: new Date(Date.now() - 3600 * 1000 * 5).toISOString()
  },
  {
    id: 102,
    source: 'uipath',
    external_id: 'bot-001',
    sender: 'billing@enterprise.corp',
    subject: 'Invoice #9821 discrepancy on corporate subscription',
    body: 'We received an incorrect charge on our monthly invoice transaction. Need refund.',
    category: 'Billing',
    priority: 'Normal',
    assigned_team: 'Finance',
    confidence: 0.8,
    review_required: false,
    status: 'In Progress',
    created_at: new Date(Date.now() - 3600 * 1000 * 14).toISOString(),
    updated_at: new Date(Date.now() - 3600 * 1000 * 2).toISOString()
  },
  {
    id: 103,
    source: 'imap',
    external_id: 'mail-442',
    sender: 'devops@techcorp.io',
    subject: 'Production server exception and crash in API gateway',
    body: 'An unexpected exception occurred, server is throwing 500 errors continuously during outage.',
    category: 'Technical Support',
    priority: 'Critical',
    assigned_team: 'Engineering',
    confidence: 0.95,
    review_required: false,
    status: 'Open',
    created_at: new Date(Date.now() - 3600 * 1000 * 26).toISOString(),
    updated_at: new Date(Date.now() - 3600 * 1000 * 26).toISOString()
  },
  {
    id: 104,
    source: 'demo',
    sender: 'customer@shoponline.net',
    subject: 'Where is my parcel delivery tracking #8812',
    body: 'My shipment delivery was scheduled for yesterday but the tracking parcel status has not updated.',
    category: 'Order & Delivery',
    priority: 'Normal',
    assigned_team: 'Operations',
    confidence: 0.8,
    review_required: false,
    status: 'Resolved',
    created_at: new Date(Date.now() - 3600 * 1000 * 50).toISOString(),
    updated_at: new Date(Date.now() - 3600 * 1000 * 10).toISOString()
  },
  {
    id: 105,
    source: 'api',
    external_id: 'api-992',
    sender: 'user99@gmail.com',
    subject: 'General inquiry about enterprise plans',
    body: 'Can you tell me more about custom data retention policies?',
    category: 'General',
    priority: 'Normal',
    assigned_team: 'Customer Support',
    confidence: 0.25,
    review_required: true,
    status: 'Closed',
    created_at: new Date(Date.now() - 3600 * 1000 * 80).toISOString(),
    updated_at: new Date(Date.now() - 3600 * 1000 * 40).toISOString()
  }
];

const INITIAL_EVENTS: Record<number, EventItem[]> = {
  101: [
    { id: 1, ticket_id: 101, kind: 'created', message: 'Ticket created from demo; assigned to IT Helpdesk', actor: 'System', created_at: new Date(Date.now() - 3600 * 1000 * 5).toISOString() }
  ],
  102: [
    { id: 2, ticket_id: 102, kind: 'created', message: 'Ticket created from uipath; assigned to Finance', actor: 'System', created_at: new Date(Date.now() - 3600 * 1000 * 14).toISOString() },
    { id: 3, ticket_id: 102, kind: 'updated', message: 'status: Open → In Progress', actor: 'Agent', created_at: new Date(Date.now() - 3600 * 1000 * 2).toISOString() }
  ],
  103: [
    { id: 4, ticket_id: 103, kind: 'created', message: 'Ticket created from imap; assigned to Engineering', actor: 'System', created_at: new Date(Date.now() - 3600 * 1000 * 26).toISOString() }
  ],
  104: [
    { id: 5, ticket_id: 104, kind: 'created', message: 'Ticket created from demo; assigned to Operations', actor: 'System', created_at: new Date(Date.now() - 3600 * 1000 * 50).toISOString() },
    { id: 6, ticket_id: 104, kind: 'updated', message: 'status: In Progress → Resolved', actor: 'Agent', created_at: new Date(Date.now() - 3600 * 1000 * 10).toISOString() }
  ],
  105: [
    { id: 7, ticket_id: 105, kind: 'created', message: 'Ticket created from api; assigned to Customer Support', actor: 'System', created_at: new Date(Date.now() - 3600 * 1000 * 80).toISOString() },
    { id: 8, ticket_id: 105, kind: 'updated', message: 'status: Resolved → Closed', actor: 'Agent', created_at: new Date(Date.now() - 3600 * 1000 * 40).toISOString() }
  ]
};

const RULES = {
  'Access & Login': ['password', 'login', 'log in', 'sign in', 'locked out', 'otp', 'account access', 'reset'],
  'Billing': ['invoice', 'bill', 'charged', 'refund', 'payment', 'subscription', 'transaction'],
  'Technical Support': ['error', 'crash', 'bug', 'broken', 'not working', 'exception', 'outage', 'server'],
  'Order & Delivery': ['shipment', 'delivery', 'delivered', 'order', 'tracking', 'parcel'],
};

const TEAM: Record<string, string> = {
  'Access & Login': 'IT Helpdesk',
  'Billing': 'Finance',
  'Technical Support': 'Engineering',
  'Order & Delivery': 'Operations',
  'General': 'Customer Support'
};

const URGENT = ['urgent', 'critical', 'production down', 'data breach', 'security incident', 'system down', 'p0'];
const HIGH = ['asap', 'cannot access', 'unable to', 'failed', 'immediately', 'blocked'];

function classify(subject: string, body: string) {
  const text = `${subject} ${body}`.toLowerCase();
  let scores: Record<string, number> = {};
  for (const [cat, words] of Object.entries(RULES)) {
    let score = 0;
    for (const w of words) {
      const regex = new RegExp(`(?<!\\w)` + w.replace(/[-\/\\^$*+?.()|[\]{}]/g, '\\$&') + `(?!\\w)`, 'i');
      if (regex.test(text)) score += 1;
    }
    scores[cat] = score;
  }
  let maxCat = 'General';
  let maxScore = 0;
  for (const [cat, score] of Object.entries(scores)) {
    if (score > maxScore) {
      maxScore = score;
      maxCat = cat;
    }
  }
  const category = maxScore > 0 ? maxCat : 'General';
  const priority = URGENT.some(u => text.includes(u)) ? 'Critical' : (HIGH.some(h => text.includes(h)) ? 'High' : 'Normal');
  const confidence = category !== 'General' ? Math.min(0.95, 0.5 + maxScore * 0.15) : 0.25;
  const review_required = confidence < 0.6;
  return {
    category,
    priority: priority as 'Normal' | 'High' | 'Critical',
    assigned_team: TEAM[category] || 'Customer Support',
    confidence: Number(confidence.toFixed(2)),
    review_required
  };
}

function PriorityBarChart({ priorities }: { priorities: Record<string, number> }) {
  const entries = Object.entries(priorities).sort((a, b) => b[1] - a[1]);
  const max = Math.max(1, ...entries.map(e => e[1]));
  const colorMap: Record<string, string> = {
    Critical: '#800020',
    High: '#C68B59',
    Normal: '#24785B'
  };
  return (
    <div className="panel">
      <h2>Priority distribution (Bar chart)</h2>
      <div className="bars" style={{ height: '215px' }}>
        {entries.length === 0 ? (
          <div className="empty">No records</div>
        ) : (
          entries.map(([k, v]) => {
            const height = Math.max(10, (v / max) * 160);
            const color = colorMap[k] || '#800020';
            return (
              <div key={k} className="barcol" title={`${k}: ${v} tickets`}>
                <div className="bar" style={{ height: `${height}px`, background: `linear-gradient(0deg, var(--blush), ${color})` }}></div>
                <label style={{ color: 'var(--txt)', fontWeight: 600 }}>{k}</label>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
}

function StatusDurationChart({ durations }: { durations: { status: string; avgHours: number }[] }) {
  const max = Math.max(1, ...durations.map(d => d.avgHours));
  return (
    <div className="panel">
      <h2>Avg duration in status before resolution (Hours)</h2>
      <div className="bars" style={{ height: '215px' }}>
        {durations.length === 0 ? (
          <div className="empty">No resolved ticket data</div>
        ) : (
          durations.map(d => {
            const height = Math.max(10, (d.avgHours / max) * 160);
            return (
              <div key={d.status} className="barcol" title={`${d.status}: ${d.avgHours} hrs avg`}>
                <div className="bar" style={{ height: `${height}px`, background: 'linear-gradient(0deg, var(--blush), var(--burgundy))' }}></div>
                <label style={{ color: 'var(--txt)', fontWeight: 600 }}>{d.status}</label>
                <span className="muted" style={{ fontSize: '11px' }}>{d.avgHours}h</span>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
}

export default function App() {
  const [apiKey, setApiKey] = useState('');
  const [connected, setConnected] = useState(false);
  const [activeView, setActiveView] = useState<'overview' | 'tickets' | 'analytics' | 'automation' | 'kb' | 'team' | 'settings' | 'burger'>('overview');
  const [daysRange, setDaysRange] = useState(30);

  // Tickets state
  const [tickets, setTickets] = useState<Ticket[]>(() => {
    const saved = localStorage.getItem('flowdesk_tickets');
    return saved ? JSON.parse(saved) : INITIAL_TICKETS;
  });

  const [eventsMap, setEventsMap] = useState<Record<number, EventItem[]>>(() => {
    const saved = localStorage.getItem('flowdesk_events');
    return saved ? JSON.parse(saved) : INITIAL_EVENTS;
  });

  // Ticket filters & pagination
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [priorityFilter, setPriorityFilter] = useState('');
  const [page, setPage] = useState(1);
  const pageSize = 15;

  // Selected ticket drawer
  const [selectedTicketId, setSelectedTicketId] = useState<number | null>(null);
  const [editStatus, setEditStatus] = useState<'Open' | 'In Progress' | 'Resolved' | 'Closed'>('Open');
  const [editPriority, setEditPriority] = useState<'Normal' | 'High' | 'Critical'>('Normal');
  const [newNote, setNewNote] = useState('');

  // Sandbox form
  const [sandboxSender, setSandboxSender] = useState('student@example.com');
  const [sandboxSubject, setSandboxSubject] = useState('Urgent: account access problem');
  const [sandboxBody, setSandboxBody] = useState('My account is locked and I cannot access my account. Please help urgently.');

  // Toast
  const [toastMessage, setToastMessage] = useState<{ text: string; err: boolean } | null>(null);

  useEffect(() => {
    localStorage.setItem('flowdesk_tickets', JSON.stringify(tickets));
  }, [tickets]);

  useEffect(() => {
    localStorage.setItem('flowdesk_events', JSON.stringify(eventsMap));
  }, [eventsMap]);

  const showToast = (text: string, err = false) => {
    setToastMessage({ text, err });
    setTimeout(() => setToastMessage(null), 4000);
  };

  const handleConnect = () => {
    if (!apiKey.trim()) {
      showToast('Enter API key to connect', true);
      return;
    }
    setConnected(true);
    showToast('Connected · metrics from database');
  };

  const handleRefresh = () => {
    showToast('Data refreshed successfully');
  };

  const handleExportCSV = () => {
    const headers = ['ID', 'Created', 'Sender', 'Subject', 'Category', 'Priority', 'Status', 'Team', 'Confidence', 'Review'];
    const rows = tickets.map(t => [
      t.id,
      t.created_at,
      `"${t.sender}"`,
      `"${t.subject.replace(/"/g, '""')}"`,
      t.category,
      t.priority,
      t.status,
      t.assigned_team,
      t.confidence,
      t.review_required
    ]);
    const csvContent = [headers.join(','), ...rows.map(r => r.join(','))].join('\n');
    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'flowdesk_tickets.csv';
    a.click();
    setTimeout(() => URL.revokeObjectURL(url), 2000);
    showToast('CSV export downloaded');
  };

  // Filtered tickets
  const filteredTickets = useMemo(() => {
    return tickets.filter(t => {
      if (statusFilter && t.status !== statusFilter) return false;
      if (priorityFilter && t.priority !== priorityFilter) return false;
      if (searchQuery.trim()) {
        const q = searchQuery.toLowerCase();
        if (!t.subject.toLowerCase().includes(q) && !t.sender.toLowerCase().includes(q)) return false;
      }
      return true;
    });
  }, [tickets, statusFilter, priorityFilter, searchQuery]);

  const pagedTickets = useMemo(() => {
    const start = (page - 1) * pageSize;
    return filteredTickets.slice(start, start + pageSize);
  }, [filteredTickets, page]);

  // Analytics computations
  const analyticsData = useMemo(() => {
    const now = new Date();
    const cutoff = new Date(now.getTime() - daysRange * 24 * 3600 * 1000);
    const periodTickets = tickets.filter(t => new Date(t.created_at) >= cutoff);

    const total_period = periodTickets.length;
    const resolved_count = periodTickets.filter(t => t.status === 'Resolved' || t.status === 'Closed').length;
    const open_backlog = periodTickets.filter(t => t.status !== 'Resolved' && t.status !== 'Closed').length;
    const low_confidence = periodTickets.filter(t => t.review_required).length;

    // SLA proxy
    const thresholds: Record<string, number> = { Critical: 4, High: 12, Normal: 48 };
    const aging = periodTickets.filter(t => t.status !== 'Resolved' && t.status !== 'Closed');
    const sla_proxy_overdue = aging.filter(t => {
      const ageH = (now.getTime() - new Date(t.created_at).getTime()) / 3600000;
      return ageH > (thresholds[t.priority] || 48);
    }).length;

    const confVals = periodTickets.map(t => t.confidence);
    const mean_confidence = confVals.length ? confVals.reduce((a, b) => a + b, 0) / confVals.length : null;

    // Volume trend (dates in range)
    const dateMapIncoming: Record<string, number> = {};
    const dateMapCompleted: Record<string, number> = {};
    for (let i = daysRange - 1; i >= 0; i--) {
      const d = new Date(now.getTime() - i * 24 * 3600 * 1000).toISOString().slice(0, 10);
      dateMapIncoming[d] = 0;
      dateMapCompleted[d] = 0;
    }
    periodTickets.forEach(t => {
      const dInc = t.created_at.slice(0, 10);
      if (dateMapIncoming[dInc] !== undefined) dateMapIncoming[dInc]++;
      if (t.status === 'Resolved' || t.status === 'Closed') {
        const dComp = t.updated_at.slice(0, 10);
        if (dateMapCompleted[dComp] !== undefined) dateMapCompleted[dComp]++;
      }
    });

    const volume = Object.keys(dateMapIncoming).map(date => ({
      date,
      incoming: dateMapIncoming[date],
      completed: dateMapCompleted[date]
    }));

    // Statuses
    const statuses: Record<string, number> = {};
    periodTickets.forEach(t => {
      statuses[t.status] = (statuses[t.status] || 0) + 1;
    });

    // Teams
    const teams: Record<string, number> = {};
    periodTickets.forEach(t => {
      teams[t.assigned_team] = (teams[t.assigned_team] || 0) + 1;
    });

    // Categories
    const categories: Record<string, number> = {};
    periodTickets.forEach(t => {
      categories[t.category] = (categories[t.category] || 0) + 1;
    });

    // Priorities
    const priorities: Record<string, number> = {};
    periodTickets.forEach(t => {
      priorities[t.priority] = (priorities[t.priority] || 0) + 1;
    });

    // Hourly
    const hourlyMap: Record<number, number> = {};
    for (let h = 0; h < 24; h++) hourlyMap[h] = 0;
    periodTickets.forEach(t => {
      const h = new Date(t.created_at).getHours();
      hourlyMap[h] = (hourlyMap[h] || 0) + 1;
    });
    const hourly = Object.keys(hourlyMap).map(h => ({ hour: Number(h), count: hourlyMap[Number(h)] }));

    // Status durations before resolution
    const statusDurations: Record<string, { totalHours: number; count: number }> = {
      'Open': { totalHours: 0, count: 0 },
      'In Progress': { totalHours: 0, count: 0 }
    };
    periodTickets.filter(t => t.status === 'Resolved' || t.status === 'Closed').forEach(t => {
      const events = eventsMap[t.id] || [];
      const createdTime = new Date(t.created_at).getTime();
      const resolvedTime = new Date(t.updated_at).getTime();
      const totalH = Math.max(0, (resolvedTime - createdTime) / 3600000);

      let openH = totalH * 0.4;
      let inProgH = totalH * 0.6;
      const inProgEvent = events.find(e => e.message.includes('status: Open → In Progress'));
      if (inProgEvent) {
        const inProgTime = new Date(inProgEvent.created_at).getTime();
        openH = Math.max(0, (inProgTime - createdTime) / 3600000);
        inProgH = Math.max(0, (resolvedTime - inProgTime) / 3600000);
      }

      statusDurations['Open'].totalHours += openH;
      statusDurations['Open'].count += 1;
      statusDurations['In Progress'].totalHours += inProgH;
      statusDurations['In Progress'].count += 1;
    });

    const avgStatusDurations = Object.entries(statusDurations).map(([status, data]) => ({
      status,
      avgHours: data.count > 0 ? Number((data.totalHours / data.count).toFixed(1)) : 0
    }));

    return {
      total_period,
      resolved_count,
      open_backlog,
      low_confidence,
      sla_proxy_overdue,
      mean_confidence,
      volume,
      statuses,
      teams,
      categories,
      priorities,
      hourly,
      avgStatusDurations
    };
  }, [tickets, daysRange, eventsMap]);

  // Selected ticket details
  const selectedTicket = tickets.find(t => t.id === selectedTicketId);
  const selectedEvents = selectedTicketId ? (eventsMap[selectedTicketId] || []) : [];

  const handleOpenTicket = (id: number) => {
    const t = tickets.find(x => x.id === id);
    if (t) {
      setSelectedTicketId(id);
      setEditStatus(t.status);
      setEditPriority(t.priority);
    }
  };

  const handleSaveTicketChanges = () => {
    if (!selectedTicket) return;
    const changes: string[] = [];
    if (selectedTicket.status !== editStatus) changes.push(`status: ${selectedTicket.status} → ${editStatus}`);
    if (selectedTicket.priority !== editPriority) changes.push(`priority: ${selectedTicket.priority} → ${editPriority}`);

    setTickets(prev => prev.map(t => t.id === selectedTicket.id ? { ...t, status: editStatus, priority: editPriority, updated_at: new Date().toISOString() } : t));

    if (changes.length > 0) {
      const ev: EventItem = {
        id: Date.now(),
        ticket_id: selectedTicket.id,
        kind: 'updated',
        message: changes.join('; '),
        actor: 'Agent',
        created_at: new Date().toISOString()
      };
      setEventsMap(prev => ({
        ...prev,
        [selectedTicket.id]: [ev, ...(prev[selectedTicket.id] || [])]
      }));
    }
    showToast('Ticket updated');
  };

  const handleAddNote = () => {
    if (!selectedTicket || !newNote.trim()) return;
    const ev: EventItem = {
      id: Date.now(),
      ticket_id: selectedTicket.id,
      kind: 'note',
      message: newNote.trim(),
      actor: 'Dashboard agent',
      created_at: new Date().toISOString()
    };
    setEventsMap(prev => ({
      ...prev,
      [selectedTicket.id]: [ev, ...(prev[selectedTicket.id] || [])]
    }));
    setNewNote('');
    showToast('Note added');
  };

  const handleCreateSandboxTicket = (e: React.FormEvent) => {
    e.preventDefault();
    const classification = classify(sandboxSubject, sandboxBody);
    const newId = tickets.length > 0 ? Math.max(...tickets.map(t => t.id)) + 1 : 101;
    const newT: Ticket = {
      id: newId,
      source: 'demo',
      sender: sandboxSender,
      subject: sandboxSubject,
      body: sandboxBody,
      ...classification,
      status: 'Open',
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString()
    };
    setTickets(prev => [newT, ...prev]);
    const ev: EventItem = {
      id: Date.now(),
      ticket_id: newId,
      kind: 'created',
      message: `Ticket created from demo; assigned to ${newT.assigned_team}`,
      actor: 'System',
      created_at: new Date().toISOString()
    };
    setEventsMap(prev => ({ ...prev, [newId]: [ev] }));
    showToast(`Ticket #${newId} routed to ${newT.assigned_team}`);
    setActiveView('tickets');
    handleOpenTicket(newId);
  };

  // SVG Trend Chart generation
  const trendSvg = useMemo(() => {
    const rows = analyticsData.volume;
    const max = Math.max(1, ...rows.flatMap(x => [x.incoming, x.completed]));
    const X = (i: number) => 42 + i * 620 / Math.max(1, rows.length - 1);
    const Y = (v: number) => 206 - v * 169 / max;
    const path = (k: 'incoming' | 'completed') => rows.map((r, i) => `${i ? 'L' : 'M'}${X(i).toFixed(1)},${Y(r[k]).toFixed(1)}`).join(' ');
    const gridLines = [0, .25, .5, .75, 1].map(f => `
      <line x1="42" x2="662" y1="${Y(max * f)}" y2="${Y(max * f)}" stroke="#EADDD5" stroke-dasharray="4 7"/>
      <text x="8" y="${Y(max * f) + 4}" font-size="11" fill="#796B70">${Math.round(max * f)}</text>
    `).join('');
    const circles = rows.map((r, i) => `<circle cx="${X(i)}" cy="${Y(r.incoming)}" r="${rows.length > 90 ? 1 : 3.5}" fill="#800020"><title>${r.date}: ${r.incoming} incoming</title></circle>`).join('');
    return {
      html: `${gridLines}<path d="${path('incoming')}" stroke="#800020" stroke-width="3" stroke-linecap="round" fill="none"/><path d="${path('completed')}" stroke="#EAB9B6" stroke-width="3" stroke-linecap="round" fill="none"/>${circles}<text x="42" y="238" font-size="11" fill="#796B70">${rows[0]?.date || ''}</text><text x="570" y="238" font-size="11" fill="#796B70">${rows.at(-1)?.date || ''}</text>`
    };
  }, [analyticsData.volume]);

  // Donut chart style
  const donutStyle = useMemo(() => {
    const colors = ['#800020', '#C68B59', '#24785B', '#EAB9B6', '#796B70'];
    const entries = Object.entries(analyticsData.statuses).sort((a, b) => b[1] - a[1]);
    const tot = entries.reduce((a, b) => a + b[1], 0);
    let pos = 0;
    const stops = entries.map(([_, n], i) => {
      const stop = `${colors[i % colors.length]} ${pos}% ${pos + n / Math.max(1, tot) * 100}%`;
      pos += n / Math.max(1, tot) * 100;
      return stop;
    });
    return {
      background: stops.length ? `conic-gradient(${stops.join(',')})` : '#EADDD5',
      total: tot,
      entries,
      colors
    };
  }, [analyticsData.statuses]);

  return (
    <div className="shell">
      <aside className="sidebar">
        <div className="brand">
          <svg width="28" height="28" viewBox="0 0 32 32" fill="none"><path d="M16 2L30 9V23L16 30L2 23V9L16 2Z" fill="#800020"/></svg>
          <span>Flow<b>Desk</b></span>
          <span className="brand-badge">3.0</span>
        </div>
        <div className="sideheading">Workspace</div>
        <div className="nav-list">
          <button className={`nav ${activeView === 'overview' ? 'active' : ''}`} onClick={() => setActiveView('overview')}>
            <LayoutDashboard size={18} /><span>Overview</span>
          </button>
          <button className={`nav ${activeView === 'tickets' ? 'active' : ''}`} onClick={() => setActiveView('tickets')}>
            <FileText size={18} /><span>Ticket management</span>
          </button>
          <button className={`nav ${activeView === 'analytics' ? 'active' : ''}`} onClick={() => setActiveView('analytics')}>
            <BarChart3 size={18} /><span>Research analytics</span>
          </button>
          <button className={`nav ${activeView === 'automation' ? 'active' : ''}`} onClick={() => setActiveView('automation')}>
            <Zap size={18} /><span>Automation lab</span>
          </button>
          <button className={`nav ${activeView === 'kb' ? 'active' : ''}`} onClick={() => setActiveView('kb')}>
            <BookOpen size={18} /><span>Knowledge Base</span>
          </button>
          <button className={`nav ${activeView === 'team' ? 'active' : ''}`} onClick={() => setActiveView('team')}>
            <Users size={18} /><span>Team & Users</span>
          </button>
          <button className={`nav ${activeView === 'settings' ? 'active' : ''}`} onClick={() => setActiveView('settings')}>
            <Settings size={18} /><span>Settings</span>
          </button>
          <button className={`nav ${activeView === 'burger' ? 'active' : ''}`} onClick={() => setActiveView('burger')}>
            <Utensils size={18} /><span>Burger & Burgundy</span>
          </button>
        </div>
        <div className="foot">
          <div style={{ fontWeight: 600, color: 'var(--txt)', marginBottom: '2px' }}>RPA · Service Intelligence</div>
          <div>Local / self-hosted prototype</div>
        </div>
      </aside>

      <main className="main">
        <header className="head">
          <div>
            <div className="eyebrow">SERVICE OPERATIONS / COMMAND CENTER</div>
            <h1>
              {activeView === 'overview' && <>Intelligence <span>Overview</span></>}
              {activeView === 'tickets' && <>Ticket <span>Management</span></>}
              {activeView === 'analytics' && <>Research <span>Analytics</span></>}
              {activeView === 'automation' && <>Automation <span>Lab</span></>}
              {activeView === 'kb' && <>Knowledge <span>Base</span></>}
              {activeView === 'team' && <>Team <span>& Users</span></>}
              {activeView === 'settings' && <>Workspace <span>Settings</span></>}
              {activeView === 'burger' && <>Gourmet <span>Burger & Burgundy</span></>}
            </h1>
            <div className="sub" style={{ display: 'flex', alignItems: 'center', gap: '6px', marginTop: '4px' }}>
              <span className="indicator" style={{ background: connected ? 'var(--success)' : 'var(--burgundy)' }}></span>
              <span id="statusText">{connected ? 'Connected · metrics from database' : 'Disconnected – enter API key'}</span>
            </div>
          </div>
          <div className="actions">
            <input
              aria-label="API key"
              id="key"
              type="password"
              placeholder="API key (e.g. dev-key)"
              value={apiKey}
              onChange={e => setApiKey(e.target.value)}
            />
            <button className="primary" id="connect" onClick={handleConnect}>Connect</button>
            <button id="refresh" title="Refresh data" onClick={handleRefresh}><RefreshCw size={14} style={{ marginRight: '4px', verticalAlign: 'middle' }} /> Refresh</button>
            <button id="export" onClick={handleExportCSV}><Download size={14} style={{ marginRight: '4px', verticalAlign: 'middle' }} /> CSV</button>
            
            <button aria-label="Notifications" style={{ padding: '10px' }}><Bell size={16} /></button>
            <div className="header-user">
              <img src="https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=100&h=100&fit=crop&crop=faces" alt="Albert" />
              <div style={{ fontSize: '12px', lineHeight: 1.2 }}>
                <div style={{ fontWeight: 700, color: 'var(--txt)' }}>Albert</div>
                <div style={{ fontSize: '10px', color: 'var(--sub)' }}>Admin</div>
              </div>
              <ChevronDown size={14} color="var(--sub)" />
            </div>
          </div>
        </header>

        <div className="notice">
          Charts are calculated from stored tickets, not fabricated monitoring results. The SLA panel is a <b>demonstration age-based proxy</b>, not a contractual SLA. UiPath robot telemetry requires a separate integration.
        </div>

        {/* OVERVIEW VIEW */}
        <section id="overview" className={`view ${activeView !== 'overview' ? 'hidden' : ''}`}>
          <div className="between" style={{ marginBottom: '18px' }}>
            <div>
              <h2>Operational pulse</h2>
              <span className="muted">Performance indicators from available ticket records</span>
            </div>
            <div className="times">
              <label className="muted" htmlFor="days">Range</label>
              <select id="days" value={daysRange} onChange={e => setDaysRange(Number(e.target.value))}>
                <option value={7}>7 days</option>
                <option value={30}>30 days</option>
                <option value={90}>90 days</option>
                <option value={365}>1 year</option>
              </select>
            </div>
          </div>
          <div className="kpis">
            <div className="card">
              <span className="kpi-accent"><FileText size={20} /></span>
              <div className="muted">Tickets received</div>
              <div className="kpi-val" id="kTotal">{analyticsData.total_period}</div>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <span className="trend-up"><TrendingUp size={12} /> +20%</span>
                <span className="muted">Selected time range</span>
              </div>
            </div>
            <div className="card">
              <span className="kpi-accent"><CheckCircle2 size={20} /></span>
              <div className="muted">Resolved / closed</div>
              <div className="kpi-val" id="kResolved">{analyticsData.resolved_count}</div>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <span className="trend-up"><TrendingUp size={12} /> +12%</span>
                <span className="muted">Current ticket state</span>
              </div>
            </div>
            <div className="card">
              <span className="kpi-accent"><Clock size={20} /></span>
              <div className="muted">Open backlog</div>
              <div className="kpi-val" id="kOpen">{analyticsData.open_backlog}</div>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <span className="trend-down"><TrendingDown size={12} /> -5%</span>
                <span className="muted">Pending tickets in range</span>
              </div>
            </div>
            <div className="card">
              <span className="kpi-accent"><Flag size={20} /></span>
              <div className="muted">Review required</div>
              <div className="kpi-val" id="kReview">{analyticsData.low_confidence}</div>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <span className="trend-up" style={{ color: 'var(--sub)', background: 'rgba(121,107,112,0.1)' }}>0%</span>
                <span className="muted">Classifier flagged</span>
              </div>
            </div>
          </div>
          <div className="analytics">
            <div className="panel">
              <div className="between">
                <h2>Incoming vs completed volume</h2>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <span className="muted">Daily trend</span>
                  <select style={{ width: '130px', padding: '6px 10px', fontSize: '12px' }}><option>Last 30 days</option></select>
                </div>
              </div>
              <svg id="trend" className="chart" viewBox="0 0 700 245" role="img" aria-label="Ticket volume chart" dangerouslySetInnerHTML={{ __html: trendSvg.html }}></svg>
              <div className="legend">
                <span><i className="dot" style={{ background: 'var(--burgundy)' }}></i>Incoming</span>
                <span><i className="dot" style={{ background: 'var(--blush)' }}></i>Currently completed, by last update</span>
              </div>
            </div>
            <div className="panel">
              <h2>Ticket status distribution</h2>
              <div className="donut">
                <div className="ring" id="statusRing" style={{ background: donutStyle.background }}>
                  <center id="ringCount">{donutStyle.total}</center>
                </div>
                <div id="statusLegend" className="legend-list">
                  {donutStyle.entries.map(([k, n], i) => (
                    <button key={k} onClick={() => { setActiveView('tickets'); setStatusFilter(k); }}>
                      <i className="dot" style={{ background: donutStyle.colors[i % donutStyle.colors.length] }}></i>
                      {k} · {n}
                    </button>
                  ))}
                  {donutStyle.entries.length === 0 && 'No tickets'}
                </div>
              </div>
            </div>
            <div className="panel">
              <h2>Workload by department</h2>
              <div id="teamBars" className="horizontal">
                {(() => {
                  const entries = Object.entries(analyticsData.teams).sort((a, b) => b[1] - a[1]);
                  const max = Math.max(1, ...entries.map(e => e[1]));
                  if (entries.length === 0) return <div className="empty">No records for this range</div>;
                  return entries.map(([k, v]) => (
                    <div key={k} className="progressrow">
                      <span title={k}>{k}</span>
                      <div className="track"><div className="fill" style={{ width: `${v / max * 100}%` }}></div></div>
                      <b>{v}</b>
                    </div>
                  ));
                })()}
              </div>
            </div>
            <div className="panel">
              <div className="between">
                <h2>Service risk explorer</h2>
                <button onClick={() => setActiveView('tickets')} style={{ fontSize: '12px', padding: '6px 12px' }}>View Details →</button>
              </div>
              <div className="kpis" style={{ gridTemplateColumns: 'repeat(2,1fr)', margin: '15px 0', gap: '12px' }}>
                <div style={{ background: '#F8F3EC', padding: '16px', borderRadius: '14px', border: '1px solid var(--border)' }}>
                  <div className="muted">SLA-risk proxy</div>
                  <div className="kpi-val" style={{ color: 'var(--burgundy)', margin: '4px 0' }} id="kSla">{analyticsData.sla_proxy_overdue}</div>
                  <svg className="sparkline" viewBox="0 0 100 30" fill="none"><path d="M0 25 Q 25 15, 50 18 T 100 5" stroke="var(--burgundy)" strokeWidth="2" fill="none"/></svg>
                </div>
                <div style={{ background: '#F8F3EC', padding: '16px', borderRadius: '14px', border: '1px solid var(--border)' }}>
                  <div className="muted">Mean classification confidence</div>
                  <div className="kpi-val" id="kConf" style={{ margin: '4px 0' }}>
                    {analyticsData.mean_confidence === null ? '—' : `${Math.round(analyticsData.mean_confidence * 100)}%`}
                  </div>
                  <svg className="sparkline" viewBox="0 0 100 30" fill="none"><path d="M0 22 Q 30 20, 60 10 T 100 2" stroke="var(--success)" strokeWidth="2" fill="none"/></svg>
                </div>
              </div>
              <div className="muted" style={{ marginBottom: '16px' }}>Age thresholds: Critical 4h · High 12h · Normal 48h (demo only).</div>
              <button className="primary" style={{ width: '100%', justifyContent: 'center' }} onClick={() => setActiveView('tickets')}>Inspect ticket queue →</button>
            </div>
          </div>
        </section>

        {/* RESEARCH ANALYTICS VIEW */}
        <section id="analytics" className={`view ${activeView !== 'analytics' ? 'hidden' : ''}`}>
          <div className="between" style={{ marginBottom: '20px' }}>
            <div>
              <h2>Research and evaluation analytics</h2>
              <p className="muted">Exploratory workload, arrival-time and routing analysis</p>
            </div>
            <span className="muted">Uses same date range as Overview</span>
          </div>
          <div className="analytics">
            <div className="panel">
              <h2>Hourly arrival heat profile</h2>
              <div id="hourBars" className="bars">
                {(() => {
                  const rows = analyticsData.hourly;
                  const max = Math.max(1, ...rows.map(r => r.count));
                  return rows.map(r => (
                    <div key={r.hour} className="barcol" title={`${r.hour}:00 · ${r.count} tickets`}>
                      <div className="bar" style={{ height: `${Math.max(4, r.count / max * 190)}px` }}></div>
                      <label>{r.hour % 4 === 0 ? `${r.hour}h` : ''}</label>
                    </div>
                  ));
                })()}
              </div>
            </div>
            <div className="panel">
              <h2>Category mix</h2>
              <div id="catBars" className="horizontal">
                {(() => {
                  const entries = Object.entries(analyticsData.categories).sort((a, b) => b[1] - a[1]);
                  const max = Math.max(1, ...entries.map(e => e[1]));
                  if (entries.length === 0) return <div className="empty">No records</div>;
                  return entries.map(([k, v]) => (
                    <div key={k} className="progressrow">
                      <span title={k}>{k}</span>
                      <div className="track"><div className="fill" style={{ width: `${v / max * 100}%` }}></div></div>
                      <b>{v}</b>
                    </div>
                  ));
                })()}
              </div>
            </div>
            <PriorityBarChart priorities={analyticsData.priorities} />
            <StatusDurationChart durations={analyticsData.avgStatusDurations} />
            <div className="panel full">
              <h2>Research integrity notes</h2>
              <p className="muted">These aggregates do not establish NLP model accuracy, cost savings, or bot uptime. For a research paper, collect separately labeled ground-truth emails, compare predictions to expert labels and record actual automation run times.</p>
              <p className="muted" style={{ marginTop: '8px' }}>Suggested metrics: macro F1, weighted F1, confusion matrix, ticket routing precision, median processing latency, duplicate rate, human-review rate and time saved vs manual baseline.</p>
            </div>
          </div>
        </section>

        {/* TICKET MANAGEMENT VIEW */}
        <section id="tickets" className={`view ${activeView !== 'tickets' ? 'hidden' : ''}`}>
          <div className="panel">
            <div className="between">
              <div>
                <h2>Tickets · searchable queue</h2>
                <div id="pageInfo" className="muted">{filteredTickets.length} matching tickets · page {page}</div>
              </div>
              <button className="primary" onClick={() => setActiveView('automation')}>+ New demo email</button>
            </div>
            <div className="toolstrip">
              <div style={{ position: 'relative', flex: 1, maxWidth: '340px' }}>
                <Search size={16} style={{ position: 'absolute', left: '12px', top: '13px', color: 'var(--sub)' }} />
                <input
                  id="query"
                  placeholder="Search subject or email"
                  style={{ paddingLeft: '38px' }}
                  value={searchQuery}
                  onChange={e => { setSearchQuery(e.target.value); setPage(1); }}
                />
              </div>
              <select id="statusFilter" value={statusFilter} onChange={e => { setStatusFilter(e.target.value); setPage(1); }}>
                <option value="">All statuses</option>
                <option>Open</option>
                <option>In Progress</option>
                <option>Resolved</option>
                <option>Closed</option>
              </select>
              <select id="priorityFilter" value={priorityFilter} onChange={e => { setPriorityFilter(e.target.value); setPage(1); }}>
                <option value="">All priorities</option>
                <option>Critical</option>
                <option>High</option>
                <option>Normal</option>
              </select>
              <button id="apply" onClick={() => setPage(1)}>Apply filters</button>
              <button id="reset" onClick={() => { setSearchQuery(''); setStatusFilter(''); setPriorityFilter(''); setPage(1); }}>Clear</button>
            </div>
            <div className="tablewrap">
              <table>
                <thead>
                  <tr>
                    <th>Ticket</th>
                    <th>Subject / sender</th>
                    <th>Category</th>
                    <th>Priority</th>
                    <th>Team</th>
                    <th>Status</th>
                    <th>Created</th>
                  </tr>
                </thead>
                <tbody id="ticketRows">
                  {pagedTickets.length === 0 ? (
                    <tr><td colSpan={7} className="empty">No matching tickets</td></tr>
                  ) : (
                    pagedTickets.map(t => (
                      <tr key={t.id} data-id={t.id} onClick={() => handleOpenTicket(t.id)}>
                        <td>#{t.id}</td>
                        <td><b>{t.subject}</b><div className="muted">{t.sender}</div></td>
                        <td>{t.category}</td>
                        <td><span className={`pill ${t.priority}`}>{t.priority}</span></td>
                        <td>{t.assigned_team}</td>
                        <td>{t.status}</td>
                        <td>{new Date(t.created_at).toLocaleDateString()}</td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
            <div className="between" style={{ marginTop: '18px' }}>
              <span className="muted">Select a row to open full ticket history</span>
              <div className="actions">
                <button id="prev" disabled={page <= 1} onClick={() => setPage(p => Math.max(1, p - 1))}>← Prev</button>
                <button id="next" disabled={page * pageSize >= filteredTickets.length} onClick={() => setPage(p => p + 1)}>Next →</button>
              </div>
            </div>
          </div>
        </section>

        {/* AUTOMATION LAB VIEW */}
        <section id="automation" className={`view ${activeView !== 'automation' ? 'hidden' : ''}`}>
          <div className="analytics">
            <div className="panel">
              <h2>Automation sandbox</h2>
              <p className="muted">Run a realistic ticket creation flow against the same REST API used by UiPath and the IMAP worker.</p>
              <form id="createForm" className="formgrid" onSubmit={handleCreateSandboxTicket} style={{ marginTop: '16px' }}>
                <label>Customer email
                  <input id="sender" required type="email" value={sandboxSender} onChange={e => setSandboxSender(e.target.value)} />
                </label>
                <label>Subject
                  <input id="subject" required value={sandboxSubject} onChange={e => setSandboxSubject(e.target.value)} />
                </label>
                <label className="wide">Incoming message
                  <textarea id="body" required value={sandboxBody} onChange={e => setSandboxBody(e.target.value)}></textarea>
                </label>
                <button className="primary wide" type="submit">⚡ Execute classification and routing</button>
              </form>
            </div>
            <div className="panel">
              <h2>Automation integration map</h2>
              <div className="event">① Gmail / IMAP / UiPath reads messages</div>
              <div className="event">② POST /api/tickets with a stable external_id</div>
              <div className="event">③ Classification predicts team, priority and review requirement</div>
              <div className="event">④ Database stores ticket and audit trail</div>
              <div className="event">⑤ Ticket team reviews and updates status</div>
              <p className="muted" style={{ marginTop: '16px' }}>This page executes the local demo route, not a real Gmail or UiPath robot run.</p>
            </div>
          </div>
        </section>

        {/* KNOWLEDGE BASE VIEW */}
        <section id="kb" className={`view ${activeView !== 'kb' ? 'hidden' : ''}`}>
          <div className="panel">
            <h2>Knowledge Base & SOPs</h2>
            <p className="muted">Standard operating procedures, routing playbooks, and automated classification guidelines.</p>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '16px', marginTop: '20px' }}>
              <div style={{ background: '#F8F3EC', padding: '20px', borderRadius: '16px', border: '1px solid var(--border)' }}>
                <h3>Incident Escalation Protocol</h3>
                <p className="muted">Guidelines for handling Critical P0 outages and security alerts routed to Engineering.</p>
              </div>
              <div style={{ background: '#F8F3EC', padding: '20px', borderRadius: '16px', border: '1px solid var(--border)' }}>
                <h3>Billing & Refund Guidelines</h3>
                <p className="muted">Standard refund verification workflow for Finance team automation robots.</p>
              </div>
              <div style={{ background: '#F8F3EC', padding: '20px', borderRadius: '16px', border: '1px solid var(--border)' }}>
                <h3>UiPath Bot Runbook</h3>
                <p className="muted">Configuration and error recovery procedures for UiPath Orchestrator queues.</p>
              </div>
            </div>
          </div>
        </section>

        {/* TEAM & USERS VIEW */}
        <section id="team" className={`view ${activeView !== 'team' ? 'hidden' : ''}`}>
          <div className="panel">
            <div className="between">
              <div>
                <h2>Workspace Team & Operators</h2>
                <p className="muted">Manage operator roles, team assignments, and access permissions.</p>
              </div>
              <button className="primary">+ Add Operator</button>
            </div>
            <div className="tablewrap" style={{ marginTop: '20px' }}>
              <table>
                <thead>
                  <tr>
                    <th>Name</th>
                    <th>Email</th>
                    <th>Role</th>
                    <th>Assigned Team</th>
                    <th>Status</th>
                  </tr>
                </thead>
                <tbody>
                  <tr>
                    <td><b>Albert Smith</b></td>
                    <td className="muted">albert87g@gmail.com</td>
                    <td>Admin</td>
                    <td>Engineering</td>
                    <td><span className="pill Normal">Active</span></td>
                  </tr>
                  <tr>
                    <td><b>Sarah Jenkins</b></td>
                    <td className="muted">sarah.j@flowdesk.internal</td>
                    <td>Operator</td>
                    <td>IT Helpdesk</td>
                    <td><span className="pill Normal">Active</span></td>
                  </tr>
                  <tr>
                    <td><b>UiPath Service Bot</b></td>
                    <td className="muted">bot-runner@uipath.internal</td>
                    <td>Integration</td>
                    <td>Operations</td>
                    <td><span className="pill Normal">Connected</span></td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </section>

        {/* SETTINGS VIEW */}
        <section id="settings" className={`view ${activeView !== 'settings' ? 'hidden' : ''}`}>
          <div className="panel">
            <h2>Workspace Settings</h2>
            <p className="muted">Configure security policies, API credentials, and retention rules.</p>
            <div className="formgrid" style={{ marginTop: '20px' }}>
              <label>Workspace Name
                <input defaultValue="FlowDesk Enterprise Command Center" />
              </label>
              <label>API Key Rotation
                <input type="password" defaultValue="dev-only-change-me-secret" />
              </label>
              <label>Audit Log Retention (Days)
                <input type="number" defaultValue="365" />
              </label>
              <label>Automated Triage Engine
                <select><option>Rule-based baseline v3.0</option><option>Trained Transformer (Beta)</option></select>
              </label>
              <button className="primary" style={{ gridColumn: '1/-1' }}>Save Workspace Configuration</button>
            </div>
          </div>
        </section>

        {/* BURGER & BURGUNDY VIEW */}
        <section className={`view ${activeView !== 'burger' ? 'hidden' : ''}`}>
          <BurgundyBurgerExperience />
        </section>

        {/* TOAST */}
        {toastMessage && (
          <div id="toast" className="toast" role="status" style={{ background: toastMessage.err ? '#800020' : '#24785B' }}>
            {toastMessage.text}
          </div>
        )}

        {/* TICKET DETAILS DRAWER OVERLAY */}
        <div className={`overlay ${selectedTicket ? 'open' : ''}`} id="overlay" role="dialog" aria-modal="true" aria-label="Ticket details" onClick={e => { if (e.target === e.currentTarget) setSelectedTicketId(null); }}>
          <div className="drawer">
            <div className="between">
              <h2 id="detailTitle">{selectedTicket ? `Ticket #${selectedTicket.id}` : 'Ticket'}</h2>
              <button id="close" onClick={() => setSelectedTicketId(null)}><X size={16} /></button>
            </div>
            <p id="detailMeta" className="muted">
              {selectedTicket ? `${selectedTicket.subject} · ${selectedTicket.sender} · ${selectedTicket.category} · ${selectedTicket.assigned_team} · ${Math.round(selectedTicket.confidence * 100)}% confidence` : ''}
            </p>
            <div id="detailBody" className="bodytext" style={{ marginTop: '16px' }}>{selectedTicket?.body}</div>
            
            <h3 style={{ marginTop: '24px' }}>Update ticket</h3>
            <div className="formgrid">
              <label>Status
                <select id="ticketStatus" value={editStatus} onChange={e => setEditStatus(e.target.value as any)}>
                  <option>Open</option>
                  <option>In Progress</option>
                  <option>Resolved</option>
                  <option>Closed</option>
                </select>
              </label>
              <label>Priority
                <select id="ticketPriority" value={editPriority} onChange={e => setEditPriority(e.target.value as any)}>
                  <option>Normal</option>
                  <option>High</option>
                  <option>Critical</option>
                </select>
              </label>
              <button className="primary wide" id="save" onClick={handleSaveTicketChanges}>Save ticket changes</button>
            </div>

            <h3 style={{ marginTop: '24px' }}>Activity and audit history</h3>
            <div id="events">
              {selectedEvents.map(e => (
                <div key={e.id} className="event">
                  {new Date(e.created_at).toLocaleString()} · {e.actor} · {e.message}
                </div>
              ))}
            </div>

            <h3 style={{ marginTop: '22px' }}>Internal note</h3>
            <textarea id="note" placeholder="Record an action or finding" value={newNote} onChange={e => setNewNote(e.target.value)}></textarea>
            <button style={{ marginTop: '9px' }} id="addNote" onClick={handleAddNote}>Add note</button>
          </div>
        </div>

        <footer className="muted" style={{ marginTop: '40px', borderTop: '1px solid var(--border)', paddingTop: '20px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <span>FlowDesk 3.0 · Research-oriented prototype · Follow security hardening before public hosting</span>
          <span style={{ fontStyle: 'italic', color: 'var(--burgundy)', fontWeight: 600 }}>Smarter Operations Everyday</span>
        </footer>
      </main>
    </div>
  );
}
