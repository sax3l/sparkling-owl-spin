'use client';

import React from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { useTranslation } from '@/hooks/useTranslation';
import { cn } from '@/lib/utils';
import {
  Home,
  Database,
  Settings,
  Users,
  FileText,
  BarChart3,
  Shield,
  Download,
  Upload,
  Activity,
  Globe,
  Clock,
  X
} from 'lucide-react';

interface SidebarProps {
  isOpen: boolean;
  onClose?: () => void;
}

const Sidebar: React.FC<SidebarProps> = ({ isOpen, onClose }) => {
  const { t } = useTranslation();
  const pathname = usePathname();

  const menuItems = [
    {
      href: '/',
      icon: Home,
      label: t('navigation.dashboard'),
      category: 'main'
    },
    {
      href: '/crawlers',
      icon: Globe,
      label: t('navigation.crawlers'),
      category: 'main'
    },
    {
      href: '/data',
      icon: Database,
      label: t('navigation.dataManagement'),
      category: 'main'
    },
    {
      href: '/exports',
      icon: Download,
      label: t('navigation.exports'),
      category: 'main'
    },
    {
      href: '/imports',
      icon: Upload,
      label: t('navigation.imports'),
      category: 'main'
    },
    {
      href: '/monitoring',
      icon: Activity,
      label: t('navigation.monitoring'),
      category: 'monitoring'
    },
    {
      href: '/analytics',
      icon: BarChart3,
      label: t('navigation.analytics'),
      category: 'monitoring'
    },
    {
      href: '/logs',
      icon: FileText,
      label: t('navigation.logs'),
      category: 'monitoring'
    },
    {
      href: '/history',
      icon: Clock,
      label: t('navigation.history'),
      category: 'monitoring'
    },
    {
      href: '/users',
      icon: Users,
      label: t('navigation.userManagement'),
      category: 'admin'
    },
    {
      href: '/security',
      icon: Shield,
      label: t('navigation.security'),
      category: 'admin'
    },
    {
      href: '/settings',
      icon: Settings,
      label: t('navigation.settings'),
      category: 'admin'
    }
  ];

  const categories = {
    main: t('navigation.categories.main'),
    monitoring: t('navigation.categories.monitoring'),
    admin: t('navigation.categories.admin')
  };

  const groupedItems = menuItems.reduce((acc, item) => {
    if (!acc[item.category]) {
      acc[item.category] = [];
    }
    acc[item.category].push(item);
    return acc;
  }, {} as Record<string, typeof menuItems>);

  return (
    <>
      {/* Mobile backdrop */}
      {isOpen && (
        <div
          className="fixed inset-0 bg-black bg-opacity-50 z-20 lg:hidden"
          onClick={onClose}
        />
      )}

      {/* Sidebar */}
      <div
        className={cn(
          'fixed left-0 top-0 z-30 h-full w-64 bg-white dark:bg-gray-800 shadow-lg transform transition-transform duration-300 ease-in-out lg:translate-x-0 lg:static lg:inset-0',
          isOpen ? 'translate-x-0' : '-translate-x-full'
        )}
      >
        {/* Mobile close button */}
        {onClose && (
          <div className="flex justify-end p-4 lg:hidden">
            <button
              onClick={onClose}
              className="text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200"
            >
              <X size={24} />
            </button>
          </div>
        )}

        {/* Navigation */}
        <nav className="flex-1 px-4 pb-4 space-y-6">
          {Object.entries(groupedItems).map(([category, items]) => (
            <div key={category}>
              <h3 className="px-3 text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                {categories[category as keyof typeof categories]}
              </h3>
              <div className="mt-2 space-y-1">
                {items.map((item) => {
                  const isActive = pathname === item.href;
                  return (
                    <Link
                      key={item.href}
                      href={item.href}
                      onClick={onClose}
                      className={cn(
                        'group flex items-center px-3 py-2 text-sm font-medium rounded-md transition-colors',
                        isActive
                          ? 'bg-blue-100 text-blue-700 dark:bg-blue-900 dark:text-blue-200'
                          : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900 dark:text-gray-300 dark:hover:bg-gray-700 dark:hover:text-white'
                      )}
                    >
                      <item.icon
                        className={cn(
                          'mr-3 flex-shrink-0 h-5 w-5',
                          isActive
                            ? 'text-blue-500 dark:text-blue-300'
                            : 'text-gray-400 group-hover:text-gray-500 dark:group-hover:text-gray-300'
                        )}
                      />
                      {item.label}
                    </Link>
                  );
                })}
              </div>
            </div>
          ))}
        </nav>
      </div>
    </>
  );
};

export { Sidebar };
