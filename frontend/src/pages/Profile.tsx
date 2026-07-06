import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { User, Mail, FileText, Save, Loader2 } from 'lucide-react';
import api from '../lib/api';
import toast from 'react-hot-toast';

export default function Profile() {
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [fullName, setFullName] = useState('');
  const [email, setEmail] = useState('');
  const [resumeText, setResumeText] = useState('');

  useEffect(() => {
    const fetchProfile = async () => {
      try {
        const res = await api.get('/profile/');
        setFullName(res.data.full_name || '');
        setEmail(res.data.email || '');
        setResumeText(res.data.resume_text || '');
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
        <motion.h1
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
        >
          My Profile
        </motion.h1>
        <motion.p
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.1 }}
        >
          Manage your details and base resume for AI optimization.
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

      {/* Resume Content */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.25 }}
        className="glass section-card"
      >
        <div className="section-card-header">
          <h2>
            <FileText size={18} className="section-icon" />
            Base Resume Content
          </h2>
          <p>
            Paste your entire resume here. The AI will extract your skills and experience to optimize applications.
          </p>
        </div>
        <div className="section-card-body">
          <textarea
            className="neu-textarea"
            rows={15}
            value={resumeText}
            onChange={(e) => setResumeText(e.target.value)}
            placeholder="Paste your resume content here..."
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
        <button
          onClick={handleSave}
          disabled={saving}
          className="btn-primary"
        >
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
