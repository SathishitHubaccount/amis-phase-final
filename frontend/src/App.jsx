import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import Layout from './components/Layout'
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
        <Route path="/" element={<Layout><Dashboard /></Layout>} />
        <Route path="/dashboard" element={<Layout><Dashboard /></Layout>} />
        <Route path="/pipeline" element={<Layout><Pipeline /></Layout>} />
        <Route path="/demand" element={<Layout><DemandIntelligence /></Layout>} />
        <Route path="/inventory" element={<Layout><InventoryControl /></Layout>} />
        <Route path="/machines" element={<Layout><MachineHealth /></Layout>} />
        <Route path="/production" element={<Layout><ProductionPlanning /></Layout>} />
        <Route path="/suppliers" element={<Layout><SupplierManagement /></Layout>} />
        <Route path="/negotiation" element={<Layout><Negotiation /></Layout>} />
        <Route path="/chat" element={<Layout><Chat /></Layout>} />
        <Route path="/integrations" element={<Layout><Integrations /></Layout>} />
        <Route path="/audit" element={<Layout><AuditLog /></Layout>} />
        <Route path="/scenarios" element={<Layout><ScenarioPlanner /></Layout>} />
      </Routes>
    </Router>
  )
}

export default App
