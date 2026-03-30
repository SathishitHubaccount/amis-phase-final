import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import Layout from './components/Layout'
import ProtectedRoute from './components/ProtectedRoute'
import Dashboard from './pages/Dashboard'
import Pipeline from './pages/Pipeline'
import DemandIntelligence from './pages/DemandIntelligence'
import InventoryControl from './pages/InventoryControl'
import MachineHealth from './pages/MachineHealth'
import ProductionPlanning from './pages/ProductionPlanning'
import SupplierManagement from './pages/SupplierManagement'
import Chat from './pages/Chat'
import Negotiation from './pages/Negotiation'
import Login from './pages/Login'
import Integrations from './pages/Integrations'
import AuditLog from './pages/AuditLog'
import ScenarioPlanner from './pages/ScenarioPlanner'

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/" element={<ProtectedRoute><Layout><Dashboard /></Layout></ProtectedRoute>} />
        <Route path="/dashboard" element={<ProtectedRoute><Layout><Dashboard /></Layout></ProtectedRoute>} />
        <Route path="/pipeline" element={<ProtectedRoute><Layout><Pipeline /></Layout></ProtectedRoute>} />
        <Route path="/demand" element={<ProtectedRoute><Layout><DemandIntelligence /></Layout></ProtectedRoute>} />
        <Route path="/inventory" element={<ProtectedRoute><Layout><InventoryControl /></Layout></ProtectedRoute>} />
        <Route path="/machines" element={<ProtectedRoute><Layout><MachineHealth /></Layout></ProtectedRoute>} />
        <Route path="/production" element={<ProtectedRoute><Layout><ProductionPlanning /></Layout></ProtectedRoute>} />
        <Route path="/suppliers" element={<ProtectedRoute><Layout><SupplierManagement /></Layout></ProtectedRoute>} />
        <Route path="/negotiation" element={<ProtectedRoute><Layout><Negotiation /></Layout></ProtectedRoute>} />
        <Route path="/chat" element={<ProtectedRoute><Layout><Chat /></Layout></ProtectedRoute>} />
        <Route path="/integrations" element={<ProtectedRoute><Layout><Integrations /></Layout></ProtectedRoute>} />
        <Route path="/audit" element={<ProtectedRoute><Layout><AuditLog /></Layout></ProtectedRoute>} />
        <Route path="/scenarios" element={<ProtectedRoute><Layout><ScenarioPlanner /></Layout></ProtectedRoute>} />
      </Routes>
    </Router>
  )
}

export default App
