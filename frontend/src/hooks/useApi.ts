// React hooks for API integration
import { useState, useEffect } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient, type ApiResponse } from '../lib/api-client';

// Health check hook
export function useHealthCheck() {
  return useQuery({
    queryKey: ['health'],
    queryFn: () => apiClient.healthCheck(),
    refetchInterval: 30000, // Check every 30 seconds
  });
}

// Jobs hooks
export function useCrawlJobs() {
  return useQuery({
    queryKey: ['crawl-jobs'],
    queryFn: () => apiClient.getCrawlJobs(),
    refetchInterval: 5000, // Refresh every 5 seconds
  });
}

export function useScrapeJobs() {
  return useQuery({
    queryKey: ['scrape-jobs'],
    queryFn: () => apiClient.getScrapeJobs(),
    refetchInterval: 5000,
  });
}

export function useCreateCrawlJob() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (parameters: Record<string, any>) => 
      apiClient.createCrawlJob(parameters),
    onSuccess: () => {
      // Invalidate jobs queries to refresh the list
      queryClient.invalidateQueries({ queryKey: ['crawl-jobs'] });
    },
  });
}

export function useCreateScrapeJob() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (parameters: Record<string, any>) => 
      apiClient.createScrapeJob(parameters),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['scrape-jobs'] });
    },
  });
}

// Exports hooks
export function useExports() {
  return useQuery({
    queryKey: ['exports'],
    queryFn: () => apiClient.getExports(),
    refetchInterval: 10000, // Refresh every 10 seconds
  });
}

export function useCreateExport() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: ({ format, parameters }: { 
      format: string; 
      parameters: Record<string, any> 
    }) => apiClient.createExport(format, parameters),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['exports'] });
    },
  });
}

// Templates hooks
export function useTemplates() {
  return useQuery({
    queryKey: ['templates'],
    queryFn: () => apiClient.getTemplates(),
  });
}

export function useCreateTemplate() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (template: Record<string, any>) => 
      apiClient.createTemplate(template),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['templates'] });
    },
  });
}

// GraphQL hook
export function useGraphQLQuery<T = any>(
  query: string, 
  variables?: Record<string, any>,
  enabled: boolean = true
) {
  return useQuery({
    queryKey: ['graphql', query, variables],
    queryFn: () => apiClient.graphqlQuery<T>(query, variables),
    enabled,
  });
}

// Connection status hook
export function useConnectionStatus() {
  const [isOnline, setIsOnline] = useState(navigator.onLine);
  const { data: healthData } = useHealthCheck();
  
  useEffect(() => {
    const handleOnline = () => setIsOnline(true);
    const handleOffline = () => setIsOnline(false);
    
    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);
    
    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []);
  
  const backendConnected = healthData?.data?.status === 'healthy';
  
  return {
    isOnline,
    backendConnected,
    status: backendConnected ? 'connected' : 'disconnected'
  };
}
