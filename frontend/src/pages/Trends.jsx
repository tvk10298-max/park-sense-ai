import { useEffect, useState } from 'react'
import { Bar, Line } from 'react-chartjs-2'
import { Chart, CategoryScale, LinearScale, BarElement, LineElement, PointElement, Title, Tooltip, Legend } from 'chart.js'
import axios from 'axios'

Chart.register(CategoryScale, LinearScale, BarElement, LineElement, PointElement, Title, Tooltip, Legend)

const API = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export default function Trends() {
  const [data, setData]       = useState([])
  const [groupBy, setGroupBy] = useState('month')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    setLoading(true)
    axios.get(API + '/trends?group_by=' + groupBy)
      .then(r => { setData(r.data.data || []); setLoading(false) })
      .catch(e => { console.error(e); setLoading(false) })
  }, [groupBy])

  const byPeriod = {}
  data.forEach(d => {
    const p = (d.period || '').slice(0, 10)
    byPeriod[p] = (byPeriod[p] || 0) + (d.count || 0)
  })
  const labels = Object.keys(byPeriod).sort()
  const counts = labels.map(l => byPeriod[l])

  const byVehicle = {}
  data.forEach(d => {
    const v = d.vehicle_type || 'OTHER'
    byVehicle[v] = (byVehicle[v] || 0) + (d.count || 0)
  })
  const vLabels = Object.keys(byVehicle).sort((a,b) => byVehicle[b]-byVehicle[a]).slice(0,8)
  const vCounts = vLabels.map(l => byVehicle[l])

  const COLORS = ['#3B82F6','#F59E0B','#EF4444','#10B981','#8B5CF6','#EC4899','#14B8A6','#F97316']

  const opts = {
    responsive: true, maintainAspectRatio: false,
    plugins: { legend: { labels: { color: '#9CA3AF' } } },
    scales: {
      x: { ticks: { color: '#6B7280' }, grid: { color: '#1F2937' } },
      y: { ticks: { color: '#6B7280' }, grid: { color: '#1F2937' }, beginAtZero: true },
    },
  }

  return (
    <div style={{ padding: 24, background: '#111827', height: '100%', overflowY: 'auto', color: '#E5E7EB' }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 20 }}>
        <h2 style={{ fontSize: 18, fontWeight: 600, color: '#F9FAFB' }}>Violation Trends</h2>
        {['month','week','day'].map(g => (
          <button key={g} onClick={() => setGroupBy(g)} style={{
            padding: '4px 14px', borderRadius: 6, border: 'none', cursor: 'pointer',
            background: groupBy===g ? '#1D4ED8' : '#1F2937',
            color: groupBy===g ? '#BFDBFE' : '#9CA3AF', fontSize: 13
          }}>{g}</button>
        ))}
        {loading && <span style={{ color: '#6B7280', fontSize: 12 }}>Loading...</span>}
      </div>

      <div style={{ background: '#1F2937', borderRadius: 10, padding: 16, marginBottom: 20, height: 300 }}>
        <div style={{ fontWeight: 500, marginBottom: 10, color: '#93C5FD' }}>
          Violations over time — {counts.reduce((a,b)=>a+b,0).toLocaleString()} total
        </div>
        <div style={{ height: 240 }}>
          {labels.length > 0 ? (
            <Line data={{
              labels,
              datasets: [{ label: 'Violations', data: counts,
                borderColor: '#3B82F6', backgroundColor: 'rgba(59,130,246,0.15)',
                tension: 0.3, fill: true, pointRadius: 4 }],
            }} options={opts} />
          ) : (
            <div style={{ color: '#4B5563', paddingTop: 80, textAlign: 'center' }}>
              {loading ? 'Loading data...' : 'No data returned from API'}
            </div>
          )}
        </div>
      </div>

      <div style={{ background: '#1F2937', borderRadius: 10, padding: 16, height: 300 }}>
        <div style={{ fontWeight: 500, marginBottom: 10, color: '#FCD34D' }}>By vehicle type</div>
        <div style={{ height: 240 }}>
          {vLabels.length > 0 ? (
            <Bar data={{
              labels: vLabels,
              datasets: [{ label: 'Violations', data: vCounts, backgroundColor: COLORS }],
            }} options={opts} />
          ) : (
            <div style={{ color: '#4B5563', paddingTop: 80, textAlign: 'center' }}>
              {loading ? 'Loading data...' : 'No data returned from API'}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
