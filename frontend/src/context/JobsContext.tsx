import { createContext, useContext, useReducer, ReactNode, useCallback } from 'react';
import api from '../lib/api';
import toast from 'react-hot-toast';

export interface Job {
  id: number;
  title: string;
  company: string;
  location: string | null;
  source: string;
  url: string;
  description: string;
}

interface Stats {
  Total: number;
  Pending: number;
  Applied: number;
  Rejected: number;
  Interview: number;
  Offer: number;
}

interface JobsState {
  jobs: Job[];
  stats: Stats;
  isLoadingJobs: boolean;
  isLoadingStats: boolean;
  isScraping: boolean;
  applyingJobId: number | null;
}

type JobsAction =
  | { type: 'SET_JOBS'; payload: Job[] }
  | { type: 'SET_STATS'; payload: Stats }
  | { type: 'SET_LOADING_JOBS'; payload: boolean }
  | { type: 'SET_LOADING_STATS'; payload: boolean }
  | { type: 'SET_SCRAPING'; payload: boolean }
  | { type: 'SET_APPLYING'; payload: number | null };

const defaultStats: Stats = {
  Total: 0,
  Pending: 0,
  Applied: 0,
  Rejected: 0,
  Interview: 0,
  Offer: 0,
};

const initialState: JobsState = {
  jobs: [],
  stats: defaultStats,
  isLoadingJobs: false,
  isLoadingStats: false,
  isScraping: false,
  applyingJobId: null,
};

function jobsReducer(state: JobsState, action: JobsAction): JobsState {
  switch (action.type) {
    case 'SET_JOBS':
      return { ...state, jobs: action.payload, isLoadingJobs: false };
    case 'SET_STATS':
      return { ...state, stats: action.payload, isLoadingStats: false };
    case 'SET_LOADING_JOBS':
      return { ...state, isLoadingJobs: action.payload };
    case 'SET_LOADING_STATS':
      return { ...state, isLoadingStats: action.payload };
    case 'SET_SCRAPING':
      return { ...state, isScraping: action.payload };
    case 'SET_APPLYING':
      return { ...state, applyingJobId: action.payload };
    default:
      return state;
  }
}

interface JobsContextType extends JobsState {
  fetchJobs: () => Promise<void>;
  fetchStats: () => Promise<void>;
  scrapeJobs: (keyword: string, location: string, maxResults?: number) => Promise<void>;
  applyToJob: (jobId: number) => Promise<void>;
}

const JobsContext = createContext<JobsContextType | undefined>(undefined);

export function JobsProvider({ children }: { children: ReactNode }) {
  const [state, dispatch] = useReducer(jobsReducer, initialState);

  const fetchJobs = useCallback(async () => {
    if (state.isLoadingJobs) return;
    dispatch({ type: 'SET_LOADING_JOBS', payload: true });
    try {
      const res = await api.get('/jobs/');
      dispatch({ type: 'SET_JOBS', payload: res.data });
    } catch {
      dispatch({ type: 'SET_LOADING_JOBS', payload: false });
    }
  }, [state.isLoadingJobs]);

  const fetchStats = useCallback(async () => {
    if (state.isLoadingStats) return;
    dispatch({ type: 'SET_LOADING_STATS', payload: true });
    try {
      const res = await api.get('/jobs/stats');
      dispatch({ type: 'SET_STATS', payload: res.data });
    } catch {
      dispatch({ type: 'SET_LOADING_STATS', payload: false });
    }
  }, [state.isLoadingStats]);

  const scrapeJobs = useCallback(async (keyword: string, location: string, maxResults = 5) => {
    dispatch({ type: 'SET_SCRAPING', payload: true });
    try {
      const res = await api.post('/jobs/scrape', {
        keyword,
        location,
        max_results: maxResults,
      });
      toast.success(res.data.message);
      // Refresh jobs list after scraping
      const jobsRes = await api.get('/jobs/');
      dispatch({ type: 'SET_JOBS', payload: jobsRes.data });
    } catch (err: unknown) {
      const message = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail || 'Failed to scrape jobs.';
      toast.error(message);
    } finally {
      dispatch({ type: 'SET_SCRAPING', payload: false });
    }
  }, []);

  const applyToJob = useCallback(async (jobId: number) => {
    dispatch({ type: 'SET_APPLYING', payload: jobId });
    try {
      const res = await api.post(`/jobs/${jobId}/apply`);
      toast.success(`Automation Complete! Status: ${res.data.status}`);
      // Refresh stats after applying
      const statsRes = await api.get('/jobs/stats');
      dispatch({ type: 'SET_STATS', payload: statsRes.data });
    } catch (err: unknown) {
      const message = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail || 'Application automation failed.';
      toast.error(message);
    } finally {
      dispatch({ type: 'SET_APPLYING', payload: null });
    }
  }, []);

  return (
    <JobsContext.Provider value={{ ...state, fetchJobs, fetchStats, scrapeJobs, applyToJob }}>
      {children}
    </JobsContext.Provider>
  );
}

export function useJobs() {
  const context = useContext(JobsContext);
  if (context === undefined) {
    throw new Error('useJobs must be used within a JobsProvider');
  }
  return context;
}
