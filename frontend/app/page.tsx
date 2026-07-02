"use client";

import { motion } from "framer-motion";
import { Briefcase, CheckCircle, Clock, XCircle, TrendingUp } from "lucide-react";

export default function Dashboard() {
  const stats = [
    { title: "Jobs Applied", value: "24", icon: Briefcase, color: "text-indigo-600", bg: "bg-indigo-100" },
    { title: "Interviews", value: "3", icon: CheckCircle, color: "text-emerald-600", bg: "bg-emerald-100" },
    { title: "Pending", value: "15", icon: Clock, color: "text-amber-600", bg: "bg-amber-100" },
    { title: "Rejected", value: "6", icon: XCircle, color: "text-rose-600", bg: "bg-rose-100" },
  ];

  return (
    <div className="max-w-6xl mx-auto space-y-8">
      <header className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-slate-800">Welcome back, Harkirat!</h1>
          <p className="text-slate-500 mt-1">Here is what your AI Agent has been up to.</p>
        </div>
        <button className="bg-indigo-600 hover:bg-indigo-700 text-white px-6 py-2.5 rounded-xl font-medium transition-all shadow-sm shadow-indigo-200">
          Start Auto-Apply
        </button>
      </header>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {stats.map((stat, idx) => (
          <motion.div 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: idx * 0.1 }}
            key={stat.title} 
            className="glass rounded-2xl p-6 flex items-center gap-4 hover:-translate-y-1 transition-all-ease cursor-default"
          >
            <div className={`w-12 h-12 rounded-xl flex items-center justify-center ${stat.bg}`}>
              <stat.icon className={`w-6 h-6 ${stat.color}`} />
            </div>
            <div>
              <p className="text-sm font-medium text-slate-500">{stat.title}</p>
              <h3 className="text-2xl font-bold text-slate-800">{stat.value}</h3>
            </div>
          </motion.div>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Recent Applications */}
        <div className="lg:col-span-2 glass rounded-2xl p-6">
          <div className="flex justify-between items-center mb-6">
            <h2 className="text-xl font-bold text-slate-800">Recent Applications</h2>
            <button className="text-sm font-medium text-indigo-600 hover:text-indigo-700">View All</button>
          </div>
          
          <div className="space-y-4">
            {[
              { role: "Backend Engineer", company: "Google", status: "Applied", time: "2 hours ago" },
              { role: "AI Software Engineer", company: "OpenAI", status: "Interview", time: "1 day ago" },
              { role: "Full Stack Developer", company: "Stripe", status: "Applied", time: "2 days ago" },
            ].map((app, i) => (
              <motion.div 
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.3 + (i * 0.1) }}
                key={i} 
                className="flex items-center justify-between p-4 rounded-xl border border-slate-100 hover:border-indigo-100 hover:bg-indigo-50/50 transition-colors"
              >
                <div>
                  <h4 className="font-bold text-slate-800">{app.role}</h4>
                  <p className="text-sm text-slate-500">{app.company}</p>
                </div>
                <div className="text-right">
                  <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium 
                    ${app.status === 'Applied' ? 'bg-amber-100 text-amber-800' : 'bg-emerald-100 text-emerald-800'}`}>
                    {app.status}
                  </span>
                  <p className="text-xs text-slate-400 mt-1">{app.time}</p>
                </div>
              </motion.div>
            ))}
          </div>
        </div>

        {/* Analytics Card */}
        <div className="glass rounded-2xl p-6">
          <h2 className="text-xl font-bold text-slate-800 mb-6">Match Analytics</h2>
          <div className="space-y-6">
            <div>
              <div className="flex justify-between text-sm mb-2">
                <span className="font-medium text-slate-600">Average Match Score</span>
                <span className="font-bold text-emerald-600">86%</span>
              </div>
              <div className="w-full bg-slate-100 rounded-full h-2">
                <div className="bg-emerald-500 h-2 rounded-full" style={{ width: '86%' }}></div>
              </div>
            </div>
            
            <div className="pt-4 border-t border-slate-100">
              <h4 className="text-sm font-medium text-slate-600 mb-3 flex items-center gap-2">
                <TrendingUp className="w-4 h-4 text-indigo-500"/> Top Missing Skills
              </h4>
              <div className="flex flex-wrap gap-2">
                <span className="px-3 py-1 bg-slate-100 text-slate-600 rounded-lg text-xs font-medium">Kubernetes</span>
                <span className="px-3 py-1 bg-slate-100 text-slate-600 rounded-lg text-xs font-medium">AWS</span>
                <span className="px-3 py-1 bg-slate-100 text-slate-600 rounded-lg text-xs font-medium">Terraform</span>
              </div>
              <p className="text-xs text-slate-500 mt-3">
                Learning <strong className="text-indigo-600">Kubernetes</strong> would unlock 32% more jobs.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
