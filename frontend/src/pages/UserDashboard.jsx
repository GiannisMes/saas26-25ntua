import { useState, useEffect } from 'react'
import axios from 'axios'

export default function UserDashboard() {
  const [reservations, setReservations] = useState([])
  const userId = "user1"

  useEffect(() => {
    axios.get(`/api/orchestrator/reservations/${userId}`)
      .then(res => setReservations(res.data || []))
      .catch(() => {})
  }, [])

  const handleCancel = async (resId) => {
    try {
      await axios.put(`/api/orchestrator/reserve/${resId}/cancel?user_id=${userId}`)
      setReservations(prev => prev.map(r => r.reservationId === resId ? {...r, status: 'CANCELLED'} : r))
      alert('Ακυρώθηκε επιτυχώς')
    } catch {
      alert('Σφάλμα ακύρωσης')
    }
  }

  return (
    <div className="max-w-4xl mx-auto p-6">
      <h1 className="text-2xl font-bold mb-6">Οι Κρατήσεις μου</h1>
      {reservations.length === 0 ? (
        <p className="text-gray-500">Δεν υπάρχουν κρατήσεις.</p>
      ) : (
        <div className="space-y-4">
          {reservations.map(r => (
            <div key={r.reservationId} className="bg-white shadow rounded-lg p-4 flex justify-between items-center">
              <div>
                <p className="font-semibold">Point: {r.pointId}</p>
                <p className="text-sm text-gray-500">Λήξη: {r.endTime}</p>
                <span className={`text-xs px-2 py-1 rounded ${r.status === 'ACTIVE' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}`}>
                  {r.status}
                </span>
              </div>
              {r.status === 'ACTIVE' && (
                <button onClick={() => handleCancel(r.reservationId)} className="bg-red-500 text-white px-4 py-2 rounded">
                  Ακύρωση
                </button>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  )
}