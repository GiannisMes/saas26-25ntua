import { useState } from 'react'
import axios from 'axios'

export default function ProviderDashboard() {
  const [providerName, setProviderName] = useState('')
  const [stats, setStats] = useState(null)

  const fetchStats = async () => {
    try {
      const res = await axios.get(`/api/orchestrator/statistics/provider/${providerName}`)
      setStats(res.data)
    } catch {
      alert('Σφάλμα φόρτωσης στατιστικών')
    }
  }

  return (
    <div className="max-w-4xl mx-auto p-6">
      <h1 className="text-2xl font-bold mb-6">Provider Dashboard</h1>
      <div className="flex gap-2 mb-6">
        <input placeholder="Όνομα Παρόχου" value={providerName}
          onChange={e => setProviderName(e.target.value)}
          className="border p-2 rounded flex-1" />
        <button onClick={fetchStats} className="bg-blue-600 text-white px-4 py-2 rounded">
          Φόρτωση
        </button>
      </div>
      {stats && (
        <div className="grid grid-cols-2 gap-4">
          <div className="bg-blue-50 p-6 rounded-lg text-center">
            <p className="text-3xl font-bold text-blue-600">{stats.statistics?.Click || 0}</p>
            <p className="text-gray-600">Clicks</p>
          </div>
          <div className="bg-green-50 p-6 rounded-lg text-center">
            <p className="text-3xl font-bold text-green-600">{stats.statistics?.Reservation || 0}</p>
            <p className="text-gray-600">Κρατήσεις</p>
          </div>
        </div>
      )}
    </div>
  )
}