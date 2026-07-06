import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import {
  Briefcase,
  Building,
  MapPin,
  Search,
  PlayCircle,
  Loader2,
  ExternalLink,
  ChevronRight,
} from 'lucide-react';
import { useJobs, Job } from '../context/JobsContext';

const cardVariants = {
  hidden: { opacity: 0, y: 20, scale: 0.95 },
  show: { opacity: 1, y: 0, scale: 1 },
};

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

export default function Jobs() {
  const { jobs, isLoadingJobs, isScraping, applyingJobId, fetchJobs, scrapeJobs, applyToJob } =
    useJobs();
  const [keyword, setKeyword] = useState('Software Engineer');
  const [location, setLocation] = useState('Remote');

  useEffect(() => {
    fetchJobs();
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  const handleScrape = (e: React.FormEvent) => {
    e.preventDefault();
    if (!keyword.trim()) return;
    scrapeJobs(keyword.trim(), location.trim());
  };

  return (
    <div className="flex-col gap-xl">
      {/* Header */}
      <div className="page-header">
        <motion.h1
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
        >
          Job Tracker
        </motion.h1>
        <motion.p
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.1 }}
        >
          Search for jobs and let the AI automation handle the rest.
        </motion.p>
      </div>

      {/* Scrape Form */}
      <motion.form
        initial={{ opacity: 0, y: 15 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.15 }}
        onSubmit={handleScrape}
        className="scrape-bar"
      >
        <div className="form-group">
          <label className="form-label">Job Title / Keyword</label>
          <input
            type="text"
            className="neu-input"
            value={keyword}
            onChange={(e) => setKeyword(e.target.value)}
            placeholder="e.g. AI Engineer, Data Scientist"
            required
          />
        </div>
        <div className="form-group">
          <label className="form-label">Location</label>
          <input
            type="text"
            className="neu-input"
            value={location}
            onChange={(e) => setLocation(e.target.value)}
            placeholder="e.g. Remote, San Francisco"
          />
        </div>
        <button type="submit" className="btn-primary" disabled={isScraping} style={{ height: 48, whiteSpace: 'nowrap' }}>
          {isScraping ? (
            <>
              <Loader2 className="spinner" size={16} />
              Crawling...
            </>
          ) : (
            <>
              <Search size={16} />
              Scrape Jobs
            </>
          )}
        </button>
      </motion.form>

      {/* Jobs Grid */}
      {isLoadingJobs ? (
        <div className="loading-screen">
          <Loader2 className="spinner" size={24} />
          <span>Loading jobs...</span>
        </div>
      ) : jobs.length === 0 ? (
        <div className="empty-state">
          <Briefcase className="empty-state-icon" />
          <p>No jobs found. Enter a keyword above and click "Scrape Jobs" to start.</p>
        </div>
      ) : (
        <motion.div
          className="jobs-grid"
          initial="hidden"
          animate="show"
          variants={{ show: { transition: { staggerChildren: 0.06 } } }}
        >
          {jobs.map((job: Job) => (
            <motion.div key={job.id} variants={cardVariants} className="glass-card job-card">
              <Link to={`/jobs/${job.id}`} className="job-card-link">
                <div className="job-card-header">
                  <div>
                    <div className="job-title">{job.title}</div>
                    <div className="job-company">
                      <Building size={14} />
                      {job.company}
                    </div>
                  </div>
                  <div className="flex-col gap-sm" style={{ alignItems: 'flex-end' }}>
                    <span className="source-badge">{job.source}</span>
                    {job.application && (
                      <span
                        className="status-badge"
                        style={{ '--badge-color': STATUS_COLORS[job.application.status] || 'var(--text-muted)' } as React.CSSProperties}
                      >
                        {job.application.status}
                        {job.application.match_score !== null && ` · ${job.application.match_score}%`}
                      </span>
                    )}
                  </div>
                </div>

                <div className="job-meta">
                  <span className="job-meta-item">
                    <MapPin size={14} />
                    {job.location || 'Remote'}
                  </span>
                  <span className="job-meta-item" style={{ marginLeft: 'auto', color: 'var(--accent-indigo)' }}>
                    View Details <ChevronRight size={14} />
                  </span>
                </div>
              </Link>

              <div className="job-card-actions">
                {job.url && (
                  <a
                    href={job.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="btn-ghost"
                    style={{ fontSize: '0.78rem', padding: '6px 12px' }}
                    onClick={(e) => e.stopPropagation()}
                  >
                    <ExternalLink size={13} />
                    Posting
                  </a>
                )}
                <button
                  onClick={(e) => {
                    e.preventDefault();
                    e.stopPropagation();
                    applyToJob(job.id);
                  }}
                  disabled={applyingJobId === job.id}
                  className="btn-primary"
                  style={{ fontSize: '0.78rem', padding: '6px 14px' }}
                >
                  {applyingJobId === job.id ? (
                    <>
                      <Loader2 className="spinner" size={13} />
                      Preparing...
                    </>
                  ) : (
                    <>
                      <PlayCircle size={13} />
                      Prepare
                    </>
                  )}
                </button>
              </div>
            </motion.div>
          ))}
        </motion.div>
      )}
    </div>
  );
}
