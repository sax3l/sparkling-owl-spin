import { useState } from 'react';
import { submitJob } from '../api/client';
import { JobType } from '../api/types';

const JobLauncher = () => {
  const [url, setUrl] = useState('');
  const [jobType, setJobType] = useState<JobType>(JobType.CRAWL);
  const [submitting, setSubmitting] = useState(false);
  const [feedback, setFeedback] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!url) {
      setFeedback('Please enter a URL.');
      return;
    }
    setSubmitting(true);
    setFeedback('Submitting job...');
    try {
      const result = await submitJob(url, jobType);
      setFeedback(`Job submitted successfully! Job ID: ${result.id}`);
      setUrl('');
    } catch (error) {
      setFeedback('Failed to submit job. See console for details.');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-md">
      <h2 className="text-2xl font-bold mb-4">Job Launcher</h2>
      <form onSubmit={handleSubmit}>
        <div className="mb-4">
          <label htmlFor="url" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            Start URL
          </label>
          <input
            type="text"
            id="url"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 dark:bg-gray-700 dark:border-gray-600"
            placeholder="https://example.com"
          />
        </div>
        <div className="mb-4">
          <label htmlFor="jobType" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            Job Type
          </label>
          <select
            id="jobType"
            value={jobType}
            onChange={(e) => setJobType(e.target.value as JobType)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 dark:bg-gray-700 dark:border-gray-600"
          >
            <option value={JobType.CRAWL}>Crawl</option>
            <option value={JobType.SCRAPE}>Scrape</option>
          </select>
        </div>
        <button
          type="submit"
          disabled={submitting}
          className="w-full bg-indigo-600 text-white py-2 px-4 rounded-md hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:bg-gray-400"
        >
          {submitting ? 'Submitting...' : 'Launch Job'}
        </button>
      </form>
      {feedback && <p className="mt-4 text-sm text-gray-600 dark:text-gray-400">{feedback}</p>}
    </div>
  );
};

export default JobLauncher;