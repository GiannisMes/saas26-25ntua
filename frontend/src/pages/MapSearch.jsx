import { useState, useEffect } from 'react'
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet'
import axios from 'axios'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'

// Fix default marker icon
delete L.Icon.Default.prototype._getIconUrl
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png',
  iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
  shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
})

export default function MapSearch() {
  const [points, setPoints] = useState([])
  const [loading, setLoading] = useState(false)

  const fetchPoints = async () => {
    setLoading(true)
    try {
      const res = await axios.post('/api/orchestrator/search')
      setPoints(res.data || [])
    } catch (err) {
      console.error(err)
    }
    setLoading(false)
  }

  useEffect(() => { fetchPoints() }, [])

  const handleReserve = async (pointId, provider) => {
    try {
      const res = await axios.post('/api/orchestrator/reserve', {
        pointId,
        userId: "user1",
        provider,
        duration: 60
      })
      if (res.data.success) {
        alert(`Κράτηση επιτυχής! Λήξη: ${res.data.endTime}`)
      } else {
        alert(`Αποτυχία: ${res.data.errorMessage}`)
      }
    } catch (err) {
      alert('Σφάλμα κράτησης')
    }
  }

  return (
    <div className="h-[calc(100vh-64px)] w-full">
      <MapContainer center={[37.98, 23.73]} zoom={12} className="h-full w-full">
        <TileLayer
          attribution='&copy; OpenStreetMap'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        {points.map((p, i) => (
          <Marker key={i} position={[p.latitude || 37.98, p.longitude || 23.73]}>
            <Popup>
              <div className="text-sm">
                <p className="font-bold">{p.pointId || p.id}</p>
                <p>Provider: {p.provider}</p>
                <p>Status: {p.status || 'Unknown'}</p>
                <button
                  onClick={() => handleReserve(p.pointId || p.id, p.provider)}
                  className="mt-2 bg-green-500 text-white px-3 py-1 rounded text-xs"
                >
                  Κράτηση
                </button>
              </div>
            </Popup>
          </Marker>
        ))}
      </MapContainer>
    </div>
  )
}