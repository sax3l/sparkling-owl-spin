import { Outlet, Link, useLocation } from 'react-router-dom';
import { 
  LayoutDashboard, 
  Play, 
  FileText, 
  BarChart3, 
  Download, 
  Shield, 
  Globe, 
  Code, 
  Settings,
  Activity,
  Database,
  Zap,
  Rocket,
  FolderOpen,
  Wand2,
  Target,
  MonitorSpeaker,
  PenTool,
  Monitor,
  Eye,
  Lock,
  Clock,
  HelpCircle,
  BookOpen
} from 'lucide-react';
import { cn } from '@/lib/utils';
import { ConnectionStatus } from './ConnectionStatus';

const navigation = [
  { name: 'Dashboard', href: '/', icon: LayoutDashboard },
  { name: 'Onboarding', href: '/onboarding', icon: Rocket },
  { name: 'Datalager', href: '/data', icon: Database },
  { name: 'Källor & Projekt', href: '/sources', icon: FolderOpen },
  { name: 'Projektstyrning', href: '/project-management', icon: Target },
  { name: 'Jobbkontroll', href: '/job-control', icon: MonitorSpeaker },
  { name: 'Crawl Plan Studio', href: '/crawl-plan', icon: PenTool },
  { name: 'Jobbdetaljer', href: '/job-details', icon: Eye },
  { name: 'Browser Panel', href: '/browser', icon: Monitor },
  { name: 'Job Launcher', href: '/launch', icon: Play },
  { name: 'Templates', href: '/templates', icon: FileText },
  { name: 'Template Wizard', href: '/template-wizard', icon: Wand2 },
  { name: 'Data Quality', href: '/dq', icon: BarChart3 },
  { name: 'Exports', href: '/exports', icon: Download },
  { name: 'Privacy Center', href: '/privacy', icon: Lock },
  { name: 'Policies', href: '/policies', icon: Shield },
  { name: 'Scheduler', href: '/scheduler', icon: Clock },
  { name: 'Audit Log', href: '/audit', icon: Activity },
  { name: 'GDPR Admin', href: '/erasure', icon: Shield },
  { name: 'Proxy Monitor', href: '/proxies', icon: Globe },
  { name: 'API Explorer', href: '/api', icon: Code },
  { name: 'Hjälp', href: '/help', icon: HelpCircle },
  { name: 'Settings', href: '/settings', icon: Settings },
];

const Layout = () => {
  const location = useLocation();

  return (
    <div className="min-h-screen bg-background">
      {/* Sidebar */}
      <div className="fixed inset-y-0 left-0 w-64 bg-sidebar border-r border-sidebar-border">
        {/* Logo */}
        <div className="flex items-center px-6 py-6">
          <div className="flex items-center space-x-3">
            <div className="w-8 h-8 bg-gradient-primary rounded-lg flex items-center justify-center">
              <Database className="w-5 h-5 text-primary-foreground" />
            </div>
            <div>
              <h1 className="text-xl font-bold text-sidebar-foreground">ECaDP</h1>
              <p className="text-xs text-sidebar-foreground/60">Ethical Crawler Platform</p>
            </div>
          </div>
        </div>

        {/* Status indicator */}
        <div className="px-6 pb-4">
          <div className="flex items-center justify-center">
            <ConnectionStatus />
          </div>
        </div>

        {/* Navigation */}
        <nav className="px-3 space-y-1">
          {navigation.map((item) => {
            const isActive = location.pathname === item.href;
            return (
              <Link
                key={item.name}
                to={item.href}
                className={cn(
                  'flex items-center space-x-3 px-3 py-2 rounded-lg text-sm font-medium transition-all duration-200',
                  isActive
                    ? 'bg-sidebar-primary text-sidebar-primary-foreground shadow-primary'
                    : 'text-sidebar-foreground hover:bg-sidebar-accent hover:text-sidebar-accent-foreground'
                )}
              >
                <item.icon className="w-5 h-5" />
                <span>{item.name}</span>
              </Link>
            );
          })}
        </nav>

        {/* Footer */}
        <div className="absolute bottom-0 left-0 right-0 p-6">
          <div className="text-xs text-sidebar-foreground/40 space-y-1">
            <div className="flex items-center space-x-2">
              <Activity className="w-3 h-3" />
              <span>v2.1.3</span>
            </div>
            <div className="flex items-center space-x-2">
              <Zap className="w-3 h-3" />
              <span>Built with Lovable</span>
            </div>
          </div>
        </div>
      </div>

      {/* Main content */}
      <div className="pl-64">
        <main className="p-8">
          <Outlet />
        </main>
      </div>
    </div>
  );
};

export default Layout;