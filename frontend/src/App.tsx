import { BrowserRouter, Routes, Route, Link } from 'react-router-dom'
import Dashboard from './pages/Dashboard'
import Materials from './pages/Materials'
import Curriculum from './pages/Curriculum'
import Lessons from './pages/Lessons'
import Reflections from './pages/Reflections'

function App() {
  return (
    <BrowserRouter>
      <div className="flex h-screen bg-gray-50">
        {/* Sidebar */}
        <div className="w-64 bg-white border-r border-gray-200 p-6">
          <div className="mb-8">
            <h1 className="text-2xl font-bold text-indigo-600">LinguaForge</h1>
            <p className="text-sm text-gray-500">Local AI Language Tutor</p>
          </div>

          <nav className="space-y-1">
            <Link to="/" className="block px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-md">Dashboard</Link>
            <Link to="/materials" className="block px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-md">My Materials</Link>
            <Link to="/curriculum" className="block px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-md">Curriculum</Link>
            <Link to="/lessons" className="block px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-md">Generate Lessons</Link>
            <Link to="/reflections" className="block px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-md">Reflections</Link>
          </nav>

          <div className="mt-auto pt-8 text-xs text-gray-400">
            Backend: http://localhost:8000
          </div>
        </div>

        {/* Main Content */}
        <div className="flex-1 overflow-auto p-8">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/materials" element={<Materials />} />
            <Route path="/curriculum" element={<Curriculum />} />
            <Route path="/lessons" element={<Lessons />} />
            <Route path="/reflections" element={<Reflections />} />
          </Routes>
        </div>
      </div>
    </BrowserRouter>
  )
}

export default App
