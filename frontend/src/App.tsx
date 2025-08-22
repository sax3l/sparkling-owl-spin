import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import Layout from "./components/Layout";
import Dashboard from "./pages/Dashboard";
import JobLauncher from "./pages/JobLauncher";
import TemplateBuilder from "./pages/TemplateBuilder";
import DQPanel from "./pages/DQPanel";
import Exports from "./pages/Exports";
import ErasureAdmin from "./pages/ErasureAdmin";
import ProxyMonitor from "./pages/ProxyMonitor";
import APIExplorer from "./pages/APIExplorer";
import Settings from "./pages/Settings";
import OnboardingWizard from "./pages/OnboardingWizard";
import DataWarehouse from "./pages/DataWarehouse";
import SourcesProjects from "./pages/SourcesProjects";
import TemplateWizard from "./pages/TemplateWizard";
import ProjectManagement from "./pages/ProjectManagement";
import JobControl from "./pages/JobControl";
import CrawlPlanStudio from "./pages/CrawlPlanStudio";
import JobDetailsConsole from "./pages/JobDetailsConsole";
import BrowserPanel from "./pages/BrowserPanel";
import PrivacyCenter from "./pages/PrivacyCenter";
import Policies from "./pages/Policies";
import Scheduler from "./pages/Scheduler";
import AuditLog from "./pages/AuditLog";
import HelpCenter from "./pages/HelpCenter";
import NotFound from "./pages/NotFound";

const queryClient = new QueryClient();

const App = () => (
  <QueryClientProvider client={queryClient}>
    <TooltipProvider>
      <Toaster />
      <Sonner />
      <BrowserRouter>
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
            <Route path="/onboarding" element={<OnboardingWizard />} />
            <Route path="/data" element={<DataWarehouse />} />
            <Route path="/sources" element={<SourcesProjects />} />
            <Route path="/template-wizard" element={<TemplateWizard />} />
            <Route path="/project-management" element={<ProjectManagement />} />
            <Route path="/job-control" element={<JobControl />} />
            <Route path="/crawl-plan" element={<CrawlPlanStudio />} />
            <Route path="/job-details" element={<JobDetailsConsole />} />
            <Route path="/browser" element={<BrowserPanel />} />
            <Route path="/privacy" element={<PrivacyCenter />} />
            <Route path="/policies" element={<Policies />} />
            <Route path="/scheduler" element={<Scheduler />} />
            <Route path="/audit" element={<AuditLog />} />
            <Route path="/help" element={<HelpCenter />} />
          </Route>
          {/* ADD ALL CUSTOM ROUTES ABOVE THE CATCH-ALL "*" ROUTE */}
          <Route path="*" element={<NotFound />} />
        </Routes>
      </BrowserRouter>
    </TooltipProvider>
  </QueryClientProvider>
);

export default App;
