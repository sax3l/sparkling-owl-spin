'use client';

import React from 'react';
import { useTranslation } from '@/hooks/useTranslation';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { 
  Activity, 
  Globe, 
  Database, 
  TrendingUp,
  Users,
  AlertTriangle,
  CheckCircle,
  Clock
} from 'lucide-react';

interface MetricCardProps {
  title: string;
  value: string | number;
  description?: string;
  icon: React.ComponentType<{ size?: number; className?: string }>;
  trend?: {
    value: number;
    isPositive: boolean;
  };
  status?: 'success' | 'warning' | 'error' | 'neutral';
}

const MetricCard: React.FC<MetricCardProps> = ({
  title,
  value,
  description,
  icon: Icon,
  trend,
  status = 'neutral'
}) => {
  const statusColors = {
    success: 'text-green-600 dark:text-green-400',
    warning: 'text-yellow-600 dark:text-yellow-400',
    error: 'text-red-600 dark:text-red-400',
    neutral: 'text-blue-600 dark:text-blue-400'
  };

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-sm font-medium">
          {title}
        </CardTitle>
        <Icon className={`h-4 w-4 ${statusColors[status]}`} />
      </CardHeader>
      <CardContent>
        <div className="text-2xl font-bold">{value}</div>
        {description && (
          <p className="text-xs text-muted-foreground">
            {description}
          </p>
        )}
        {trend && (
          <div className="flex items-center text-xs">
            <TrendingUp 
              className={`mr-1 h-3 w-3 ${
                trend.isPositive ? 'text-green-500' : 'text-red-500'
              }`} 
            />
            <span className={trend.isPositive ? 'text-green-600' : 'text-red-600'}>
              {trend.isPositive ? '+' : ''}{trend.value}%
            </span>
            <span className="text-muted-foreground ml-1">from last month</span>
          </div>
        )}
      </CardContent>
    </Card>
  );
};

const DashboardMetrics: React.FC = () => {
  const { t } = useTranslation();
  
  // Mock data - replace with real API calls
  const metrics = [
    {
      title: t('dashboard.metrics.activeCrawlers'),
      value: 12,
      description: t('dashboard.metrics.crawlersRunning'),
      icon: Globe,
      status: 'success' as const,
      trend: { value: 8.2, isPositive: true }
    },
    {
      title: t('dashboard.metrics.totalRecords'),
      value: '2.3M',
      description: t('dashboard.metrics.recordsCollected'),
      icon: Database,
      status: 'neutral' as const,
      trend: { value: 12.5, isPositive: true }
    },
    {
      title: t('dashboard.metrics.systemHealth'),
      value: '98.5%',
      description: t('dashboard.metrics.uptime'),
      icon: Activity,
      status: 'success' as const
    },
    {
      title: t('dashboard.metrics.activeUsers'),
      value: 24,
      description: t('dashboard.metrics.usersOnline'),
      icon: Users,
      status: 'neutral' as const,
      trend: { value: 4.1, isPositive: true }
    }
  ];

  return (
    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
      {metrics.map((metric, index) => (
        <MetricCard key={index} {...metric} />
      ))}
    </div>
  );
};

const SystemStatus: React.FC = () => {
  const { t } = useTranslation();

  // Mock data - replace with real API calls
  const systemServices = [
    {
      name: t('dashboard.services.webCrawler'),
      status: 'operational',
      uptime: '99.9%',
      lastCheck: '2 min ago'
    },
    {
      name: t('dashboard.services.database'),
      status: 'operational',
      uptime: '99.8%',
      lastCheck: '1 min ago'
    },
    {
      name: t('dashboard.services.apiGateway'),
      status: 'operational',
      uptime: '99.7%',
      lastCheck: '3 min ago'
    },
    {
      name: t('dashboard.services.exportService'),
      status: 'maintenance',
      uptime: '98.2%',
      lastCheck: '5 min ago'
    }
  ];

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'operational':
        return <CheckCircle className="h-4 w-4 text-green-500" />;
      case 'maintenance':
        return <AlertTriangle className="h-4 w-4 text-yellow-500" />;
      default:
        return <AlertTriangle className="h-4 w-4 text-red-500" />;
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case 'operational':
        return t('dashboard.status.operational');
      case 'maintenance':
        return t('dashboard.status.maintenance');
      default:
        return t('dashboard.status.down');
    }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center">
          <Activity className="mr-2 h-5 w-5" />
          {t('dashboard.systemStatus')}
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {systemServices.map((service, index) => (
            <div key={index} className="flex items-center justify-between py-2">
              <div className="flex items-center space-x-3">
                {getStatusIcon(service.status)}
                <div>
                  <p className="text-sm font-medium">{service.name}</p>
                  <p className="text-xs text-muted-foreground">
                    {getStatusText(service.status)} • {service.uptime} uptime
                  </p>
                </div>
              </div>
              <div className="text-right">
                <p className="text-xs text-muted-foreground flex items-center">
                  <Clock className="mr-1 h-3 w-3" />
                  {service.lastCheck}
                </p>
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
};

export { DashboardMetrics, SystemStatus };
