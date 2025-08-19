import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import Layout from './components/Layout';
import Dashboard from './pages/Dashboard';
import JobLauncher from './pages/JobLauncher';
import TemplateBuilder from './pages/TemplateBuilder';
import DQPanel from './pages/DQPanel';
import Exports from './pages/Exports';
import ErasureAdmin from './pages/ErasureAdmin';
import ProxyMonitor from './pages/ProxyMonitor';
import APIExplorer from './pages/APIExplorer';
import Settings from './pages/Settings';

function App() {
  return (
    <Router>
      <Routes>
        <Route element={<Layout />}>
          <Route path="/" element={<Dashboard />} />
          <Route path="/launch" element={<JobLauncher />} />
          <Route path="/templates" element={<TemplateBuilder />} />
          <Route path="/dq" element={<DQPanel />} />
          <Route path="/exports" element={<Exports />} />
          <Route path="/erasure" element={<ErasureAdmin />} />
          <Route path="/proxies" element={<ProxyMonitor />} />
          <Route path="/api" element={<APIExplorer />} />
          <Route path="/settings" element={<Settings />} />
        </Route>
      </Routes>
    </Router>
  );
}

export default App;