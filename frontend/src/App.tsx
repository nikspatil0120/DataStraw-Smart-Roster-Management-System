import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { QueryClientProvider, QueryClient } from '@tanstack/react-query'
import Layout from './components/layout/Layout'
import Dashboard from './pages/Dashboard'
import Employees from './pages/Employees'
import Brands from './pages/Brands'
import Processes from './pages/Processes'
import Pods from './pages/Pods'
import Roster from './pages/Roster'
import Conflicts from './pages/Conflicts'
import Analytics from './pages/Analytics'

const queryClient = new QueryClient()

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <Router>
        <Routes>
          <Route element={<Layout />}>
            <Route path="/" element={<Dashboard />} />
            <Route path="/employees" element={<Employees />} />
            <Route path="/brands" element={<Brands />} />
            <Route path="/processes" element={<Processes />} />
            <Route path="/pods" element={<Pods />} />
            <Route path="/roster" element={<Roster />} />
            <Route path="/conflicts" element={<Conflicts />} />
            <Route path="/analytics" element={<Analytics />} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Route>
        </Routes>
      </Router>
    </QueryClientProvider>
  )
}

export default App
