import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import Dashboard from './pages/Dashboard';
import JobLauncher from './pages/JobLauncher';
import TemplateBuilder from './pages/TemplateBuilder';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/launch" element={<JobLauncher />} />
        <Route path="/templates" element={<TemplateBuilder />} />
      </Routes>
    </Router>
  );
}

export default App;