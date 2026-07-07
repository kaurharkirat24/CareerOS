import { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  User,
  Mail,
  FileText,
  Save,
  Loader2,
  Upload,
  CheckCircle2,
  X,
  ChevronDown,
  ChevronUp,
  Briefcase,
  Code,
  GraduationCap,
  Link as LinkIcon,
} from 'lucide-react';
import api from '../lib/api';
import toast from 'react-hot-toast';

interface ParsedProfile {
  summary: string;
  skills: string[];
  experience: { company: string; role: string; duration: string; bullets: string[] }[];
  projects: { name: string; description: string; technologies: string[]; bullets: string[] }[];
  education: { institution: string; degree: string; duration: string }[];
  links: string[];
  contact_name: string;
  contact_email: string;
  contact_phone: string;
}

export default function Profile() {
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [fullName, setFullName] = useState('');
  const [email, setEmail] = useState('');
  const [resumeText, setResumeText] = useState('');
  const [resumeFilePath, setResumeFilePath] = useState('');
  const [parsedProfile, setParsedProfile] = useState<ParsedProfile | null>(null);

  // Upload state
  const [uploading, setUploading] = useState(false);
  const [extractedText, setExtractedText] = useState('');
  const [showExtracted, setShowExtracted] = useState(false);
  const [confirming, setConfirming] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Profile sections expand
  const [profileExpanded, setProfileExpanded] = useState(false);

  useEffect(() => {
    const fetchProfile = async () => {
      try {
        const res = await api.get('/profile/');
        setFullName(res.data.full_name || '');
        setEmail(res.data.email || '');
        setResumeText(res.data.resume_text || '');
        setResumeFilePath(res.data.resume_file_path || '');
        if (res.data.parsed_profile) {
          setParsedProfile(res.data.parsed_profile);
        }
      } catch {
        // Handled by global interceptor
      } finally {
        setLoading(false);
      }
    };
    fetchProfile();
  }, []);

  const handleSave = async () => {
    setSaving(true);
    try {
      await api.put('/profile/', {
        full_name: fullName,
        resume_text: resumeText,
      });
      toast.success('Profile saved successfully!');
    } catch {
      toast.error('Failed to save profile.');
    } finally {
      setSaving(false);
    }
  };

  const handleUpload = async (file: File) => {
    setUploading(true);
    const formData = new FormData();
    formData.append('file', file);

    try {
      const res = await api.post('/profile/resume/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      setExtractedText(res.data.extracted_text);
      setResumeFilePath(res.data.file_path);
      setShowExtracted(true);
      toast.success(res.data.message);
    } catch (err: unknown) {
      const message =
        (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail ||
        'Failed to upload resume.';
      toast.error(message);
    } finally {
      setUploading(false);
    }
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) handleUpload(file);
    // Reset so the same file can be re-uploaded
    e.target.value = '';
  };

  const handleConfirmExtracted = async () => {
    if (!extractedText.trim()) return;
    setConfirming(true);
    try {
      const res = await api.post('/profile/resume/confirm', {
        resume_text: extractedText,
      });
      setResumeText(extractedText);
      setShowExtracted(false);
      setExtractedText('');
      if (res.data.parsed_profile) {
        setParsedProfile(res.data.parsed_profile);
      }
      toast.success(res.data.message);
    } catch {
      toast.error('Failed to save resume.');
    } finally {
      setConfirming(false);
    }
  };

  if (loading) {
    return (
      <div className="loading-screen">
        <Loader2 className="spinner" size={24} />
        <span>Loading profile...</span>
      </div>
    );
  }

  return (
    <div className="flex-col gap-xl" style={{ maxWidth: 800, margin: '0 auto' }}>
      <div className="page-header">
        <motion.h1 initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }}>
          My Profile
        </motion.h1>
        <motion.p
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.1 }}
        >
          Manage your details and upload your resume for AI optimization.
        </motion.p>
      </div>

      {/* Personal Details */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.15 }}
        className="glass section-card"
      >
        <div className="section-card-header">
          <h2>
            <User size={18} className="section-icon" />
            Personal Details
          </h2>
        </div>
        <div className="section-card-body">
          <div className="form-grid">
            <div className="form-group">
              <label className="form-label">Full Name</label>
              <div className="neu-input-icon">
                <User className="icon" />
                <input
                  type="text"
                  className="neu-input"
                  value={fullName}
                  onChange={(e) => setFullName(e.target.value)}
                  placeholder="Your full name"
                />
              </div>
            </div>
            <div className="form-group">
              <label className="form-label">Email (Read-Only)</label>
              <div className="neu-input-icon">
                <Mail className="icon" />
                <input
                  type="email"
                  className="neu-input"
                  value={email}
                  disabled
                  style={{ opacity: 0.5, cursor: 'not-allowed' }}
                />
              </div>
            </div>
          </div>
        </div>
      </motion.div>

      {/* Resume Upload */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
        className="glass section-card"
      >
        <div className="section-card-header">
          <h2>
            <Upload size={18} className="section-icon" />
            Upload Resume
          </h2>
          <p>Upload a PDF resume. The text will be extracted for you to review before saving.</p>
        </div>
        <div className="section-card-body flex-col gap-md">
          {/* Drop zone */}
          <div
            className="upload-zone"
            onClick={() => fileInputRef.current?.click()}
            onDragOver={(e) => { e.preventDefault(); e.currentTarget.classList.add('drag-over'); }}
            onDragLeave={(e) => e.currentTarget.classList.remove('drag-over')}
            onDrop={(e) => {
              e.preventDefault();
              e.currentTarget.classList.remove('drag-over');
              const file = e.dataTransfer.files[0];
              if (file) handleUpload(file);
            }}
          >
            <input
              ref={fileInputRef}
              type="file"
              accept=".pdf"
              onChange={handleFileSelect}
              style={{ display: 'none' }}
            />
            {uploading ? (
              <div className="upload-zone-content">
                <Loader2 className="spinner" size={32} />
                <span>Extracting text from PDF...</span>
              </div>
            ) : (
              <div className="upload-zone-content">
                <Upload size={32} style={{ opacity: 0.4 }} />
                <span>Click or drag a PDF file here to upload</span>
                <span className="upload-hint">Maximum 10 MB · PDF only</span>
              </div>
            )}
          </div>

          {resumeFilePath && !showExtracted && (
            <div className="upload-status">
              <CheckCircle2 size={14} style={{ color: 'var(--accent-emerald)' }} />
              <span>Resume on file</span>
            </div>
          )}

          {/* Extracted text review */}
          <AnimatePresence>
            {showExtracted && (
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto' }}
                exit={{ opacity: 0, height: 0 }}
                className="flex-col gap-md"
              >
                <div className="extracted-header">
                  <h3 style={{ fontSize: '0.9rem', fontWeight: 600 }}>
                    Extracted Text — Review & Edit
                  </h3>
                  <button
                    className="btn-ghost"
                    onClick={() => { setShowExtracted(false); setExtractedText(''); }}
                    style={{ padding: '4px 8px' }}
                  >
                    <X size={14} /> Cancel
                  </button>
                </div>
                <textarea
                  className="neu-textarea"
                  rows={16}
                  value={extractedText}
                  onChange={(e) => setExtractedText(e.target.value)}
                />
                <button
                  className="btn-primary"
                  onClick={handleConfirmExtracted}
                  disabled={confirming || !extractedText.trim()}
                  style={{ alignSelf: 'flex-end' }}
                >
                  {confirming ? (
                    <>
                      <Loader2 className="spinner" size={16} />
                      Saving & Parsing...
                    </>
                  ) : (
                    <>
                      <CheckCircle2 size={16} />
                      Confirm & Save Resume
                    </>
                  )}
                </button>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </motion.div>

      {/* Parsed Profile Sections */}
      {parsedProfile && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.25 }}
          className="glass section-card"
        >
          <div
            className="section-card-header"
            style={{ cursor: 'pointer' }}
            onClick={() => setProfileExpanded(!profileExpanded)}
          >
            <h2>
              <FileText size={18} className="section-icon" />
              Parsed Profile
              {profileExpanded ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
            </h2>
            <p>Structured data extracted from your resume by AI</p>
          </div>
          <AnimatePresence>
            {profileExpanded && (
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto' }}
                exit={{ opacity: 0, height: 0 }}
                className="section-card-body flex-col gap-lg"
              >
                {/* Summary */}
                {parsedProfile.summary && (
                  <div className="profile-section">
                    <h3 className="profile-section-title">
                      <User size={14} /> Summary
                    </h3>
                    <p className="profile-section-text">{parsedProfile.summary}</p>
                  </div>
                )}

                {/* Skills */}
                {parsedProfile.skills.length > 0 && (
                  <div className="profile-section">
                    <h3 className="profile-section-title">
                      <Code size={14} /> Skills
                    </h3>
                    <div className="skill-tags">
                      {parsedProfile.skills.map((s, i) => (
                        <span key={i} className="skill-tag matched">{s}</span>
                      ))}
                    </div>
                  </div>
                )}

                {/* Experience */}
                {parsedProfile.experience.length > 0 && (
                  <div className="profile-section">
                    <h3 className="profile-section-title">
                      <Briefcase size={14} /> Experience
                    </h3>
                    {parsedProfile.experience.map((exp, i) => (
                      <div key={i} className="profile-item">
                        <div className="profile-item-header">
                          <strong>{exp.role}</strong>
                          <span className="profile-item-meta">{exp.duration}</span>
                        </div>
                        <div className="profile-item-sub">{exp.company}</div>
                        <ul className="profile-bullets">
                          {exp.bullets.map((b, j) => <li key={j}>{b}</li>)}
                        </ul>
                      </div>
                    ))}
                  </div>
                )}

                {/* Projects */}
                {parsedProfile.projects.length > 0 && (
                  <div className="profile-section">
                    <h3 className="profile-section-title">
                      <Code size={14} /> Projects
                    </h3>
                    {parsedProfile.projects.map((proj, i) => (
                      <div key={i} className="profile-item">
                        <div className="profile-item-header">
                          <strong>{proj.name}</strong>
                        </div>
                        <div className="profile-item-sub">
                          {proj.technologies.join(', ')}
                        </div>
                        <ul className="profile-bullets">
                          {proj.bullets.map((b, j) => <li key={j}>{b}</li>)}
                        </ul>
                      </div>
                    ))}
                  </div>
                )}

                {/* Education */}
                {parsedProfile.education.length > 0 && (
                  <div className="profile-section">
                    <h3 className="profile-section-title">
                      <GraduationCap size={14} /> Education
                    </h3>
                    {parsedProfile.education.map((edu, i) => (
                      <div key={i} className="profile-item">
                        <div className="profile-item-header">
                          <strong>{edu.degree}</strong>
                          <span className="profile-item-meta">{edu.duration}</span>
                        </div>
                        <div className="profile-item-sub">{edu.institution}</div>
                      </div>
                    ))}
                  </div>
                )}

                {/* Links */}
                {parsedProfile.links.length > 0 && (
                  <div className="profile-section">
                    <h3 className="profile-section-title">
                      <LinkIcon size={14} /> Links
                    </h3>
                    <div className="flex-col gap-sm">
                      {parsedProfile.links.map((link, i) => (
                        <a
                          key={i}
                          href={link}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="profile-link"
                        >
                          {link}
                        </a>
                      ))}
                    </div>
                  </div>
                )}
              </motion.div>
            )}
          </AnimatePresence>
        </motion.div>
      )}

      {/* Raw Resume Text (manual fallback) */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3 }}
        className="glass section-card"
      >
        <div className="section-card-header">
          <h2>
            <FileText size={18} className="section-icon" />
            Resume Text
          </h2>
          <p>
            Your stored resume text. You can also paste or edit directly here.
          </p>
        </div>
        <div className="section-card-body">
          <textarea
            className="neu-textarea"
            rows={12}
            value={resumeText}
            onChange={(e) => setResumeText(e.target.value)}
            placeholder="Paste your resume content here or upload a PDF above..."
          />
        </div>
      </motion.div>

      {/* Save button */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.35 }}
        className="form-actions"
      >
        <button onClick={handleSave} disabled={saving} className="btn-primary">
          {saving ? (
            <>
              <Loader2 className="spinner" size={18} />
              Saving...
            </>
          ) : (
            <>
              <Save size={18} />
              Save Profile
            </>
          )}
        </button>
      </motion.div>
    </div>
  );
}
