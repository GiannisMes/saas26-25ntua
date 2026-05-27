import { useState, useEffect } from 'react'
import axios from 'axios'

export default function AdminDashboard() {
  const [stats, setStats] = useState(null)
  const [health, setHealth] = useState(null)

  useEffect(() => {
    axios.get('/api/orchestrator/admin/stats')
      .then(res => setStats(res.data))
      .catch(() => {})
    axios.get('/health')
      .then(res => setHealth(res.data))
      .catch(() => {})
  }, [])

  return (
    <div className="max-w-4xl mx-auto p-6">
      <h1 className="text-2xl font-bold mb-6">Admin Dashboard</h1>
      
      {health && typeof health === 'object' && !Array.isArray(health) && (
        <div className="mb-8">
          <h2 className="text-lg font-semibold mb-3">System Health</h2>
          <div className="grid grid-cols-4 gap-3">
            {Object.entries(health).filter(([k]) => k !== 'pending_retry_events').map(([name, status]) => (
              <div key={name} className={`p-3 rounded-lg text-center ${status === 'UP' ? 'bg-green-100' : 'bg-red-100'}`}>
                <p className="font-semibold">{name}</p>
                <p className={status === 'UP' ? 'text-green-600' : 'text-red-600'}>{status}</p>
              </div>
            ))}
            <div className="p-3 rounded-lg text-center bg-yellow-100">
              <p className="font-semibold">Pending Events</p>
              <p className="text-yellow-600">{health.pending_retry_events}</p>
            </div>
          </div>
        </div>
      )}

      {stats && (
        <div className="grid grid-cols-3 gap-4">
          <div className="bg-blue-50 p-6 rounded-lg text-center">
            <p className="text-3xl font-bold text-blue-600">{stats.total_reservations}</p>
            <p className="text-gray-600">Σύνολο Κρατήσεων</p>
          </div>
          <div className="bg-green-50 p-6 rounded-lg text-center">
            <p className="text-3xl font-bold text-green-600">{stats.active_reservations}</p>
            <p className="text-gray-600">Ενεργές</p>
          </div>
          <div className="bg-red-50 p-6 rounded-lg text-center">
            <p className="text-3xl font-bold text-red-600">{stats.cancelled_reservations}</p>
            <p className="text-gray-600">Ακυρωμένες</p>
          </div>
        </div>
      )}
    </div>
  )
}