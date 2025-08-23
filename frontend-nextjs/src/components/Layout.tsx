import React, { useState } from 'react';
import { usePathname } from 'next/navigation';
import Link from 'next/link';
import { 
  LayoutDashboard, 
  Play, 
  FileText, 
  BarChart3, 
  Shield, 
  Globe, 
  Code, 
  Settings,
  Activity,
  Database,
  Zap,
  MousePointer,
  Search,
  MapPin,
  Users,
  Building,
  Car,
  UploadCloud,
  Calendar,
  LineChart,
  Key,
  ShieldCheck,
  HelpCircle,
  ChevronDown,
  ChevronRight
} from 'lucide-react';
import { cn } from '@/lib/utils';

const navigationSections = [
  {
    title: 'Hem & Översikt',
    items: [
      { name: 'Dashboard', href: '/', icon: LayoutDashboard },
    ]
  },
  {
    title: 'Mallar & Extrahering',
    items: [
      { name: 'Mallbibliotek', href: '/templates', icon: FileText },
      { name: 'Peka-och-extrahera', href: '/selector-studio', icon: MousePointer },
      { name: 'XPath-analys', href: '/xpath-analysis', icon: Search },
    ]
  },
  {
    title: 'Crawling & Scraping',
    items: [
      { name: 'Crawl-konfigurator', href: '/crawl-config', icon: MapPin },
      { name: 'Jobbkö', href: '/jobs', icon: Play },
      { name: 'Sitemaps', href: '/sitemaps', icon: Globe },
    ]
  },
  {
    title: 'Data & Export',
    items: [
      { name: 'Personer', href: '/data/persons', icon: Users },
      { name: 'Företag', href: '/data/companies', icon: Building },
      { name: 'Fordon', href: '/data/vehicles', icon: Car },
      { name: 'Datakvalitet', href: '/dq', icon: BarChart3 },
      { name: 'Export/Import', href: '/exports', icon: UploadCloud },
    ]
  },
  {
    title: 'Proxy & Anti-bot',
    items: [
      { name: 'Proxy-hälsa', href: '/proxies', icon: Shield },
      { name: 'Anti-bot-policyer', href: '/anti-bot', icon: ShieldCheck },
      { name: 'URL-diagnostik', href: '/diagnostics', icon: Search },
    ]
  },
  {
    title: 'Observability',
    items: [
      { name: 'Metrics', href: '/metrics', icon: LineChart },
      { name: 'Schemaläggning', href: '/scheduler', icon: Calendar },
      { name: 'Loggar', href: '/logs', icon: Activity },
    ]
  },
  {
    title: 'API & Integration',
    items: [
      { name: 'API-nycklar', href: '/api-keys', icon: Key },
      { name: 'API Explorer', href: '/api', icon: Code },
      { name: 'Webhooks', href: '/webhooks', icon: Zap },
    ]
  },
  {
    title: 'Säkerhet & Governance',
    items: [
      { name: 'GDPR/Privacy', href: '/privacy', icon: Shield },
      { name: 'Roller', href: '/roles', icon: Users },
      { name: 'Auditlogg', href: '/audit', icon: Activity },
    ]
  },
  {
    title: 'System',
    items: [
      { name: 'Inställningar', href: '/settings', icon: Settings },
      { name: 'Hjälp', href: '/help', icon: HelpCircle },
    ]
  }
];

interface LayoutProps {
  children: React.ReactNode;
}

const Layout: React.FC<LayoutProps> = ({ children }) => {
  const pathname = usePathname();
  const [collapsedSections, setCollapsedSections] = useState<Set<string>>(new Set());

  const toggleSection = (title: string) => {
    const newCollapsed = new Set(collapsedSections);
    if (newCollapsed.has(title)) {
      newCollapsed.delete(title);
    } else {
      newCollapsed.add(title);
    }
    setCollapsedSections(newCollapsed);
  };

  return (
    <div className="min-h-screen bg-background">
      {/* Sidebar */}
      <div className="fixed inset-y-0 left-0 w-64 bg-sidebar border-r border-sidebar-border overflow-y-auto">
        {/* Logo */}
        <div className="flex items-center px-6 py-6 border-b border-sidebar-border">
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
        <div className="px-6 py-4 border-b border-sidebar-border">
          <div className="flex items-center space-x-2 text-sm">
            <div className="flex items-center space-x-2 px-3 py-2 bg-sidebar-accent rounded-lg">
              <div className="w-2 h-2 bg-success rounded-full animate-pulse" />
              <span className="text-sidebar-foreground text-xs">System Online</span>
            </div>
          </div>
        </div>

        {/* Navigation */}
        <nav className="px-3 py-4 space-y-2">
          {navigationSections.map((section) => {
            const isCollapsed = collapsedSections.has(section.title);
            return (
              <div key={section.title}>
                <button
                  onClick={() => toggleSection(section.title)}
                  className="flex items-center justify-between w-full px-3 py-2 text-xs font-semibold text-sidebar-foreground/70 hover:text-sidebar-foreground transition-colors"
                >
                  <span>{section.title}</span>
                  {isCollapsed ? (
                    <ChevronRight className="w-3 h-3" />
                  ) : (
                    <ChevronDown className="w-3 h-3" />
                  )}
                </button>
                {!isCollapsed && (
                  <div className="space-y-1 mt-1">
                    {section.items.map((item) => {
                      const isActive = pathname === item.href;
                      return (
                        <Link
                          key={item.name}
                          href={item.href}
                          className={cn(
                            'flex items-center space-x-3 px-3 py-2 rounded-lg text-sm font-medium transition-all duration-200',
                            isActive
                              ? 'bg-sidebar-primary text-sidebar-primary-foreground shadow-primary'
                              : 'text-sidebar-foreground hover:bg-sidebar-accent hover:text-sidebar-accent-foreground'
                          )}
                        >
                          <item.icon className="w-4 h-4" />
                          <span>{item.name}</span>
                        </Link>
                      );
                    })}
                  </div>
                )}
              </div>
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
              <span>Built with Next.js</span>
            </div>
          </div>
        </div>
      </div>

      {/* Main content */}
      <div className="pl-64">
        <main className="p-8">
          {children}
        </main>
      </div>
    </div>
  );
};

export default Layout;
