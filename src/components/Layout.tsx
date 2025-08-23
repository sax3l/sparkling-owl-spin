'use client'

import React, { useState } from 'react'
import Link from 'next/link'
import { 
  ChevronLeft, 
  ChevronRight,
  Home,
  Database,
  Car,
  Users,
  Building,
  BarChart3,
  Shield,
  Server,
  Target,
  Settings,
  Activity,
  Globe,
  Eye,
  Download,
  Clock,
  AlertTriangle,
  CheckCircle,
  XCircle
} from 'lucide-react'

interface NavigationItem {
  name: string
  href: string
  icon: React.ComponentType<any>
  description?: string
}

interface NavigationSection {
  title: string
  items: NavigationItem[]
}

const navigationSections: NavigationSection[] = [
  {
    title: "Dashboard",
    items: [
      { name: "Översikt", href: "/", icon: Home, description: "Huvuddashboard" }
    ]
  },
  {
    title: "Data Management",
    items: [
      { name: "Fastigheter", href: "/data/properties", icon: Database, description: "Fastighetsdata" },
      { name: "Fordon", href: "/data/vehicles", icon: Car, description: "Fordonsdata" },
      { name: "Personer", href: "/data/persons", icon: Users, description: "Persondata" },
      { name: "Företag", href: "/data/companies", icon: Building, description: "Företagsdata" }
    ]
  },
  {
    title: "Analytics & Reports",
    items: [
      { name: "Användaranalys", href: "/analytics", icon: BarChart3, description: "Dataanalys" },
      { name: "Export Data", href: "/export", icon: Download, description: "Dataexport" },
      { name: "Schemaläggning", href: "/scheduling", icon: Clock, description: "Automatisering" }
    ]
  },
  {
    title: "System Configuration",
    items: [
      { name: "Proxies", href: "/proxies", icon: Server, description: "Proxy-hantering" },
      { name: "Anti-Bot", href: "/anti-bot", icon: Shield, description: "Bot-skydd" },
      { name: "Selector Studio", href: "/selector-studio", icon: Target, description: "CSS-selektorer" },
      { name: "Inställningar", href: "/settings", icon: Settings, description: "Systemkonfiguration" }
    ]
  },
  {
    title: "Monitoring",
    items: [
      { name: "Systemstatus", href: "/monitoring", icon: Activity, description: "Övervakningsdashboard" },
      { name: "Global Status", href: "/global-status", icon: Globe, description: "Global systemstatus" },
      { name: "Observability", href: "/observability", icon: Eye, description: "Systeminsyn" }
    ]
  }
]

interface LayoutProps {
  children: React.ReactNode
}

export default function Layout({ children }: LayoutProps) {
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false)

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'success': return 'text-green-500'
      case 'warning': return 'text-yellow-500'
      case 'error': return 'text-red-500'
      default: return 'text-gray-500'
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'success': return CheckCircle
      case 'warning': return AlertTriangle
      case 'error': return XCircle
      default: return Activity
    }
  }

  return (
    <div className="min-h-screen bg-gray-50 flex">
      {/* Sidebar */}
      <div className={`bg-white shadow-lg transition-all duration-300 ${sidebarCollapsed ? 'w-16' : 'w-64'}`}>
        <div className="flex flex-col h-full">
          {/* Header */}
          <div className="p-4 border-b border-gray-200">
            <div className="flex items-center justify-between">
              {!sidebarCollapsed && (
                <div>
                  <h1 className="text-xl font-bold text-gray-900">ECaDP</h1>
                  <p className="text-sm text-gray-600">Enhanced Crawler Platform</p>
                </div>
              )}
              <button
                onClick={() => setSidebarCollapsed(!sidebarCollapsed)}
                className="p-1 rounded-lg hover:bg-gray-100 transition-colors"
              >
                {sidebarCollapsed ? (
                  <ChevronRight className="w-5 h-5 text-gray-600" />
                ) : (
                  <ChevronLeft className="w-5 h-5 text-gray-600" />
                )}
              </button>
            </div>
          </div>

          {/* Navigation */}
          <div className="flex-1 overflow-y-auto py-4">
            {navigationSections.map((section, sectionIndex) => (
              <div key={sectionIndex} className="mb-6">
                {!sidebarCollapsed && (
                  <div className="px-4 mb-2">
                    <h2 className="text-xs font-semibold text-gray-400 uppercase tracking-wider">
                      {section.title}
                    </h2>
                  </div>
                )}
                
                <nav className="space-y-1 px-2">
                  {section.items.map((item, itemIndex) => {
                    const Icon = item.icon
                    return (
                      <Link
                        key={itemIndex}
                        href={item.href}
                        className="group flex items-center px-2 py-2 text-sm font-medium rounded-md text-gray-700 hover:bg-gray-100 hover:text-gray-900 transition-colors"
                      >
                        <Icon className={`flex-shrink-0 w-5 h-5 text-gray-400 group-hover:text-gray-500 ${sidebarCollapsed ? '' : 'mr-3'}`} />
                        {!sidebarCollapsed && (
                          <div className="flex-1">
                            <div className="text-sm font-medium">{item.name}</div>
                            {item.description && (
                              <div className="text-xs text-gray-500">{item.description}</div>
                            )}
                          </div>
                        )}
                      </Link>
                    )
                  })}
                </nav>
              </div>
            ))}
          </div>

          {/* Footer Status */}
          <div className="p-4 border-t border-gray-200">
            {!sidebarCollapsed && (
              <div className="space-y-2">
                <div className="text-xs font-semibold text-gray-400 uppercase tracking-wider">
                  System Status
                </div>
                <div className="space-y-1">
                  <div className="flex items-center text-sm">
                    <CheckCircle className="w-4 h-4 text-green-500 mr-2" />
                    <span className="text-gray-700">Crawler: Online</span>
                  </div>
                  <div className="flex items-center text-sm">
                    <CheckCircle className="w-4 h-4 text-green-500 mr-2" />
                    <span className="text-gray-700">Database: Connected</span>
                  </div>
                  <div className="flex items-center text-sm">
                    <AlertTriangle className="w-4 h-4 text-yellow-500 mr-2" />
                    <span className="text-gray-700">Proxies: 12/15</span>
                  </div>
                </div>
              </div>
            )}
            {sidebarCollapsed && (
              <div className="flex flex-col items-center space-y-2">
                <CheckCircle className="w-4 h-4 text-green-500" />
                <CheckCircle className="w-4 h-4 text-green-500" />
                <AlertTriangle className="w-4 h-4 text-yellow-500" />
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex flex-col overflow-hidden">
        <main className="flex-1 overflow-y-auto">
          {children}
        </main>
      </div>
    </div>
  )
}
