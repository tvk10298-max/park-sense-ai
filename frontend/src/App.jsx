import { BrowserRouter, Routes, Route, NavLink } from 'react-router-dom'
import Dashboard   from './pages/Dashboard'
import Trends      from './pages/Trends'
import Enforcement from './pages/Enforcement'
import Predictions from './pages/Predictions'

export default function App() {
  return (
    <BrowserRouter>
      <div style={{ display: 'flex', flexDirection: 'column', height: '100vh', background: '#0F1E3C' }}>
        <nav style={{ display: 'flex', alignItems: 'center', gap: 8, padding: '0 20px', height: 52, background: '#0F1E3C', borderBottom: '1px solid #1E3A5F', flexShrink: 0 }}>
          <span style={{ color: '#60A5FA', fontWeight: 700, fontSize: 16, marginRight: 20 }}>🅿 ParkSense AI</span>
          {[
            { to: '/',            label: '🗺 Heatmap' },
            { to: '/trends',      label: '📈 Trends' },
            { to: '/enforcement', label: '👮 Enforcement' },
            { to: '/predictions', label: '🔮 Predictions' },
          ].map(({ to, label }) => (
            <NavLink key={to} to={to} end={to === '/'} style={({ isActive }) => ({ color: isActive ? '#60A5FA' : '#94A3B8', textDecoration: 'none', fontSize: 13, padding: '4px 12px', borderRadius: 6, background: isActive ? 'rgba(96,165,250,0.15)' : 'transparent' })}>
              {label}
            </NavLink>
          ))}
        </nav>
        <div style={{ flex: 1, overflow: 'hidden' }}>
          <Routes>
            <Route path='/'            element={<Dashboard />} />
            <Route path='/trends'      element={<Trends />} />
            <Route path='/enforcement' element={<Enforcement />} />
            <Route path='/predictions' element={<Predictions />} />
          </Routes>
        </div>
      </div>
    </BrowserRouter>
  )
}
