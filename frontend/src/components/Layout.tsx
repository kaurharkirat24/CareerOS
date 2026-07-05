import { NavLink, Outlet, useNavigate } from 'react-router-dom';
import { Home, Briefcase, User, LogOut } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

export default function Layout() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <>
      {/* Animated background */}
      <div className="app-background">
        <div className="floating-orb" />
        <div className="floating-orb" />
        <div className="floating-orb" />
      </div>

      <div className="app-layout">
        {/* Sidebar */}
        <aside className="sidebar">
          <div>
            <div className="sidebar-logo">
              <div className="sidebar-logo-icon">C</div>
              <span className="sidebar-logo-text">CareerOS</span>
            </div>

            <nav className="sidebar-nav">
              <NavLink
                to="/"
                end
                className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
              >
                <Home className="nav-icon" />
                Dashboard
              </NavLink>
              <NavLink
                to="/jobs"
                className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
              >
                <Briefcase className="nav-icon" />
                Job Tracker
              </NavLink>
              <NavLink
                to="/profile"
                className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
              >
                <User className="nav-icon" />
                My Profile
              </NavLink>
            </nav>
          </div>

          <div className="flex-col gap-sm">
            {user && (
              <div style={{ padding: '12px 16px', fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                {user.full_name || user.email}
              </div>
            )}
            <button onClick={handleLogout} className="nav-link" style={{ width: '100%', background: 'none', color: 'var(--text-secondary)' }}>
              <LogOut className="nav-icon" />
              Logout
            </button>
          </div>
        </aside>

        {/* Main content */}
        <main className="main-content">
          <Outlet />
        </main>
      </div>
    </>
  );
}
