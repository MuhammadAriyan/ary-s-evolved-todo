// Audit log viewer component with timeline display.
'use client';

import { useState, useEffect } from 'react';
import { Clock, User, FileText, Download, ChevronDown, ChevronUp } from 'lucide-react';

interface AuditLog {
  id: number;
  event_id: string;
  event_type: string;
  task_id: string;
  user_id: string;
  operation: string;
  before_state: Record<string, any> | null;
  after_state: Record<string, any> | null;
  ip_address: string | null;
  user_agent: string | null;
  timestamp: string;
  created_at: string;
}

interface AuditLogViewerProps {
  taskId: string;
  maxHeight?: string;
}

export default function AuditLogViewer({ taskId, maxHeight = '600px' }: AuditLogViewerProps) {
  const [logs, setLogs] = useState<AuditLog[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [expandedLogs, setExpandedLogs] = useState<Set<number>>(new Set());
  const [isExporting, setIsExporting] = useState(false);

  // Fetch audit logs
  useEffect(() => {
    const fetchLogs = async () => {
      setIsLoading(true);
      setError(null);

      try {
        const response = await fetch(`/api/v1/audit/tasks/${taskId}`, {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          }
        });

        if (!response.ok) {
          throw new Error('Failed to fetch audit logs');
        }

        const data = await response.json();
        setLogs(data.logs);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to fetch audit logs');
      } finally {
        setIsLoading(false);
      }
    };

    fetchLogs();
  }, [taskId]);

  // Toggle log expansion
  const toggleLogExpansion = (logId: number) => {
    const newExpanded = new Set(expandedLogs);
    if (newExpanded.has(logId)) {
      newExpanded.delete(logId);
    } else {
      newExpanded.add(logId);
    }
    setExpandedLogs(newExpanded);
  };

  // Export audit logs
  const handleExport = async (format: 'json' | 'csv') => {
    setIsExporting(true);

    try {
      const response = await fetch('/api/v1/audit/export', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          format,
          task_id: taskId
        })
      });

      if (!response.ok) {
        throw new Error('Export failed');
      }

      // Download file
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `audit_logs_${taskId}_${Date.now()}.${format}`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (err) {
      console.error('Export failed:', err);
      alert('Failed to export audit logs');
    } finally {
      setIsExporting(false);
    }
  };

  // Get operation color
  const getOperationColor = (operation: string) => {
    switch (operation) {
      case 'created':
        return 'bg-green-100 text-green-800';
      case 'updated':
        return 'bg-blue-100 text-blue-800';
      case 'deleted':
        return 'bg-red-100 text-red-800';
      case 'completed':
        return 'bg-purple-100 text-purple-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  // Get changed fields
  const getChangedFields = (log: AuditLog): string[] => {
    if (!log.before_state || !log.after_state) return [];

    const changes: string[] = [];
    const allKeys = new Set([
      ...Object.keys(log.before_state),
      ...Object.keys(log.after_state)
    ]);

    allKeys.forEach(key => {
      const before = log.before_state?.[key];
      const after = log.after_state?.[key];
      if (JSON.stringify(before) !== JSON.stringify(after)) {
        changes.push(key);
      }
    });

    return changes;
  };

  // Format timestamp
  const formatTimestamp = (timestamp: string) => {
    const date = new Date(timestamp);
    return date.toLocaleString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-red-800">
        {error}
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-sm">
      {/* Header */}
      <div className="px-6 py-4 border-b border-gray-200 flex items-center justify-between">
        <div>
          <h3 className="text-lg font-semibold text-gray-900">Audit Trail</h3>
          <p className="text-sm text-gray-600 mt-1">
            {logs.length} change{logs.length !== 1 ? 's' : ''} recorded
          </p>
        </div>

        {/* Export Buttons */}
        <div className="flex space-x-2">
          <button
            onClick={() => handleExport('json')}
            disabled={isExporting || logs.length === 0}
            className="flex items-center space-x-2 px-3 py-2 text-sm border border-gray-300 rounded-md hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <Download className="w-4 h-4" />
            <span>JSON</span>
          </button>
          <button
            onClick={() => handleExport('csv')}
            disabled={isExporting || logs.length === 0}
            className="flex items-center space-x-2 px-3 py-2 text-sm border border-gray-300 rounded-md hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <Download className="w-4 h-4" />
            <span>CSV</span>
          </button>
        </div>
      </div>

      {/* Timeline */}
      <div className="overflow-y-auto" style={{ maxHeight }}>
        {logs.length === 0 ? (
          <div className="px-6 py-8 text-center text-gray-500">
            <FileText className="w-12 h-12 mx-auto mb-3 text-gray-400" />
            <p>No audit logs found for this task</p>
          </div>
        ) : (
          <div className="px-6 py-4">
            {logs.map((log, index) => {
              const isExpanded = expandedLogs.has(log.id);
              const changedFields = getChangedFields(log);

              return (
                <div key={log.id} className="relative">
                  {/* Timeline Line */}
                  {index < logs.length - 1 && (
                    <div className="absolute left-4 top-10 bottom-0 w-0.5 bg-gray-200" />
                  )}

                  {/* Log Entry */}
                  <div className="flex space-x-4 mb-6">
                    {/* Timeline Dot */}
                    <div className="flex-shrink-0 w-8 h-8 rounded-full bg-blue-100 flex items-center justify-center relative z-10">
                      <Clock className="w-4 h-4 text-blue-600" />
                    </div>

                    {/* Log Content */}
                    <div className="flex-1 bg-gray-50 rounded-lg p-4">
                      {/* Log Header */}
                      <div className="flex items-start justify-between mb-2">
                        <div className="flex items-center space-x-2">
                          <span className={`px-2 py-1 rounded-full text-xs font-medium ${getOperationColor(log.operation)}`}>
                            {log.operation}
                          </span>
                          <span className="text-sm text-gray-600">
                            {formatTimestamp(log.timestamp)}
                          </span>
                        </div>

                        {changedFields.length > 0 && (
                          <button
                            onClick={() => toggleLogExpansion(log.id)}
                            className="text-gray-400 hover:text-gray-600"
                          >
                            {isExpanded ? (
                              <ChevronUp className="w-5 h-5" />
                            ) : (
                              <ChevronDown className="w-5 h-5" />
                            )}
                          </button>
                        )}
                      </div>

                      {/* Changed Fields Summary */}
                      {changedFields.length > 0 && (
                        <div className="text-sm text-gray-700 mb-2">
                          Changed: {changedFields.join(', ')}
                        </div>
                      )}

                      {/* Expanded Details */}
                      {isExpanded && (log.before_state || log.after_state) && (
                        <div className="mt-3 space-y-2">
                          {changedFields.map(field => (
                            <div key={field} className="bg-white rounded p-3 text-sm">
                              <div className="font-medium text-gray-700 mb-1">{field}</div>
                              <div className="grid grid-cols-2 gap-4">
                                <div>
                                  <div className="text-xs text-gray-500 mb-1">Before</div>
                                  <div className="text-gray-900 font-mono text-xs">
                                    {JSON.stringify(log.before_state?.[field], null, 2)}
                                  </div>
                                </div>
                                <div>
                                  <div className="text-xs text-gray-500 mb-1">After</div>
                                  <div className="text-gray-900 font-mono text-xs">
                                    {JSON.stringify(log.after_state?.[field], null, 2)}
                                  </div>
                                </div>
                              </div>
                            </div>
                          ))}
                        </div>
                      )}

                      {/* Metadata */}
                      {log.ip_address && (
                        <div className="mt-2 text-xs text-gray-500">
                          IP: {log.ip_address}
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}
