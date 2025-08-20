import { useState } from 'react';
import { submitJob, submitDiagnosticJob } from '../api/client';
import { JobType } from '../api/types';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Textarea } from '@/components/ui/textarea'; // Assuming you have a Textarea component

const JobLauncher = () => {
  const [url, setUrl] = useState('');
  const [jobType, setJobType] = useState<JobType>(JobType.CRAWL);
  const [templateId, setTemplateId] = useState(''); // For scrape/diagnostic jobs
  const [sampleHtml, setSampleHtml] = useState(''); // For diagnostic jobs
  const [submitting, setSubmitting] = useState(false);
  const [feedback, setFeedback] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    setFeedback('Submitting job...');
    try {
      let result;
      if (jobType === JobType.CRAWL) {
        if (!url) {
          setFeedback('Please enter a URL for Crawl job.');
          return;
        }
        result = await submitJob(url, JobType.CRAWL);
      } else if (jobType === JobType.SCRAPE) {
        if (!templateId || !url) {
          setFeedback('Please enter Template ID and URL for Scrape job.');
          return;
        }
        // For simplicity, assuming scrape job uses a single URL from the input field
        result = await submitJob(url, JobType.SCRAPE); // This needs to be updated to use templateId and proper source
      } else if (jobType === JobType.DIAGNOSTIC) {
        if (!templateId || (!url && !sampleHtml)) {
          setFeedback('Please enter Template ID and either a Target URL or Sample HTML for Diagnostic job.');
          return;
        }
        result = await submitDiagnosticJob(templateId, url || undefined, sampleHtml || undefined);
      } else {
        setFeedback('Invalid job type selected.');
        return;
      }
      
      setFeedback(`Job submitted successfully! Job ID: ${result.id}`);
      setUrl('');
      setTemplateId('');
      setSampleHtml('');
    } catch (error) {
      setFeedback('Failed to submit job. See console for details.');
      console.error("Job submission error:", error);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-md">
      <h2 className="text-2xl font-bold mb-4">Job Launcher</h2>
      <form onSubmit={handleSubmit}>
        <div className="mb-4">
          <Label htmlFor="jobType" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            Job Type
          </Label>
          <Select value={jobType} onValueChange={(value: JobType) => setJobType(value)}>
            <SelectTrigger id="jobType">
              <SelectValue placeholder="Select job type" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value={JobType.CRAWL}>Crawl</SelectItem>
              <SelectItem value={JobType.SCRAPE}>Scrape</SelectItem>
              <SelectItem value={JobType.DIAGNOSTIC}>Diagnostic (Template Staging)</SelectItem>
            </SelectContent>
          </Select>
        </div>

        {(jobType === JobType.SCRAPE || jobType === JobType.DIAGNOSTIC) && (
          <div className="mb-4">
            <Label htmlFor="templateId" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Template ID
            </Label>
            <Input
              type="text"
              id="templateId"
              value={templateId}
              onChange={(e) => setTemplateId(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 dark:bg-gray-700 dark:border-gray-600"
              placeholder="e.g., vehicle_detail_v1"
            />
          </div>
        )}

        {(jobType === JobType.CRAWL || jobType === JobType.SCRAPE || jobType === JobType.DIAGNOSTIC) && (
          <div className="mb-4">
            <Label htmlFor="url" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              {jobType === JobType.DIAGNOSTIC ? 'Target URL (Optional)' : 'Start URL'}
            </Label>
            <Input
              type="text"
              id="url"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 dark:bg-gray-700 dark:border-gray-600"
              placeholder="https://example.com"
              disabled={jobType === JobType.DIAGNOSTIC && !!sampleHtml}
            />
          </div>
        )}

        {jobType === JobType.DIAGNOSTIC && (
          <div className="mb-4">
            <Label htmlFor="sampleHtml" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Sample HTML (Optional)
            </Label>
            <Textarea
              id="sampleHtml"
              value={sampleHtml}
              onChange={(e) => setSampleHtml(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 dark:bg-gray-700 dark:border-gray-600"
              placeholder="Paste HTML content here for diagnostic"
              rows={5}
              disabled={!!url}
            />
          </div>
        )}

        <Button
          type="submit"
          disabled={submitting}
          className="w-full bg-indigo-600 text-white py-2 px-4 rounded-md hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:bg-gray-400"
        >
          {submitting ? 'Submitting...' : 'Launch Job'}
        </Button>
      </form>
      {feedback && <p className="mt-4 text-sm text-gray-600 dark:text-gray-400">{feedback}</p>}
    </div>
  );
};

export default JobLauncher;