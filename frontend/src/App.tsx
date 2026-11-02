import './App.css'
import { useCallback, useEffect, useMemo, useState } from 'react'

type Page = 'overview' | 'chat' | 'knowledge' | 'sources'
type IconName =
  | 'activity' | 'arrow' | 'bell' | 'book' | 'bot' | 'database' | 'check'
  | 'chevron' | 'clock' | 'close' | 'file' | 'grid' | 'help'
  | 'layers' | 'menu' | 'message' | 'more' | 'paperclip'
  | 'plus' | 'search' | 'send' | 'sparkles' | 'trend'
  | 'upload' | 'users'

type DocumentItem = {
  name: string
  path: string
  category: string
  file_type: string
  size_bytes: number
  modified: number
  indexed_chunks: number
}

type KnowledgeStats = {
  collection: string
  total_chunks: number
  storage: string
}

type AskSource = {
  document: string
  similarity: number
}

type AskResponse = {
  answer: string
  sources: AskSource[]
  confidence: number
  grounded: boolean
}

const iconPaths: Record<IconName, React.ReactNode> = {
  activity: <path d="M3 12h4l2.5-7 5 14 2.5-7h4" />,
  arrow: <><path d="M5 12h14M13 6l6 6-6 6" /></>,
  bell: <><path d="M18 8a6 6 0 0 0-12 0c0 7-3 7-3 9h18c0-2-3-2-3-9M10 21h4" /></>,
  book: <><path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20V4H6.5A2.5 2.5 0 0 0 4 6.5zM4 6.5v13" /></>,
  bot: <><rect x="4" y="8" width="16" height="12" rx="3" /><path d="M9 12h.01M15 12h.01M9 16h6M12 8V4M9 4h6" /></>,
  database: <><ellipse cx="12" cy="5" rx="9" ry="3" /><path d="M3 5v14c0 1.7 4 3 9 3s9-1.3 9-3V5M3 12c0 1.7 4 3 9 3s9-1.3 9-3" /></>,
  check: <path d="m5 12 4 4L19 6" />,
  chevron: <path d="m9 18 6-6-6-6" />,
  clock: <><circle cx="12" cy="12" r="9" /><path d="M12 7v5l3 2" /></>,
  close: <path d="m6 6 12 12M18 6 6 18" />,
  file: <><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" /><path d="M14 2v6h6M8 13h8M8 17h6" /></>,
  grid: <><rect x="3" y="3" width="7" height="7" rx="1" /><rect x="14" y="3" width="7" height="7" rx="1" /><rect x="3" y="14" width="7" height="7" rx="1" /><rect x="14" y="14" width="7" height="7" rx="1" /></>,
  help: <><circle cx="12" cy="12" r="9" /><path d="M9.6 9a2.5 2.5 0 1 1 4.2 1.8c-1 .8-1.8 1.2-1.8 2.7M12 17h.01" /></>,
  layers: <><path d="m12 2 9 5-9 5-9-5zM3 12l9 5 9-5M3 17l9 5 9-5" /></>,
  menu: <path d="M4 7h16M4 12h16M4 17h16" />,
  message: <path d="M21 15a4 4 0 0 1-4 4H8l-5 3V7a4 4 0 0 1 4-4h10a4 4 0 0 1 4 4z" />,
  more: <><circle cx="5" cy="12" r="1" /><circle cx="12" cy="12" r="1" /><circle cx="19" cy="12" r="1" /></>,
  paperclip: <path d="m21 11.5-8.5 8.5a6 6 0 0 1-8.5-8.5l9-9a4 4 0 0 1 5.5 5.5l-9 9a2 2 0 0 1-3-3l8.5-8.5" />,
  plus: <path d="M12 5v14M5 12h14" />,
  search: <><circle cx="11" cy="11" r="7" /><path d="m20 20-4-4" /></>,
  send: <><path d="m22 2-7 20-4-9-9-4zM22 2 11 13" /></>,
  sparkles: <path d="m12 3-1.2 3.2a7 7 0 0 1-4.1 4.1L3.5 11.5l3.2 1.2a7 7 0 0 1 4.1 4.1L12 20l1.2-3.2a7 7 0 0 1 4.1-4.1l3.2-1.2-3.2-1.2a7 7 0 0 1-4.1-4.1z" />,
  trend: <path d="m3 17 6-6 4 4 8-8M15 7h6v6" />,
  upload: <><path d="M12 16V4M7 9l5-5 5 5M4 20h16" /></>,
  users: <path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2M9 11a4 4 0 1 0 0-8M22 21v-2a4 4 0 0 0-3-3.87M16 3.13a4 4 0 0 1 0 7.75" />,
}

function Icon({ name, size = 18 }: { name: IconName; size?: number }) {
  return <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">{iconPaths[name]}</svg>
}

const navItems: { id: Page; label: string; icon: IconName }[] = [
  { id: 'overview', label: 'Overview', icon: 'grid' },
  { id: 'chat', label: 'AI Support Chat', icon: 'message' },
  { id: 'knowledge', label: 'Knowledge Base', icon: 'book' },
  { id: 'sources', label: 'Source Explorer', icon: 'layers' },
]

const pageTitles: Record<Page, { title: string; eyebrow: string }> = {
  overview: { title: 'SupportIQ Overview', eyebrow: 'Live status of your support knowledge system.' },
  chat: { title: 'AI Support Chat', eyebrow: 'Get answers grounded in your indexed support knowledge.' },
  knowledge: { title: 'Knowledge Base', eyebrow: 'Review your documents and refresh the knowledge index.' },
  sources: { title: 'Source Explorer', eyebrow: 'Search the documents available to the retrieval system.' },
}

function Status({ children, tone = 'green' }: { children: React.ReactNode; tone?: 'green' | 'blue' | 'violet' | 'amber' }) {
  return <span className={`status status-${tone}`}><span className="status-dot" />{children}</span>
}

function formatBytes(bytes: number) {
  if (!Number.isFinite(bytes) || bytes <= 0) return '—'
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
}

function formatDate(timestamp: number) {
  if (!timestamp) return '—'
  return new Date(timestamp * 1000).toLocaleString()
}

function errorMessage(value: unknown) {
  return value instanceof Error ? value.message : 'An unexpected error occurred.'
}

async function apiRequest<T>(url: string, options?: RequestInit): Promise<T> {
  const response = await fetch(url, {
    ...options,
    headers: { 'Content-Type': 'application/json', ...(options?.headers || {}) },
  })
  const payload = await response.json().catch(() => ({}))
  if (!response.ok) {
    throw new Error(typeof payload.detail === 'string' ? payload.detail : `Request failed (${response.status})`)
  }
  return payload as T
}

function Sidebar({ page, setPage, collapsed, setCollapsed, mobileOpen, setMobileOpen }: {
  page: Page
  setPage: (page: Page) => void
  collapsed: boolean
  setCollapsed: (value: boolean) => void
  mobileOpen: boolean
  setMobileOpen: (value: boolean) => void
}) {
  return <>
    {mobileOpen && <div className="mobile-backdrop" onClick={() => setMobileOpen(false)} />}
    <aside className={`sidebar ${collapsed ? 'collapsed' : ''} ${mobileOpen ? 'mobile-open' : ''}`}>
      <div className="brand-row">
        <div className="brand-mark"><Icon name="sparkles" size={19} /></div>
        {!collapsed && <span className="brand-name">Support<span>IQ</span></span>}
        <button className="icon-button mobile-close" onClick={() => setMobileOpen(false)} aria-label="Close navigation"><Icon name="close" /></button>
      </div>
      <div className="workspace">
        <div className="workspace-logo">SI</div>
        {!collapsed && <div className="workspace-copy"><strong>SupportIQ Workspace</strong><span>Knowledge assistant</span></div>}
        {!collapsed && <Icon name="chevron" size={15} />}
      </div>
      <nav className="primary-nav" aria-label="Main navigation">
        {!collapsed && <span className="nav-label">Workspace</span>}
        {navItems.map((item) => (
          <button key={item.id} className={`nav-item ${page === item.id ? 'active' : ''}`} onClick={() => { setPage(item.id); setMobileOpen(false) }} title={collapsed ? item.label : undefined}>
            <Icon name={item.icon} size={19} /><span>{item.label}</span>
            {item.id === 'chat' && !collapsed && <span className="ai-pill">AI</span>}
          </button>
        ))}
      </nav>
      <div className="sidebar-bottom">
        <div className="nav-item"><Icon name="help" size={19} /><span>FastAPI · ChromaDB</span></div>
        <button className="collapse-button" onClick={() => setCollapsed(!collapsed)}><Icon name="chevron" size={17} /><span>Collapse sidebar</span></button>
      </div>
    </aside>
  </>
}

function Topbar({ page, onMenu, backendOnline }: { page: Page; onMenu: () => void; backendOnline: boolean }) {
  return <header className="topbar">
    <div className="topbar-title">
      <button className="icon-button menu-button" onClick={onMenu} aria-label="Open navigation"><Icon name="menu" /></button>
      <div><strong>{pageTitles[page].title}</strong><span>{pageTitles[page].eyebrow}</span></div>
    </div>
    <div className="topbar-actions">
      <Status tone={backendOnline ? 'green' : 'amber'}>{backendOnline ? 'API connected' : 'API unavailable'}</Status>
      <div className="profile"><div className="avatar">SI</div><div><strong>Administrator</strong><span>Workspace</span></div></div>
    </div>
  </header>
}

function MetricCard({ label, value, note, icon, tone }: { label: string; value: string; note: string; icon: IconName; tone: string }) {
  return <div className="card metric-card">
    <div className={`metric-icon ${tone}`}><Icon name={icon} size={19} /></div>
    <div className="metric-header"><span>{label}</span></div>
    <strong className="metric-value">{value}</strong>
    <div className="metric-change"><span>{note}</span></div>
  </div>
}

function Overview({ stats, documents, backendOnline, loading, onRefresh, goToChat, error }: {
  stats: KnowledgeStats | null
  documents: DocumentItem[]
  backendOnline: boolean
  loading: boolean
  onRefresh: () => void
  goToChat: () => void
  error: string
}) {
  const indexedDocuments = documents.filter((doc) => doc.indexed_chunks > 0).length
  const totalIndexed = documents.length
  return <div className="page-content">
    <section className="welcome-banner">
      <div className="welcome-orb orb-one" /><div className="welcome-orb orb-two" />
      <div className="welcome-copy">
        <span className="welcome-label"><Icon name="sparkles" size={14} /> AI support intelligence</span>
        <strong>Turn your support knowledge into trusted answers.</strong>
        <p>SupportIQ retrieves relevant information from your documents and generates answers grounded in the indexed knowledge base.</p>
        <button className="welcome-button" onClick={goToChat}>Ask SupportIQ <Icon name="arrow" size={16} /></button>
      </div>
      <div className="welcome-visual" aria-hidden="true">
        <div className="floating-card floating-main">
          <div><span>Indexed knowledge chunks</span><strong>{stats?.total_chunks ?? '—'}</strong></div>
          <div className="mini-bars"><i /><i /><i /><i /><i /><i /><i /></div>
        </div>
        <div className="floating-card floating-small"><span><Icon name="check" size={14} /> {backendOnline ? 'Connected' : 'Offline'}</span><small>Backend status</small></div>
        <div className="floating-badge"><Icon name="file" size={15} /> {documents.length} source files</div>
      </div>
    </section>
    <section className="metrics-grid">
      <MetricCard label="Source documents" value={loading ? '…' : String(totalIndexed)} note="Files found in documents/" icon="file" tone="blue" />
      <MetricCard label="Indexed documents" value={loading ? '…' : String(indexedDocuments)} note="Documents with indexed chunks" icon="check" tone="violet" />
      <MetricCard label="Indexed chunks" value={loading ? '…' : String(stats?.total_chunks ?? 0)} note="ChromaDB collection count" icon="layers" tone="green" />
      <MetricCard label="Backend status" value={backendOnline ? 'Online' : 'Offline'} note={stats?.storage ?? 'Waiting for API'} icon="activity" tone="amber" />
    </section>
    <section className="overview-grid">
      <div className="card chart-card">
        <div className="section-heading"><div><strong>Knowledge base status</strong><span>Current document indexing overview</span></div><button className="filter-button" onClick={onRefresh} disabled={loading}>Refresh <Icon name="arrow" size={14} /></button></div>
        <div className="knowledge-stats">
          <div className="compact-stat"><div className="metric-icon blue"><Icon name="file" /></div><div><span>Documents discovered</span><strong>{documents.length}</strong></div></div>
          <div className="compact-stat"><div className="metric-icon violet"><Icon name="layers" /></div><div><span>Indexed documents</span><strong>{indexedDocuments}</strong></div></div>
          <div className="compact-stat"><div className="metric-icon green"><Icon name="database" /></div><div><span>Chunks in collection</span><strong>{stats?.total_chunks ?? 0}</strong></div></div>
        </div>
        <p className="muted-note">Document discovery and indexed chunk counts are read from the SupportIQ API. No conversation analytics endpoint is currently configured.</p>
        {error && <p className="error-text">{error}</p>}
      </div>
      <div className="card ai-preview">
        <div className="ai-glow" />
        <div className="section-heading"><div><strong>Ask SupportIQ</strong><span>Answers from your knowledge base</span></div><div className="assistant-icon"><Icon name="sparkles" /></div></div>
        <div className="mini-conversation">
          <div className="mini-user">Ask a question about shipping, returns, payments, or products.</div>
          <div className="mini-ai"><div className="mini-ai-avatar"><Icon name="sparkles" size={14} /></div><p>SupportIQ searches indexed documents and returns an answer with source references when relevant information is found.</p></div>
        </div>
        <div className="source-chip"><Icon name="layers" size={14} /> Retrieval-augmented generation <span>RAG</span></div>
        <button className="primary-button full-button" onClick={goToChat}>Open AI Support Chat <Icon name="arrow" size={16} /></button>
      </div>
    </section>
    <section className="card activity-card">
      <div className="section-heading"><div><strong>Available source documents</strong><span>Latest files returned by the knowledge API</span></div><button className="text-button" onClick={onRefresh}>Refresh list <Icon name="arrow" size={14} /></button></div>
      <div className="activity-list">
        {documents.slice(0, 5).map((doc) => <div className="activity-row" key={doc.path}>
          <div className="activity-icon blue"><Icon name="file" size={17} /></div>
          <div className="activity-copy"><strong>{doc.name}</strong><span>{doc.path} · {doc.indexed_chunks} indexed chunks</span></div>
          <Status tone={doc.indexed_chunks > 0 ? 'green' : 'amber'}>{doc.indexed_chunks > 0 ? 'Indexed' : 'Not indexed'}</Status>
        </div>)}
        {!documents.length && <div className="empty-state"><Icon name="file" /><strong>No supported documents found</strong><span>Add PDF, DOCX, TXT, or MD files to the documents folder.</span></div>}
      </div>
    </section>
  </div>
}

type ChatMessage = {
  role: 'user' | 'assistant'
  text: string
  result?: AskResponse
  error?: string
}

function Chat() {
  const [input, setInput] = useState('')
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [sending, setSending] = useState(false)
  const [error, setError] = useState('')
  const suggestions = [
    'What is the return and refund policy?',
    'How long does standard shipping take?',
    'Which payment methods are supported?',
  ]

  const send = async (raw = input) => {
    const question = raw.trim()
    if (!question || sending) return
    setInput('')
    setError('')
    setMessages((current) => [...current, { role: 'user', text: question }])
    setSending(true)
    try {
      const result = await apiRequest<AskResponse>('/api/ask', {
        method: 'POST',
        body: JSON.stringify({ question, top_k: 3 }),
      })
      setMessages((current) => [...current, { role: 'assistant', text: result.answer, result }])
    } catch (err) {
      const message = errorMessage(err)
      setError(message)
      setMessages((current) => [...current, { role: 'assistant', text: 'I could not complete that request.', error: message }])
    } finally {
      setSending(false)
    }
  }

  return <div className="chat-layout">
    <aside className="chat-history card">
      <button className="primary-button new-chat" onClick={() => { setMessages([]); setError(''); setInput('') }}><Icon name="plus" /> New conversation</button>
      <span className="nav-label">Session</span>
      <div className="history-item active"><span>Current conversation</span><small>{messages.length} messages</small></div>
      <div className="index-health"><div><Icon name="activity" /><strong>Answer grounding</strong></div><span>Responses include source references when available.</span></div>
    </aside>
    <section className="chat-main card">
      <div className="chat-titlebar"><div><div className="assistant-icon"><Icon name="sparkles" /></div><div><strong>SupportIQ Assistant</strong><span><i /> Connected to the knowledge API</span></div></div><Status tone="blue">RAG enabled</Status></div>
      <div className="messages">
        <div className="date-divider"><span>Conversation</span></div>
        {!messages.length && <div className="empty-state"><div className="assistant-icon"><Icon name="sparkles" size={24} /></div><strong>What would you like to know?</strong><span>Ask a question and SupportIQ will search the indexed knowledge base.</span></div>}
        {messages.map((message, index) => (
          <div className={`message ${message.role === 'user' ? 'user-message' : 'ai-message'}`} key={`${message.role}-${index}`}>
            {message.role === 'user' ? <div className="avatar small">You</div> : <div className="mini-ai-avatar"><Icon name="sparkles" size={15} /></div>}
            <div>
              <span>{message.role === 'user' ? 'You' : 'SupportIQ'}</span>
              <div className="answer"><p>{message.text}</p>
                {message.error && <p className="error-text">{message.error}</p>}
                {message.result && <div className="confidence">
                  <Status tone={message.result.grounded ? 'green' : 'amber'}>{message.result.grounded ? 'Grounded answer' : 'Fallback / ungrounded'}</Status>
                  <span>Retrieval similarity: {(message.result.confidence * 100).toFixed(1)}%</span>
                </div>}
              </div>
              {message.result?.sources?.length ? <div className="citations">
                {message.result.sources.map((source, sourceIndex) => <div className="citation-item" key={`${source.document}-${sourceIndex}`}>
                  <Icon name="file" size={14} /><span><strong>{source.document}</strong> Similarity {(source.similarity * 100).toFixed(1)}%</span>
                </div>)}
              </div> : null}
            </div>
          </div>
        ))}
        {sending && <div className="message ai-message"><div className="mini-ai-avatar"><Icon name="sparkles" size={15} /></div><div><span>SupportIQ</span><div className="answer"><p>Searching your knowledge base…</p></div></div></div>}
        <div className="suggestions"><span>Try asking</span><div>{suggestions.map((suggestion) => <button key={suggestion} onClick={() => send(suggestion)} disabled={sending}>{suggestion}<Icon name="arrow" size={13} /></button>)}</div></div>
      </div>
      <div className="composer-wrap">
        <div className="composer"><textarea value={input} onChange={(event) => setInput(event.target.value)} onKeyDown={(event) => { if (event.key === 'Enter' && !event.shiftKey) { event.preventDefault(); void send() } }} placeholder="Ask a question about your support knowledge..." />
          <div><span>Enter to send · Shift + Enter for new line</span><button className="send-button" onClick={() => void send()} disabled={sending || !input.trim()} aria-label="Send"><Icon name="send" size={17} /></button></div>
        </div>
        {error && <small className="error-text">{error}</small>}
        <small>Verify critical support information before acting on an answer.</small>
      </div>
    </section>
  </div>
}

function Knowledge({ documents, stats, loading, indexing, error, onRefresh, onIndex }: {
  documents: DocumentItem[]
  stats: KnowledgeStats | null
  loading: boolean
  indexing: boolean
  error: string
  onRefresh: () => void
  onIndex: () => void
}) {
  const indexed = documents.filter((doc) => doc.indexed_chunks > 0).length
  return <div className="page-content">
    <section className="knowledge-stats">
      <div className="card compact-stat"><div className="metric-icon blue"><Icon name="file" /></div><div><span>Total documents</span><strong>{loading ? '…' : documents.length}</strong></div><small>Supported files discovered</small></div>
      <div className="card compact-stat"><div className="metric-icon violet"><Icon name="layers" /></div><div><span>Indexed chunks</span><strong>{stats?.total_chunks ?? 0}</strong></div><small>Persistent ChromaDB collection</small></div>
      <div className="card compact-stat"><div className="metric-icon green"><Icon name="check" /></div><div><span>Indexed documents</span><strong>{indexed}</strong></div><small>Files with indexed chunks</small></div>
    </section>
    <section className="card upload-card">
      <div className="upload-icon"><Icon name="upload" size={23} /></div>
      <div><strong>Refresh knowledge index</strong><span>Re-process supported files currently stored in the documents folder.</span></div>
      <button className="secondary-button" onClick={onIndex} disabled={indexing}><Icon name="upload" size={16} />{indexing ? 'Indexing…' : 'Run indexing'}</button>
      <button className="text-button" onClick={onRefresh} disabled={loading}><Icon name="plus" size={16} /> Refresh list</button>
    </section>
    {error && <p className="error-text">{error}</p>}
    <section className="card documents-card">
      <div className="document-toolbar"><div><strong>Documents</strong><span>Files discovered by the SupportIQ API</span></div><div><button className="filter-button" onClick={onRefresh} disabled={loading}>Refresh <Icon name="arrow" size={14} /></button></div></div>
      <div className="table-wrap"><table><thead><tr><th>Document</th><th>Category</th><th>Status</th><th>Chunks</th><th>Size</th><th>Modified</th></tr></thead>
        <tbody>{documents.map((doc) => <tr key={doc.path}>
          <td><div className={`file-tile ${doc.file_type.toLowerCase()}`}><Icon name="file" size={17} /></div><div><strong>{doc.name}</strong><span>{doc.path}</span></div></td>
          <td>{doc.category}</td><td><Status tone={doc.indexed_chunks > 0 ? 'green' : 'amber'}>{doc.indexed_chunks > 0 ? 'Indexed' : 'Not indexed'}</Status></td>
          <td>{doc.indexed_chunks}</td><td>{formatBytes(doc.size_bytes)}</td><td>{formatDate(doc.modified)}</td>
        </tr>)}</tbody>
      </table></div>
      {!documents.length && <div className="empty-state"><Icon name="file" size={28} /><strong>No documents found</strong><span>Add PDF, DOCX, TXT, or MD files to the documents directory.</span></div>}
      <div className="table-footer"><span>{documents.length} document(s) · {stats?.total_chunks ?? 0} total chunks</span><span>{stats?.collection ?? 'Collection unavailable'}</span></div>
    </section>
  </div>
}

function Sources({ documents, stats }: { documents: DocumentItem[]; stats: KnowledgeStats | null }) {
  const [query, setQuery] = useState('')
  const [category, setCategory] = useState('All sources')
  const categories = useMemo(() => ['All sources', ...Array.from(new Set(documents.map((doc) => doc.category))).sort()], [documents])
  const filtered = useMemo(() => documents.filter((doc) =>
    (category === 'All sources' || doc.category === category) &&
    `${doc.name} ${doc.path} ${doc.category} ${doc.file_type}`.toLowerCase().includes(query.toLowerCase())
  ), [documents, query, category])
  return <div className="source-layout">
    <aside className="source-filters card">
      <div><strong>Filters</strong><button className="text-button" onClick={() => { setCategory('All sources'); setQuery('') }}>Reset</button></div>
      <label>Category</label>
      {categories.map((item) => <button key={item} className={category === item ? 'selected' : ''} onClick={() => setCategory(item)}><span>{item}</span><small>{item === 'All sources' ? documents.length : documents.filter((doc) => doc.category === item).length}</small></button>)}
      <div className="index-health"><div><Icon name="activity" /><strong>Index status</strong></div><span><i /> {stats?.total_chunks ?? 0} chunks in collection</span><div className="progress"><i /></div><small>{documents.filter((doc) => doc.indexed_chunks > 0).length} of {documents.length} documents have indexed chunks</small></div>
    </aside>
    <section className="sources-main">
      <div className="source-search"><Icon name="search" /><input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Search source documents..." /><kbd>⌘ K</kbd></div>
      <div className="results-heading"><div><strong>{filtered.length} source(s)</strong><span>Discovered from the documents directory</span></div><span>{stats?.total_chunks ?? 0} indexed chunks</span></div>
      <div className="source-cards">{filtered.map((doc) => <article className="card source-card" key={doc.path}>
        <div className="source-card-top"><div className={`file-tile ${doc.file_type.toLowerCase()}`}><Icon name="file" /></div><Status tone={doc.indexed_chunks > 0 ? 'green' : 'amber'}>{doc.indexed_chunks > 0 ? 'Indexed' : 'Not indexed'}</Status></div>
        <strong>{doc.name}</strong><p>{doc.path}</p>
        <div className="source-tags"><span>{doc.category}</span><span>{doc.file_type}</span></div>
        <div className="source-details"><div><span>Indexed chunks</span><strong>{doc.indexed_chunks}</strong></div><div><span>File size</span><strong>{formatBytes(doc.size_bytes)}</strong></div></div>
        <footer><span>Modified {formatDate(doc.modified)}</span><span>{doc.indexed_chunks > 0 ? 'Available for retrieval' : 'Awaiting indexing'}</span></footer>
      </article>)}</div>
      {filtered.length === 0 && <div className="card empty-state"><Icon name="search" size={28} /><strong>No sources found</strong><span>Try changing your search or category filter.</span></div>}
    </section>
  </div>
}

export default function App() {
  const [page, setPage] = useState<Page>('overview')
  const [collapsed, setCollapsed] = useState(false)
  const [mobileOpen, setMobileOpen] = useState(false)
  const [backendOnline, setBackendOnline] = useState(false)
  const [stats, setStats] = useState<KnowledgeStats | null>(null)
  const [documents, setDocuments] = useState<DocumentItem[]>([])
  const [loading, setLoading] = useState(true)
  const [indexing, setIndexing] = useState(false)
  const [error, setError] = useState('')

  const refreshData = useCallback(async () => {
    setLoading(true)
    setError('')
    try {
      const [health, nextStats, documentResult] = await Promise.all([
        apiRequest<{ status: string }>('/health'),
        apiRequest<KnowledgeStats>('/api/knowledge/stats'),
        apiRequest<{ total_documents: number; total_chunks: number; documents: DocumentItem[] }>('/api/knowledge/documents'),
      ])
      setBackendOnline(health.status === 'healthy')
      setStats(nextStats)
      setDocuments(documentResult.documents || [])
    } catch (err) {
      setBackendOnline(false)
      setError(errorMessage(err))
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => { void refreshData() }, [refreshData])

  const runIndex = async () => {
    setIndexing(true)
    setError('')
    try {
      await apiRequest<Record<string, unknown>>('/api/index', { method: 'POST' })
      await refreshData()
    } catch (err) {
      setError(errorMessage(err))
    } finally {
      setIndexing(false)
    }
  }

  return <div className="app-shell">
    <Sidebar page={page} setPage={setPage} collapsed={collapsed} setCollapsed={setCollapsed} mobileOpen={mobileOpen} setMobileOpen={setMobileOpen} />
    <div className={`main-shell ${collapsed ? 'sidebar-collapsed' : ''}`}>
      <Topbar page={page} onMenu={() => setMobileOpen(true)} backendOnline={backendOnline} />
      <main>
        {page === 'overview' && <Overview stats={stats} documents={documents} backendOnline={backendOnline} loading={loading} onRefresh={() => void refreshData()} goToChat={() => setPage('chat')} error={error} />}
        {page === 'chat' && <Chat />}
        {page === 'knowledge' && <Knowledge documents={documents} stats={stats} loading={loading} indexing={indexing} error={error} onRefresh={() => void refreshData()} onIndex={() => void runIndex()} />}
        {page === 'sources' && <Sources documents={documents} stats={stats} />}
      </main>
    </div>
  </div>
}


