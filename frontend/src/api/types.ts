export enum JobType {
  CRAWL = "crawl",
  SCRAPE = "scrape",
}

export interface Job {
  id: string;
  task: {
    start_url: string;
    job_type: JobType;
  };
  status: string;
}