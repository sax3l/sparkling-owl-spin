import React, { useState, useEffect } from 'react';
import { submitExport, listExports, getExportStatus, getDirectData } from '../api/client';
import { ExportCreate, ExportRead, JobStatus } from '../api/types';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { useToast } from '@/components/ui/use-toast'; // Assuming you have a toast component

const Exports: React.FC = () => {
  const { toast } = useToast();
  const [exportType, setExportType] = useState<string>('person');
  const [format, setFormat] = useState<ExportCreate['format']>('csv');
  const [compress, setCompress] = useState<ExportCreate['compress']>('none');
  const [fileNamePrefix, setFileNamePrefix] = useState<string>('');
  const [filters, setFilters] = useState<string>('{}'); // JSON string for filters
  const [exports, setExports] = useState<ExportRead[]>([]);
  const [loading, setLoading] = useState<boolean>(false);

  const fetchExports = async () => {
    setLoading(true);
    try {
      const data = await listExports();
      setExports(data);
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to load exports.",
        variant: "destructive",
      });
      console.error("Error fetching exports:", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchExports();
    const interval = setInterval(fetchExports, 5000); // Poll every 5 seconds
    return () => clearInterval(interval);
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      const parsedFilters = JSON.parse(filters);
      const newExport: ExportCreate = {
        export_type: exportType,
        format,
        compress,
        destination: { type: 'supabase_storage', retention_hours: 72 },
        file_name_prefix: fileNamePrefix || undefined,
        filters: parsedFilters,
      };
      const result = await submitExport(newExport);
      setExports((prev) => [result, ...prev]);
      toast({
        title: "Export Initiated",
        description: `Export job ${result.id} has been queued.`,
      });
    } catch (error: any) {
      toast({
        title: "Error",
        description: `Failed to initiate export: ${error.message || 'Unknown error'}`,
        variant: "destructive",
      });
      console.error("Error submitting export:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleDownload = async (exportJob: ExportRead) => {
    if (exportJob.download_url) {
      window.open(exportJob.download_url, '_blank');
    } else {
      toast({
        title: "Not Ready",
        description: "The export file is not yet available for download.",
        variant: "warning",
      });
    }
  };

  const handleDirectDownload = async () => {
    setLoading(true);
    try {
      const parsedFilters = JSON.parse(filters);
      const response = await getDirectData(exportType, format, parsedFilters, compress === 'gzip');
      
      const blob = await response.blob();
      const contentDisposition = response.headers.get('Content-Disposition');
      let filename = `${exportType}_data.${format}`;
      if (compress === 'gzip') filename += '.gz';

      if (contentDisposition) {
        const filenameMatch = contentDisposition.match(/filename="([^"]+)"/);
        if (filenameMatch && filenameMatch[1]) {
          filename = filenameMatch[1];
        }
      }

      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      a.remove();
      window.URL.revokeObjectURL(url);
      toast({
        title: "Download Started",
        description: `Direct download of ${filename} initiated.`,
      });
    } catch (error: any) {
      toast({
        title: "Error",
        description: `Failed to initiate direct download: ${error.message || 'Unknown error'}`,
        variant: "destructive",
      });
      console.error("Error initiating direct download:", error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-8">
      <Card>
        <CardHeader>
          <CardTitle>Initiate New Export</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="exportType">Export Type</Label>
              <Select value={exportType} onValueChange={setExportType}>
                <SelectTrigger id="exportType">
                  <SelectValue placeholder="Select export type" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="person">Person</SelectItem>
                  <SelectItem value="company">Company</SelectItem>
                  <SelectItem value="vehicle">Vehicle</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label htmlFor="format">Format</Label>
              <Select value={format} onValueChange={setFormat}>
                <SelectTrigger id="format">
                  <SelectValue placeholder="Select format" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="csv">CSV</SelectItem>
                  <SelectItem value="json">JSON</SelectItem>
                  <SelectItem value="ndjson">NDJSON</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label htmlFor="compress">Compression</Label>
              <Select value={compress} onValueChange={setCompress}>
                <SelectTrigger id="compress">
                  <SelectValue placeholder="Select compression" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="none">None</SelectItem>
                  <SelectItem value="gzip">Gzip</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label htmlFor="fileNamePrefix">File Name Prefix (Optional)</Label>
              <Input
                id="fileNamePrefix"
                value={fileNamePrefix}
                onChange={(e) => setFileNamePrefix(e.target.value)}
                placeholder="e.g., my_data"
              />
            </div>

            <div className="space-y-2 md:col-span-2">
              <Label htmlFor="filters">Filters (JSON)</Label>
              <Input
                id="filters"
                value={filters}
                onChange={(e) => setFilters(e.target.value)}
                placeholder='{"status": "active"}'
              />
            </div>

            <div className="md:col-span-2 flex gap-4">
              <Button type="submit" disabled={loading}>
                {loading ? 'Initiating...' : 'Initiate Async Export'}
              </Button>
              <Button type="button" onClick={handleDirectDownload} disabled={loading} variant="outline">
                {loading ? 'Downloading...' : 'Direct Download (Small Data)'}
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Export History</CardTitle>
        </CardHeader>
        <CardContent>
          {loading && exports.length === 0 ? (
            <p>Loading exports...</p>
          ) : exports.length === 0 ? (
            <p>No export jobs found.</p>
          ) : (
            <div className="overflow-x-auto">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>ID</TableHead>
                    <TableHead>Type</TableHead>
                    <TableHead>File Name</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead>Created At</TableHead>
                    <TableHead>Expires At</TableHead>
                    <TableHead>Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {exports.map((exp) => (
                    <TableRow key={exp.id}>
                      <TableCell className="font-medium">{exp.id.substring(0, 8)}...</TableCell>
                      <TableCell>{exp.export_type}</TableCell>
                      <TableCell>{exp.file_name}</TableCell>
                      <TableCell>
                        <span
                          className={`px-2 py-1 rounded-full text-xs font-semibold ${
                            exp.status === JobStatus.COMPLETED
                              ? 'bg-green-100 text-green-800'
                              : exp.status === JobStatus.FAILED
                              ? 'bg-red-100 text-red-800'
                              : 'bg-yellow-100 text-yellow-800'
                          }`}
                        >
                          {exp.status}
                        </span>
                      </TableCell>
                      <TableCell>{new Date(exp.created_at).toLocaleString()}</TableCell>
                      <TableCell>{exp.expires_at ? new Date(exp.expires_at).toLocaleString() : 'N/A'}</TableCell>
                      <TableCell>
                        {exp.status === JobStatus.COMPLETED && exp.download_url ? (
                          <Button onClick={() => handleDownload(exp)} size="sm">
                            Download
                          </Button>
                        ) : (
                          <Button size="sm" disabled>
                            Download
                          </Button>
                        )}
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
};

export default Exports;