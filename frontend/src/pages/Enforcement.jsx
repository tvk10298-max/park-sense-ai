import { useEffect, useState } from 'react'
import axios from 'axios'

const API = import.meta.env.VITE_API_URL || ''

const CIS_COLOR = (score) =>
  score > 70 ? '#EF4444' : score > 45 ? '#F59E0B' : '#10B981'

export default function Enforcement() {
  const [recs, setRecs] = useState([])

  useEffect(() => {
    axios.get(`${API}/enforcement/priority?top_n=15`)
      .then(r => setRecs(r.data.recommendations || []))
      .catch(console.error)
  }, [])

  return (
    <div style={{ padding: 24, background: '#111827', height: '100%', overflowY: 'auto', color: '#E5E7EB' }}>
      <h2 style={{ fontSize: 18, fontWeight: 600, color: '#F9FAFB', marginBottom: 4 }}>
        Enforcement Priority
      </h2>
      <p style={{ fontSize: 13, color: '#6B7280', marginBottom: 20 }}>
        Ranked by Congestion Impact Score × violation volume. Deploy officers to top zones first.
      </p>

      <div style={{ display: 'grid', gap: 10 }}>
        {recs.map((r, i) => (
          <div key={i} style={{
            background: '#1F2937', borderRadius: 10, padding: 16,
            display: 'flex', alignItems: 'center', gap: 16,
            border: i === 0 ? '1px solid #EF4444' : '1px solid #374151'
          }}>
            {/* Rank */}
            <div style={{
              width: 36, height: 36, borderRadius: '50%', flexShrink: 0,
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              background: i === 0 ? '#7F1D1D' : '#111827',
              color: i === 0 ? '#FCA5A5' : '#9CA3AF', fontWeight: 700, fontSize: 15
            }}>#{i+1}</div>

            {/* Station info */}
            <div style={{ flex: 1 }}>
              <div style={{ fontWeight: 600, color: '#F9FAFB', fontSize: 15 }}>
                {r.police_station}
              </div>
              <div style={{ color: '#6B7280', fontSize: 12, marginTop: 2 }}>
                {r.violation_count?.toLocaleString()} violations · Peak hour: {r.peak_hour}:00
              </div>
            </div>

            {/* CIS badge */}
            <div style={{ textAlign: 'center' }}>
              <div style={{ fontSize: 22, fontWeight: 700, color: CIS_COLOR(r.avg_cis_score) }}>
                {r.avg_cis_score}
              </div>
              <div style={{ fontSize: 10, color: '#6B7280' }}>avg CIS</div>
            </div>

            {/* Officers */}
            <div style={{ textAlign: 'center', minWidth: 72 }}>
              <div style={{
                background: '#0F2D52', borderRadius: 8, padding: '6px 12px',
                color: '#60A5FA', fontWeight: 700, fontSize: 16
              }}>
                {r.recommended_officers}
              </div>
              <div style={{ fontSize: 10, color: '#6B7280', marginTop: 3 }}>officers</div>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
