"use client";

import { motion } from "framer-motion";
import { Briefcase, Building, MapPin, Search, PlayCircle } from "lucide-react";

export default function JobsTracker() {
  const mockJobs = [
    { id: 1, title: "Senior AI Engineer", company: "Anthropic", location: "Remote", status: "New", score: 92, source: "LinkedIn" },
    { id: 2, title: "Full Stack Developer", company: "Stripe", location: "San Francisco, CA", status: "Applied", score: 88, source: "Indeed" },
    { id: 3, title: "Backend Engineer", company: "Meta", location: "Remote", status: "Skipped", score: 45, source: "LinkedIn" },
  ];

  return (
    <div className="max-w-6xl mx-auto space-y-8">
      <header className="flex justify-between items-end">
        <div>
          <h1 className="text-3xl font-bold text-slate-800">Job Tracker</h1>
          <p className="text-slate-500 mt-1">Review scraped jobs and run the LangGraph automation.</p>
        </div>
        
        <div className="flex gap-3">
          <button className="bg-white border border-slate-200 hover:bg-slate-50 text-slate-700 px-5 py-2.5 rounded-xl font-medium transition-all shadow-sm flex items-center gap-2">
            <Search className="w-4 h-4" /> Scrape New Jobs
          </button>
          <button className="bg-indigo-600 hover:bg-indigo-700 text-white px-5 py-2.5 rounded-xl font-medium transition-all shadow-sm flex items-center gap-2">
            <PlayCircle className="w-4 h-4" /> Run Automation Queue
          </button>
        </div>
      </header>

      <div className="glass rounded-2xl overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-slate-50/50 border-b border-slate-100">
                <th className="p-4 font-medium text-slate-500 text-sm">Role & Company</th>
                <th className="p-4 font-medium text-slate-500 text-sm">Location</th>
                <th className="p-4 font-medium text-slate-500 text-sm">Source</th>
                <th className="p-4 font-medium text-slate-500 text-sm">Match Score</th>
                <th className="p-4 font-medium text-slate-500 text-sm">Status</th>
                <th className="p-4 font-medium text-slate-500 text-sm text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {mockJobs.map((job, idx) => (
                <motion.tr 
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: idx * 0.1 }}
                  key={job.id} 
                  className="hover:bg-white/50 transition-colors group"
                >
                  <td className="p-4">
                    <div className="font-bold text-slate-800 flex items-center gap-2">
                      <Briefcase className="w-4 h-4 text-slate-400" /> {job.title}
                    </div>
                    <div className="text-sm text-slate-500 flex items-center gap-2 mt-1">
                      <Building className="w-4 h-4 text-slate-400" /> {job.company}
                    </div>
                  </td>
                  <td className="p-4 text-slate-600 flex items-center gap-2 mt-3">
                    <MapPin className="w-4 h-4 text-slate-400" /> {job.location}
                  </td>
                  <td className="p-4">
                    <span className="px-2.5 py-1 bg-slate-100 text-slate-600 rounded-lg text-xs font-medium border border-slate-200">
                      {job.source}
                    </span>
                  </td>
                  <td className="p-4">
                    <div className="flex items-center gap-2">
                      <div className="w-full bg-slate-100 rounded-full h-1.5 w-16">
                        <div 
                          className={`h-1.5 rounded-full ${job.score >= 70 ? 'bg-emerald-500' : 'bg-rose-500'}`} 
                          style={{ width: `${job.score}%` }}
                        ></div>
                      </div>
                      <span className={`text-sm font-bold ${job.score >= 70 ? 'text-emerald-600' : 'text-rose-600'}`}>{job.score}%</span>
                    </div>
                  </td>
                  <td className="p-4">
                    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border
                      ${job.status === 'New' ? 'bg-blue-50 text-blue-700 border-blue-200' : 
                        job.status === 'Applied' ? 'bg-emerald-50 text-emerald-700 border-emerald-200' : 
                        'bg-slate-100 text-slate-600 border-slate-200'}`}>
                      {job.status}
                    </span>
                  </td>
                  <td className="p-4 text-right">
                    <button className="text-sm font-medium text-indigo-600 hover:text-indigo-700 opacity-0 group-hover:opacity-100 transition-opacity">
                      View Details
                    </button>
                  </td>
                </motion.tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
