"use client";

import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { Briefcase, FileText, Send, XCircle, Trophy, BarChart3, Loader2 } from "lucide-react";
import api from "@/lib/api";

const container = {
  hidden: { opacity: 0 },
  show: {
    opacity: 1,
    transition: {
      staggerChildren: 0.1
    }
  }
};

const item = {
  hidden: { opacity: 0, y: 20 },
  show: { opacity: 1, y: 0 }
};

export default function Home() {
  const [stats, setStats] = useState({
    Total: 0,
    Pending: 0,
    Applied: 0,
    Rejected: 0,
    Interview: 0,
    Offer: 0
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const res = await api.get("/jobs/stats");
        setStats(res.data);
      } catch (err) {
        console.error("Failed to fetch stats", err);
      } finally {
        setLoading(false);
      }
    };
    fetchStats();
  }, []);

  const statCards = [
    { title: "Total Scraped", value: stats.Total.toString(), icon: Briefcase, color: "text-blue-500", bg: "bg-blue-50" },
    { title: "Applications Sent", value: stats.Applied.toString(), icon: Send, color: "text-indigo-500", bg: "bg-indigo-50" },
    { title: "Pending", value: stats.Pending.toString(), icon: FileText, color: "text-amber-500", bg: "bg-amber-50" },
    { title: "Interviews", value: stats.Interview.toString(), icon: BarChart3, color: "text-emerald-500", bg: "bg-emerald-50" },
    { title: "Offers", value: stats.Offer.toString(), icon: Trophy, color: "text-yellow-500", bg: "bg-yellow-50" },
    { title: "Rejected", value: stats.Rejected.toString(), icon: XCircle, color: "text-rose-500", bg: "bg-rose-50" },
  ];

  return (
    <div className="max-w-6xl mx-auto space-y-8">
      <header>
        <h1 className="text-3xl font-bold text-slate-800">Dashboard</h1>
        <p className="text-slate-500 mt-1">Welcome back. Here is your AI application overview.</p>
      </header>

      {loading ? (
        <div className="flex justify-center items-center h-64 text-slate-500">
          <Loader2 className="w-6 h-6 animate-spin mr-2" /> Loading stats...
        </div>
      ) : (
        <motion.div 
          variants={container}
          initial="hidden"
          animate="show"
          className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6"
        >
          {statCards.map((stat, idx) => (
            <motion.div key={idx} variants={item} className="glass p-6 rounded-2xl flex items-start gap-4">
              <div className={`p-3 rounded-xl ${stat.bg}`}>
                <stat.icon className={`w-6 h-6 ${stat.color}`} />
              </div>
              <div>
                <p className="text-sm font-medium text-slate-500">{stat.title}</p>
                <h3 className="text-2xl font-bold text-slate-800 mt-1">{stat.value}</h3>
              </div>
            </motion.div>
          ))}
        </motion.div>
      )}

      <motion.div 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.4 }}
        className="glass rounded-2xl p-8 mt-8"
      >
        <h2 className="text-xl font-bold text-slate-800 mb-4">Recent Activity</h2>
        <div className="space-y-4">
          <div className="flex items-center gap-4 p-4 rounded-xl hover:bg-slate-50/50 transition border border-transparent hover:border-slate-100">
            <div className="w-2 h-2 rounded-full bg-indigo-500"></div>
            <p className="text-sm text-slate-600 flex-1">AI Agent successfully submitted application to <span className="font-semibold text-slate-800">Google</span></p>
            <span className="text-xs text-slate-400 font-medium">Just now</span>
          </div>
          <div className="flex items-center gap-4 p-4 rounded-xl hover:bg-slate-50/50 transition border border-transparent hover:border-slate-100">
            <div className="w-2 h-2 rounded-full bg-emerald-500"></div>
            <p className="text-sm text-slate-600 flex-1">Scraper found <span className="font-semibold text-slate-800">14 new jobs</span> matching your criteria</p>
            <span className="text-xs text-slate-400 font-medium">2h ago</span>
          </div>
          <div className="flex items-center gap-4 p-4 rounded-xl hover:bg-slate-50/50 transition border border-transparent hover:border-slate-100">
            <div className="w-2 h-2 rounded-full bg-amber-500"></div>
            <p className="text-sm text-slate-600 flex-1">Resume Agent updated your profile for <span className="font-semibold text-slate-800">Senior AI Engineer</span></p>
            <span className="text-xs text-slate-400 font-medium">5h ago</span>
          </div>
        </div>
      </motion.div>
    </div>
  );
}
