import { Route, Routes } from 'react-router-dom'
import Layout from './components/Layout.jsx'
import Home from './pages/Home.jsx'
import Dashboard from './pages/Dashboard.jsx'
import Menu from './pages/Menu.jsx'
import Warehouse from './pages/Warehouse.jsx'
import Audit from './pages/Audit.jsx'
import Insights from './pages/Insights.jsx'
import Assistant from './pages/Assistant.jsx'
import Pricing from './pages/Pricing.jsx'
import BillingSuccess from './pages/BillingSuccess.jsx'
import NotFound from './pages/NotFound.jsx'

export default function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route index element={<Home />} />
        <Route path="dashboard" element={<Dashboard />} />
        <Route path="menu" element={<Menu />} />
        <Route path="warehouse" element={<Warehouse />} />
        <Route path="audit" element={<Audit />} />
        <Route path="insights" element={<Insights />} />
        <Route path="assistant" element={<Assistant />} />
        <Route path="pricing" element={<Pricing />} />
        <Route path="billing/success" element={<BillingSuccess />} />
        <Route path="*" element={<NotFound />} />
      </Route>
    </Routes>
  )
}
