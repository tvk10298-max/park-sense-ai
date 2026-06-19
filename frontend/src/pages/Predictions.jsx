import { useEffect, useState } from 'react'
import axios from 'axios'
import { Bar } from 'react-chartjs-2'
import { Chart, CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend } from 'chart.js'

Chart.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend)

const API = import.meta.env.VITE_API_URL || ''

export default function Predictions() {
  const [data, setData]       = useState([])
  const [station, setStation] = useState('Upparpet')
  const [all, setAll]         = useState([])

  useEffect(() => {
    axios.get(`${API}/predictions`)
      .then(r => { setAll(r.data.predictions || []); })
      .catch(console.error)
  }, [])

  useEffect(() => {
    axios.get(`${API}/predictions?station=${encodeURIComponent(station)}`)
      .then(r => setData(r.data.predictions || []))
      .catch(console.error)
  }, [station])

  // Top stations for tomorrow
  const tomorrow = all.filter(d => d.date === all[0]?.date)
    .sort((a,b) => b.predicted_violations - a.predicted_violations)
    .slice(0, 8)

  const stations = [...new Set(all.map(d => d.police_station))].sort()

  const chartData = {
    labels: data.map(d => `${d.day_name}\n${d.date}`),
    datasets: [{
      label: 'Predicted violations',
      data: data.map(d => d.predicted_violations),
      backgroundColor: data.map(d =>
        d.predicted_violations > 50 ? '#EF4444' :
        d.predicted_violations > 20 ? '#F59E0B' : '#10B981'
      ),
      borderRadius: 6,
    }]
  }

  const chartOpts = {
    responsive: true, maintainAspectRatio: false,
    plugins: { legend: { labels: { color: '#9CA3AF' } } },
    scales: {
      x: { ticks: { color: '#6B7280' }, grid: { color: '#1F2937' } },
      y: { ticks: { color: '#6B7280' }, grid: { color: '#1F2937' }, beginAtZero: true },
    },
  }

  return (
    <div style={{ padding: 24, background: '#111827', height: '100%', overflowY: 'auto', color: '#E5E7EB' }}>
      <h2 style={{ fontSize: 18, fontWeight: 600, color: '#F9FAFB', marginBottom: 4 }}>
        🔮 7-Day Violation Forecast
      </h2>
      <p style={{ fontSize: 13, color: '#6B7280', marginBottom: 20 }}>
        XGBoost model trained on 298,450 Bengaluru violation records · Predicts next 7 days
      </p>

      {/* Tomorrow's top hotspots */}
      <div style={{ marginBottom: 24 }}>
        <div style={{ fontWeight: 600, color: '#FCD34D', marginBottom: 10, fontSize: 14 }}>
          ⚠ Predicted Hotspots Tomorrow
        </div>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 8 }}>
          {tomorrow.map((t, i) => (
            <div key={i} onClick={() => setStation(t.police_station)}
              style={{
                background: '#1F2937', borderRadius: 8, padding: '10px 14px',
                cursor: 'pointer', border: i < 2 ? '1px solid #EF4444' : '1px solid #374151'
              }}>
              <div style={{ fontWeight: 600, fontSize: 13, color: '#F9FAFB' }}>
                {t.police_station}
              </div>
              <div style={{ fontSize: 20, fontWeight: 700,
                color: t.predicted_violations > 50 ? '#EF4444' :
                       t.predicted_violations > 20 ? '#F59E0B' : '#10B981',
                marginTop: 4 }}>
                {t.predicted_violations}
              </div>
              <div style={{ fontSize: 11, color: '#6B7280' }}>predicted violations</div>
            </div>
          ))}
        </div>
      </div>

      {/* Station selector + chart */}
      <div style={{ background: '#1F2937', borderRadius: 10, padding: 16 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 16 }}>
          <span style={{ fontSize: 14, fontWeight: 500, color: '#93C5FD' }}>
            7-day forecast for:
          </span>
          <select value={station} onChange={e => setStation(e.target.value)}
            style={{ background: '#111827', color: '#E5E7EB', border: '1px solid #374151',
                     borderRadius: 6, padding: '4px 10px', fontSize: 13 }}>
            {stations.map(s => <option key={s} value={s}>{s}</option>)}
          </select>
        </div>
        <div style={{ height: 260 }}>
          <Bar data={chartData} options={chartOpts} />
        </div>
      </div>
    </div>
  )
}