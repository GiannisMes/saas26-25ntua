import { BrowserRouter, Routes, Route, Link } from 'react-router-dom'
import MapSearch from './pages/MapSearch'
import UserDashboard from './pages/UserDashboard'
import ProviderRegister from './pages/ProviderRegister'
import ProviderDashboard from './pages/ProviderDashboard'
import AdminDashboard from './pages/AdminDashboard'

function App() {
  return (
    <BrowserRouter>
      <nav className="bg-gray-900 text-white p-4 flex gap-6">
        <Link to="/" className="font-bold text-xl text-green-400">⚡ saasPlug</Link>
        <Link to="/" className="hover:text-green-300">Χάρτης</Link>
        <Link to="/user" className="hover:text-green-300">Κρατήσεις μου</Link>
        <Link to="/provider/register" className="hover:text-green-300">Εγγραφή Παρόχου</Link>
        <Link to="/provider/dashboard" className="hover:text-green-300">Provider Dashboard</Link>
        <Link to="/admin" className="hover:text-green-300">Admin</Link>
      </nav>
      <Routes>
        <Route path="/" element={<MapSearch />} />
        <Route path="/user" element={<UserDashboard />} />
        <Route path="/provider/register" element={<ProviderRegister />} />
        <Route path="/provider/dashboard" element={<ProviderDashboard />} />
        <Route path="/admin" element={<AdminDashboard />} />
      </Routes>
    </BrowserRouter>
  )
}

export default App