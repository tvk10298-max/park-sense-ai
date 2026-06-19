import { useEffect, useState, useRef } from 'react'
import { MapContainer, TileLayer, useMap, CircleMarker, Popup } from 'react-leaflet'
import L from 'leaflet'
import 'leaflet.heat'
import axios from 'axios'

const API = import.meta.env.VITE_API_URL || 'http://localhost:8000'
const WS  = import.meta.env.VITE_WS_URL  || 'ws://localhost:8000'

function HeatLayer({ points }) {
  const map = useMap()
  const layerRef = useRef(null)
  useEffect(() => {
    if (!points.length) return
    if (layerRef.current) map.removeLayer(layerRef.current)
    layerRef.current = L.heatLayer(points, {
      radius: 30, blur: 20, maxZoom: 17,
      gradient: { 0.2: '#3B82F6', 0.5: '#F59E0B', 0.8: '#EF4444', 1.0: '#7C3AED' }
    }).addTo(map)
    return () => { if (layerRef.current) map.removeLayer(layerRef.current) }
  }, [points])
  return null
}

function MapController({ flyTarget }) {
  const map = useMap()
  useEffect(() => {
    if (flyTarget) map.flyTo([flyTarget.lat, flyTarget.lng], 15, { duration: 1.5 })
  }, [flyTarget])
  return null
}

const CIS_COLOR = s => s > 70 ? '#EF4444' : s > 55 ? '#F59E0B' : '#10B981'

export default function Dashboard() {
  const [hotspots, setHotspots]   = useState([])
  const [heatPts,  setHeatPts]    = useState([])
  const [live,     setLive]       = useState([])
  const [flyTarget, setFlyTarget] = useState(null)

  useEffect(() => {
    axios.get(API + '/hotspots?limit=200').then(r => {
      const h = r.data.hotspots || []
      setHotspots(h)
      setHeatPts(h.map(x => [x.centroid_lat, x.centroid_lng, Math.min(1, x.avg_cis_score / 100)]))
    }).catch(console.error)
  }, [])

  useEffect(() => {
    const ws = new WebSocket(WS + '/live')
    ws.onmessage = e => {
      const msg = JSON.parse(e.data)
      if (msg.type === 'violation') {
        setLive(prev => [msg, ...prev].slice(0, 50))
        setHeatPts(prev => [[msg.latitude, msg.longitude, 0.8], ...prev].slice(0, 5000))
      }
    }
    return () => ws.close()
  }, [])

  return (
    <div style={{ display: 'flex', height: '100%' }}>
      <div style={{ flex: 1 }}>
        <MapContainer center={[12.9716, 77.5946]} zoom={12}
          style={{ height: '100%', width: '100%' }}>
          <TileLayer
            url='https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png'
            attribution='© OpenStreetMap' />
          <HeatLayer points={heatPts} />
          <MapController flyTarget={flyTarget} />
          {hotspots.map((h, i) => (
            <CircleMarker key={i}
              center={[h.centroid_lat, h.centroid_lng]}
              radius={Math.max(6, Math.min(22, h.violation_count / 700))}
              pathOptions={{
                color: CIS_COLOR(h.avg_cis_score),
                fillColor: CIS_COLOR(h.avg_cis_score),
                fillOpacity: 0.75
              }}>
              <Popup>
                <div style={{ minWidth: 180 }}>
                  <strong>{h.police_station}</strong><br/>
                  Violations: <strong>{h.violation_count?.toLocaleString()}</strong><br/>
                  CIS Score: <strong>{h.avg_cis_score}</strong><br/>
                  Top: {h.top_violation}
                </div>
              </Popup>
            </CircleMarker>
          ))}
        </MapContainer>
      </div>

      <div style={{ width: 300, background: '#111827', color: '#E5E7EB', overflowY: 'auto', padding: 16, fontSize: 13 }}>
        <div style={{ fontWeight: 700, fontSize: 14, marginBottom: 4, color: '#60A5FA' }}>
          Top Hotspots — by CIS Score
        </div>
        <div style={{ fontSize: 11, color: '#4B5563', marginBottom: 12 }}>
          Click a station to fly to it on the map
        </div>
        {hotspots.slice(0, 15).map((h, i) => (
          <div key={i}
            onClick={() => setFlyTarget({ lat: h.centroid_lat, lng: h.centroid_lng, ts: Date.now() })}
            style={{ background: '#1F2937', borderRadius: 8, padding: '8px 10px', marginBottom: 6, cursor: 'pointer', border: '1px solid #374151' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span style={{ color: '#F9FAFB', fontWeight: 500 }}>
                {'#'}{i + 1} {h.police_station}
              </span>
              <span style={{ background: CIS_COLOR(h.avg_cis_score), color: '#fff', padding: '1px 7px', borderRadius: 4, fontSize: 11 }}>
                CIS {h.avg_cis_score}
              </span>
            </div>
            <div style={{ color: '#9CA3AF', marginTop: 3 }}>
              {h.violation_count?.toLocaleString()} violations
            </div>
          </div>
        ))}

        <div style={{ fontWeight: 700, fontSize: 14, margin: '16px 0 8px', color: '#34D399' }}>
          Live Feed
        </div>
        {live.slice(0, 10).map((v, i) => (
          <div key={i} style={{ background: '#1F2937', borderRadius: 6, padding: '6px 8px', marginBottom: 4, borderLeft: '3px solid #F59E0B' }}>
            <span style={{ color: '#FCD34D' }}>{v.vehicle_type}</span>
            <span style={{ color: '#9CA3AF', marginLeft: 6 }}>{v.police_station}</span>
          </div>
        ))}
        {!live.length && (
          <div style={{ color: '#4B5563', fontSize: 12 }}>Waiting for live violations…</div>
        )}
      </div>
    </div>
  )
}