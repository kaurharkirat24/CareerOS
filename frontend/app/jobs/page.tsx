"use client";

import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { Briefcase, Building, MapPin, Search, PlayCircle, Loader2 } from "lucide-react";
import api from "@/lib/api";
import toast from "react-hot-toast";

interface Job {
  id: number;
  title: string;
  company: string;
  location: string;
  source: string;
  url: string;
}

export default function JobsTracker() {
  const [jobs, setJobs] = useState<Job[]>([]);
  const [loading, setLoading] = useState(true);
  const [scraping, setScraping] = useState(false);
  const [applyingId, setApplyingId] = useState<number | null>(null);
  
  const fetchJobs = async () => {
    try {
      const res = await api.get("/jobs/");
      setJobs(res.data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchJobs();
  }, []);

  const handleScrape = async () => {
    setScraping(true);
    try {
      const res = await api.post("/jobs/scrape", {
        keyword: "Software Engineer", // Hardcoded for demo, could be an input
        location: "Remote",
        max_results: 3
      });
      toast.success(res.data.message);
      fetchJobs();
    } catch (err) {
      toast.error("Failed to scrape jobs.");
    } finally {
      setScraping(false);
    }
  };

  const handleApply = async (jobId: number) => {
    setApplyingId(jobId);
    try {
      const res = await api.post(`/jobs/${jobId}/apply`);
      toast.success(`Automation Complete! Status: ${res.data.status}`);
    } catch (err: any) {
      toast.error(`Application failed: ${err.response?.data?.detail || err.message}`);
    } finally {
      setApplyingId(null);
    }
  };

  return (
    <div className="max-w-6xl mx-auto space-y-8">
      <header className="flex justify-between items-end">
        <div>
          <h1 className="text-3xl font-bold text-slate-800">Job Tracker</h1>
          <p className="text-slate-500 mt-1">Review scraped jobs and run the LangGraph automation.</p>
        </div>
        
        <div className="flex gap-3">
          <button 
            onClick={handleScrape}
            disabled={scraping}
            className="bg-white border border-slate-200 hover:bg-slate-50 text-slate-700 px-5 py-2.5 rounded-xl font-medium transition-all shadow-sm flex items-center gap-2 disabled:opacity-50"
          >
            {scraping ? <Loader2 className="w-4 h-4 animate-spin" /> : <Search className="w-4 h-4" />} 
            {scraping ? "Crawling..." : "Scrape New Jobs"}
          </button>
        </div>
      </header>

      <div className="glass rounded-2xl overflow-hidden min-h-[400px]">
        {loading ? (
          <div className="flex justify-center items-center h-64 text-slate-500">
            <Loader2 className="w-6 h-6 animate-spin mr-2" /> Loading jobs...
          </div>
        ) : jobs.length === 0 ? (
          <div className="flex flex-col justify-center items-center h-64 text-slate-500">
            <Briefcase className="w-12 h-12 mb-4 text-slate-300" />
            <p>No jobs found. Click "Scrape New Jobs" to start.</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="bg-slate-50/50 border-b border-slate-100">
                  <th className="p-4 font-medium text-slate-500 text-sm">Role & Company</th>
                  <th className="p-4 font-medium text-slate-500 text-sm">Location</th>
                  <th className="p-4 font-medium text-slate-500 text-sm">Source</th>
                  <th className="p-4 font-medium text-slate-500 text-sm text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {jobs.map((job, idx) => (
                  <motion.tr 
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: idx * 0.05 }}
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
                      <MapPin className="w-4 h-4 text-slate-400" /> {job.location || "Remote"}
                    </td>
                    <td className="p-4">
                      <span className="px-2.5 py-1 bg-slate-100 text-slate-600 rounded-lg text-xs font-medium border border-slate-200">
                        {job.source}
                      </span>
                    </td>
                    <td className="p-4 text-right">
                      <button 
                        onClick={() => handleApply(job.id)}
                        disabled={applyingId === job.id}
                        className="text-sm font-medium bg-indigo-50 text-indigo-700 px-3 py-1.5 rounded-lg hover:bg-indigo-100 transition-colors flex items-center gap-1 ml-auto disabled:opacity-50"
                      >
                        {applyingId === job.id ? <Loader2 className="w-4 h-4 animate-spin" /> : <PlayCircle className="w-4 h-4" />}
                        {applyingId === job.id ? "Running AI..." : "Auto Apply"}
                      </button>
                    </td>
                  </motion.tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
