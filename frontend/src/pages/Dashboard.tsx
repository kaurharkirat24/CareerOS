import { useEffect } from 'react';
import { motion } from 'framer-motion';
import { Briefcase, Send, FileText, BarChart3, Trophy, XCircle, Loader2 } from 'lucide-react';
import { useJobs } from '../context/JobsContext';

const container = {
  hidden: { opacity: 0 },
  show: {
    opacity: 1,
    transition: { staggerChildren: 0.08 },
  },
};

const item = {
  hidden: { opacity: 0, y: 20, scale: 0.95 },
  show: { opacity: 1, y: 0, scale: 1 },
};

export default function Dashboard() {
  const { stats, isLoadingStats, fetchStats } = useJobs();

  useEffect(() => {
    fetchStats();
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  const statCards = [
    { title: 'Total Applications', value: stats.Total, icon: Briefcase, color: 'indigo' },
    { title: 'Applied', value: stats.Applied, icon: Send, color: 'violet' },
    { title: 'Pending', value: stats.Pending, icon: FileText, color: 'amber' },
    { title: 'Interviews', value: stats.Interview, icon: BarChart3, color: 'emerald' },
    { title: 'Offers', value: stats.Offer, icon: Trophy, color: 'cyan' },
    { title: 'Rejected', value: stats.Rejected, icon: XCircle, color: 'rose' },
  ];

  return (
    <div className="flex-col gap-xl">
      <div className="page-header">
        <motion.h1
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.4 }}
        >
          Dashboard
        </motion.h1>
        <motion.p
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.4, delay: 0.1 }}
        >
          Welcome back. Here is your AI application overview.
        </motion.p>
      </div>

      {isLoadingStats ? (
        <div className="loading-screen">
          <Loader2 className="spinner" size={24} />
          <span>Loading stats...</span>
        </div>
      ) : (
        <motion.div
          className="stats-grid"
          variants={container}
          initial="hidden"
          animate="show"
        >
          {statCards.map((stat, idx) => (
            <motion.div
              key={idx}
              variants={item}
              className="glass-card stat-card"
            >
              <div className={`stat-icon-wrap ${stat.color}`}>
                <stat.icon size={22} />
              </div>
              <div>
                <div className="stat-label">{stat.title}</div>
                <div className="stat-value">{stat.value}</div>
              </div>
            </motion.div>
          ))}
        </motion.div>
      )}

      {/* Recent Activity */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.5 }}
        className="glass section-card"
      >
        <div className="section-card-header">
          <h2>Recent Activity</h2>
        </div>
        <div className="section-card-body">
          <div className="empty-state" style={{ minHeight: 120 }}>
            <p style={{ fontSize: '0.85rem' }}>
              No recent activity yet. Start by scraping jobs from the Job Tracker page.
            </p>
          </div>
        </div>
      </motion.div>
    </div>
  );
}
