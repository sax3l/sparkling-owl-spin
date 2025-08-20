export enum JobType {
  CRAWL = "crawl",
  SCRAPE = "scrape",
  EXPORT = "export", // Added EXPORT job type
}

export enum JobStatus {
  PENDING = "pending",
  QUEUED = "queued",
  RUNNING = "running",
  COMPLETED = "completed",
  FAILED = "failed",
  CANCELLED = "cancelled",
}

export interface Job {
  id: string;
  tenant_id: string;
  job_type: JobType;
  start_url: string;
  status: JobStatus;
  params?: Record<string, any>;
  result?: Record<string, any>;
  created_at: string;
  started_at?: string;
  finished_at?: string;
  links: { self: string };
}

export interface ExportDestination {
  type: "internal_staging" | "s3_presigned" | "gcs_signed" | "supabase_storage";
  retention_hours: number;
}

export interface ExportCreate {
  export_type: string; // e.g., 'person', 'company', 'vehicle'
  filters?: Record<string, any>;
  format: "json" | "csv" | "ndjson";
  compress: "none" | "gzip";
  destination: ExportDestination;
  file_name_prefix?: string;
}

export interface ExportRead {
  id: string;
  user_id?: string;
  export_type: string;
  file_name: string;
  file_size_mb?: number;
  credits_used: number;
  status: JobStatus;
  download_url?: string;
  expires_at?: string;
  created_at: string;
  filters_json?: Record<string, any>;
}