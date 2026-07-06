import { useEffect, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import { motion } from 'framer-motion';
import {
  AlertTriangle,
  ArrowLeft,
  BarChart3,
  Building,
  Check,
  ChevronDown,
  Clock,
  Copy,
  ExternalLink,
  FileText,
  Loader2,
  MapPin,
  Target,
  Zap,
} from 'lucide-react';
import toast from 'react-hot-toast';
import api from '../lib/api';

interface ApplicationDetail {
  id: number;
  status: string;
  stage: string;
  status_reason: string | null;
  source_url: string | null;
  match_score: number | null;
  needs_user_review: boolean;
  applied_at: string | null;
  submitted_at: string | null;
  last_event_at: string | null;
}

interface JobDetail {
  id: number;
  title: string;
  company: string;
  location: string | null;
  url: string;
  description: string;
  source: string;
  salary: string | null;
  experience_level: string | null;
}

interface Artifact {
  tailored_resume_text: string | null;
  cover_letter_text: string | null;
  resume_pdf_path: string | null;
  match_explanation: string | null;
  matched_skills: string[];
  missing_skills: string[];
  weak_skills: string[];
}

interface TimelineEvent {
  id: number;
  event_type: string;
  status: string;
  message: string | null;
  metadata: Record<string, unknown>;
  created_at: string | null;
}

interface DetailPayload {
  application: ApplicationDetail | null;
  job: JobDetail;
  artifact: Artifact | null;
  events: TimelineEvent[];
}

const STATUS_COLORS: Record<string, string> = {
  Draft: 'var(--text-muted)',
  Pending: 'var(--accent-amber)',
  Ready: 'var(--accent-cyan)',
  Applied: 'var(--accent-emerald)',
  Failed: 'var(--accent-rose)',
  Skipped: 'var(--text-muted)',
  'Needs Review': 'var(--accent-amber)',
  Rejected: 'var(--accent-rose)',
  Interview: 'var(--accent-indigo)',
  Offer: 'var(--accent-cyan)',
};

const EVENT_ICONS: Record<string, typeof Zap> = {
  application_created: FileText,
  automation_started: Zap,
  match_scored: Target,
  resume_generated: FileText,
  cover_letter_generated: FileText,
  submitted: Check,
  skipped: AlertTriangle,
  failed: AlertTriangle,
  status_changed: BarChart3,
};

const ALLOWED_STATUSES = [
  'Pending',
  'Ready',
  'Applied',
  'Interview',
  'Offer',
  'Rejected',
  'Skipped',
  'Needs Review',
];

function formatDate(iso: string | null): string {
  if (!iso) return '-';
  return new Date(iso).toLocaleString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
}

function CopyButton({ text }: { text: string }) {
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    await navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <button className="btn-ghost" onClick={handleCopy} style={{ padding: '6px 12px', fontSize: '0.75rem' }}>
      {copied ? <><Check size={12} /> Copied</> : <><Copy size={12} /> Copy</>}
    </button>
  );
}

export default function JobDetailPage() {
  const { jobId } = useParams<{ jobId: string }>();
  const [data, setData] = useState<DetailPayload | null>(null);
  const [loading, setLoading] = useState(true);
  const [artifactTab, setArtifactTab] = useState<'resume' | 'cover_letter'>('resume');
  const [statusValue, setStatusValue] = useState('');
  const [statusNote, setStatusNote] = useState('');
  const [saving, setSaving] = useState(false);
  const [preparing, setPreparing] = useState(false);
  const [submitting, setSubmitting] = useState(false);

  const loadDetail = async () => {
    const detailRes = await api.get(`/applications/by-job/${jobId}/detail`);
    setData(detailRes.data);
    setStatusValue(detailRes.data.application?.status || 'Needs Review');
  };

  useEffect(() => {
    const load = async () => {
      try {
        await loadDetail();
      } catch {
        toast.error('Failed to load job details.');
      } finally {
        setLoading(false);
      }
    };
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [jobId]);

  const handlePrepare = async () => {
    if (!jobId) return;
    setPreparing(true);
    try {
      const res = await api.post(`/jobs/${jobId}/apply`);
      toast.success(res.data.message || 'Preparation complete. Review before submitting.');
      await loadDetail();
    } catch (err: unknown) {
      const message =
        (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail ||
        'Failed to prepare application.';
      toast.error(message);
    } finally {
      setPreparing(false);
    }
  };

  const handleStatusSave = async () => {
    if (!data?.application) return;
    setSaving(true);
    try {
      await api.patch(`/applications/${data.application.id}/status`, {
        status: statusValue,
        note: statusNote || undefined,
      });
      toast.success(`Status updated to ${statusValue}`);
      await loadDetail();
      setStatusNote('');
    } catch {
      toast.error('Failed to update status.');
    } finally {
      setSaving(false);
    }
  };

  const handleSubmit = async () => {
    if (!data?.application || !jobId) return;
    setSubmitting(true);
    try {
      const res = await api.post(`/jobs/${jobId}/submit`);
      toast.success(res.data.message);
      await loadDetail();
    } catch (err: unknown) {
      const message =
        (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail ||
        'Submission failed.';
      toast.error(message);
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) {
    return (
      <div className="loading-screen" style={{ minHeight: '60vh' }}>
        <Loader2 className="spinner" size={24} />
        <span>Loading details...</span>
      </div>
    );
  }

  if (!data?.job) {
    return (
      <div className="flex-col gap-lg" style={{ padding: '40px 0' }}>
        <Link to="/jobs" className="detail-back-link">
          <ArrowLeft size={16} /> Back to Jobs
        </Link>
        <div className="empty-state">
          <FileText className="empty-state-icon" />
          <p>Job details could not be loaded.</p>
        </div>
      </div>
    );
  }

  const { application, artifact, events, job } = data;
  const matchScore = application?.match_score ?? null;
  const badgeColor = application
    ? STATUS_COLORS[application.status] || 'var(--text-muted)'
    : 'var(--text-muted)';

  return (
    <div className="flex-col gap-xl">
      <div>
        <Link to="/jobs" className="detail-back-link">
          <ArrowLeft size={16} /> Back to Jobs
        </Link>

        <motion.div initial={{ opacity: 0, y: 15 }} animate={{ opacity: 1, y: 0 }} className="detail-header">
          <div className="detail-header-info">
            <h1>{job.title}</h1>
            <div className="detail-header-meta">
              <span className="detail-meta-item"><Building size={14} /> {job.company}</span>
              <span className="detail-meta-item"><MapPin size={14} /> {job.location || 'Remote'}</span>
              {job.salary && <span className="detail-meta-item">{job.salary}</span>}
            </div>
          </div>
          <div className="detail-header-actions">
            <span className="status-badge" style={{ '--badge-color': badgeColor } as React.CSSProperties}>
              {application?.status || 'Not Prepared'}
            </span>
            {!application && (
              <button className="btn-primary" onClick={handlePrepare} disabled={preparing} style={{ fontSize: '0.8rem', padding: '8px 16px' }}>
                {preparing ? <><Loader2 className="spinner" size={14} /> Preparing...</> : <><Zap size={14} /> Prepare Application</>}
              </button>
            )}
            {(application?.status === 'Needs Review' || application?.status === 'Ready') && (
              <button className="btn-primary" onClick={handleSubmit} disabled={submitting} style={{ fontSize: '0.8rem', padding: '8px 16px' }}>
                {submitting ? <><Loader2 className="spinner" size={14} /> Submitting...</> : <><Check size={14} /> Approve & Submit</>}
              </button>
            )}
            {job.url && (
              <a href={job.url} target="_blank" rel="noopener noreferrer" className="btn-ghost">
                <ExternalLink size={14} /> View Posting
              </a>
            )}
          </div>
        </motion.div>
      </div>

      <div className="detail-grid">
        <div className="flex-col gap-lg">
          {matchScore !== null && (
            <motion.div initial={{ opacity: 0, y: 15 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }} className="glass section-card">
              <div className="section-card-header">
                <h2><Target size={18} className="section-icon" /> Match Analysis</h2>
              </div>
              <div className="section-card-body">
                <div className="match-score-row">
                  <div className="match-gauge">
                    <svg viewBox="0 0 120 120" className="match-gauge-svg">
                      <circle cx="60" cy="60" r="50" fill="none" stroke="rgba(255,255,255,0.06)" strokeWidth="8" />
                      <circle
                        cx="60"
                        cy="60"
                        r="50"
                        fill="none"
                        stroke={matchScore >= 70 ? 'var(--accent-emerald)' : matchScore >= 40 ? 'var(--accent-amber)' : 'var(--accent-rose)'}
                        strokeWidth="8"
                        strokeDasharray={`${(matchScore / 100) * 314} 314`}
                        strokeLinecap="round"
                        transform="rotate(-90 60 60)"
                      />
                    </svg>
                    <div className="match-gauge-value">{matchScore}%</div>
                  </div>
                  {artifact?.match_explanation && (
                    <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', lineHeight: 1.6 }}>
                      {artifact.match_explanation}
                    </p>
                  )}
                </div>

                {artifact && (artifact.matched_skills.length > 0 || artifact.missing_skills.length > 0 || artifact.weak_skills.length > 0) && (
                  <div className="skills-section mt-md">
                    {artifact.matched_skills.length > 0 && (
                      <div className="skill-group">
                        <span className="skill-group-label">Matched Skills</span>
                        <div className="skill-tags">
                          {artifact.matched_skills.map((skill) => <span key={skill} className="skill-tag matched">{skill}</span>)}
                        </div>
                      </div>
                    )}
                    {artifact.missing_skills.length > 0 && (
                      <div className="skill-group mt-md">
                        <span className="skill-group-label">Missing Skills</span>
                        <div className="skill-tags">
                          {artifact.missing_skills.map((skill) => <span key={skill} className="skill-tag missing">{skill}</span>)}
                        </div>
                      </div>
                    )}
                    {artifact.weak_skills.length > 0 && (
                      <div className="skill-group mt-md">
                        <span className="skill-group-label">Weakly Represented</span>
                        <div className="skill-tags">
                          {artifact.weak_skills.map((skill) => <span key={skill} className="skill-tag weak">{skill}</span>)}
                        </div>
                      </div>
                    )}
                  </div>
                )}
              </div>
            </motion.div>
          )}

          {artifact && (artifact.tailored_resume_text || artifact.cover_letter_text) && (
            <motion.div initial={{ opacity: 0, y: 15 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }} className="glass section-card">
              <div className="section-card-header">
                <div className="tab-bar">
                  <button className={`tab-btn ${artifactTab === 'resume' ? 'active' : ''}`} onClick={() => setArtifactTab('resume')}>
                    Tailored Resume
                  </button>
                  <button className={`tab-btn ${artifactTab === 'cover_letter' ? 'active' : ''}`} onClick={() => setArtifactTab('cover_letter')}>
                    Cover Letter
                  </button>
                </div>
              </div>
              <div className="section-card-body">
                {artifactTab === 'resume' ? (
                  artifact.tailored_resume_text ? (
                    <div className="artifact-content">
                      <div className="artifact-actions"><CopyButton text={artifact.tailored_resume_text} /></div>
                      <pre className="artifact-text">{artifact.tailored_resume_text}</pre>
                    </div>
                  ) : <p className="text-muted" style={{ fontSize: '0.85rem' }}>No tailored resume generated yet.</p>
                ) : (
                  artifact.cover_letter_text ? (
                    <div className="artifact-content">
                      <div className="artifact-actions"><CopyButton text={artifact.cover_letter_text} /></div>
                      <pre className="artifact-text">{artifact.cover_letter_text}</pre>
                    </div>
                  ) : <p className="text-muted" style={{ fontSize: '0.85rem' }}>No cover letter generated yet.</p>
                )}
              </div>
            </motion.div>
          )}

          <motion.div initial={{ opacity: 0, y: 15 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }} className="glass section-card">
            <div className="section-card-header">
              <h2><FileText size={18} className="section-icon" /> Job Description</h2>
            </div>
            <div className="section-card-body">
              <pre className="jd-text">{job.description}</pre>
            </div>
          </motion.div>
        </div>

        <div className="flex-col gap-lg">
          {application ? (
            <>
              <motion.div initial={{ opacity: 0, y: 15 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.15 }} className="glass section-card">
                <div className="section-card-header">
                  <h2><BarChart3 size={18} className="section-icon" /> Update Status</h2>
                </div>
                <div className="section-card-body flex-col gap-md">
                  <div className="form-group">
                    <label className="form-label">Status</label>
                    <div className="select-wrapper">
                      <select className="neu-input" value={statusValue} onChange={(event) => setStatusValue(event.target.value)}>
                        {ALLOWED_STATUSES.map((status) => <option key={status} value={status}>{status}</option>)}
                      </select>
                      <ChevronDown className="select-chevron" size={16} />
                    </div>
                  </div>
                  <div className="form-group">
                    <label className="form-label">Note (optional)</label>
                    <input
                      type="text"
                      className="neu-input"
                      value={statusNote}
                      onChange={(event) => setStatusNote(event.target.value)}
                      placeholder="e.g. Recruiter emailed me"
                    />
                  </div>
                  <button className="btn-primary" onClick={handleStatusSave} disabled={saving || statusValue === application.status} style={{ justifyContent: 'center' }}>
                    {saving ? <><Loader2 className="spinner" size={14} /> Saving...</> : 'Save Status'}
                  </button>
                </div>
              </motion.div>

              <motion.div initial={{ opacity: 0, y: 15 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.25 }} className="glass section-card">
                <div className="section-card-header">
                  <h2><Clock size={18} className="section-icon" /> Timeline</h2>
                </div>
                <div className="section-card-body">
                  {events.length === 0 ? (
                    <p className="text-muted" style={{ fontSize: '0.85rem' }}>No events recorded yet.</p>
                  ) : (
                    <div className="timeline">
                      {events.map((event) => {
                        const Icon = EVENT_ICONS[event.event_type] || Clock;
                        return (
                          <div key={event.id} className="timeline-item">
                            <div className="timeline-dot" style={{ color: STATUS_COLORS[event.status] || 'var(--text-muted)' }}>
                              <Icon size={14} />
                            </div>
                            <div className="timeline-content">
                              <div className="timeline-title">
                                {event.event_type.replace(/_/g, ' ')}
                                <span className="timeline-status" style={{ color: STATUS_COLORS[event.status] || 'var(--text-muted)' }}>
                                  {event.status}
                                </span>
                              </div>
                              {event.message && <p className="timeline-message">{event.message}</p>}
                              <span className="timeline-time">{formatDate(event.created_at)}</span>
                            </div>
                          </div>
                        );
                      })}
                    </div>
                  )}
                </div>
              </motion.div>
            </>
          ) : (
            <motion.div initial={{ opacity: 0, y: 15 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.15 }} className="glass section-card">
              <div className="section-card-header">
                <h2><Zap size={18} className="section-icon" /> Prepare First</h2>
              </div>
              <div className="section-card-body flex-col gap-md">
                <p className="text-muted" style={{ fontSize: '0.85rem', lineHeight: 1.6 }}>
                  Generate the match analysis, tailored resume, and cover letter before any submission attempt.
                </p>
                <button className="btn-primary" onClick={handlePrepare} disabled={preparing} style={{ justifyContent: 'center' }}>
                  {preparing ? <><Loader2 className="spinner" size={14} /> Preparing...</> : <><Zap size={14} /> Prepare Application</>}
                </button>
              </div>
            </motion.div>
          )}
        </div>
      </div>
    </div>
  );
}
