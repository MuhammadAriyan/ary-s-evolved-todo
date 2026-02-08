// Search results page with highlighting and filters
'use client';

import { useState, useEffect } from 'react';
import { useSearchParams, useRouter } from 'next/navigation';
import { Search, Filter, Clock, Tag, AlertCircle } from 'lucide-react';
import dynamic from 'next/dynamic';
import { Skeleton } from '@/components/ui/skeleton';

// Dynamic import for SearchBar to reduce initial bundle size (T055)
const SearchBar = dynamic(() => import('@/components/search/SearchBar'), {
  ssr: false,
  loading: () => <Skeleton className="h-10 w-full bg-white/10" />,
});

interface Task {
  id: number;
  title: string;
  description: string;
  completed: boolean;
  priority: string;
  tags: string[];
  due_date: string | null;
  created_at: string;
}

interface SearchResult {
  task: Task;
  score: number;
  highlighted_title: string;
  highlighted_description: string;
}

interface SearchResponse {
  results: SearchResult[];
  total: number;
  query: string;
  filters_applied: {
    status?: string;
    priority?: string;
    tags?: string[];
    date_from?: string;
    date_to?: string;
    fuzzy?: boolean;
  };
}

export default function SearchResultsPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [results, setResults] = useState<SearchResult[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [searchResponse, setSearchResponse] = useState<SearchResponse | null>(null);

  const query = searchParams.get('q') || '';
  const status = searchParams.get('status');
  const priority = searchParams.get('priority');
  const tags = searchParams.get('tags')?.split(',').filter(Boolean);
  const dateFrom = searchParams.get('dateFrom');
  const dateTo = searchParams.get('dateTo');
  const fuzzy = searchParams.get('fuzzy') === 'true';

  // Fetch search results
  useEffect(() => {
    if (!query) return;

    const fetchResults = async () => {
      setIsLoading(true);
      setError(null);

      try {
        const params = new URLSearchParams({ q: query });
        if (status) params.append('status', status);
        if (priority) params.append('priority', priority);
        if (tags?.length) tags.forEach(tag => params.append('tags', tag));
        if (dateFrom) params.append('date_from', dateFrom);
        if (dateTo) params.append('date_to', dateTo);
        if (fuzzy) params.append('fuzzy', 'true');

        const response = await fetch(`/api/v1/search/tasks?${params.toString()}`, {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          }
        });

        if (!response.ok) {
          throw new Error('Search failed');
        }

        const data: SearchResponse = await response.json();
        setSearchResponse(data);
        setResults(data.results);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Search failed');
      } finally {
        setIsLoading(false);
      }
    };

    fetchResults();
  }, [query, status, priority, tags, dateFrom, dateTo, fuzzy]);

  // Handle task click
  const handleTaskClick = (taskId: number) => {
    router.push(`/tasks/${taskId}`);
  };

  // Get priority badge color
  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'High':
        return 'bg-red-100 text-red-800';
      case 'Medium':
        return 'bg-yellow-100 text-yellow-800';
      case 'Low':
        return 'bg-green-100 text-green-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-4xl mx-auto px-4">
        {/* Search Bar */}
        <div className="mb-8">
          <SearchBar autoFocus={false} showFilters={true} />
        </div>

        {/* Search Info */}
        {searchResponse && (
          <div className="mb-6 flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">
                Search Results
              </h1>
              <p className="text-gray-600 mt-1">
                Found {searchResponse.total} result{searchResponse.total !== 1 ? 's' : ''} for "{searchResponse.query}"
              </p>
            </div>

            {/* Active Filters */}
            {(searchResponse.filters_applied.status ||
              searchResponse.filters_applied.priority ||
              searchResponse.filters_applied.tags?.length ||
              searchResponse.filters_applied.fuzzy) && (
              <div className="flex items-center space-x-2">
                <Filter className="w-4 h-4 text-gray-400" />
                <span className="text-sm text-gray-600">Filters active</span>
              </div>
            )}
          </div>
        )}

        {/* Loading State */}
        {isLoading && (
          <div className="flex items-center justify-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
          </div>
        )}

        {/* Error State */}
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 flex items-start space-x-3">
            <AlertCircle className="w-5 h-5 text-red-600 mt-0.5" />
            <div>
              <h3 className="text-red-800 font-medium">Search Error</h3>
              <p className="text-red-600 text-sm mt-1">{error}</p>
            </div>
          </div>
        )}

        {/* No Results */}
        {!isLoading && !error && results.length === 0 && query && (
          <div className="bg-white rounded-lg shadow-sm p-8 text-center">
            <Search className="w-12 h-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">
              No results found
            </h3>
            <p className="text-gray-600">
              Try adjusting your search query or filters
            </p>
          </div>
        )}

        {/* Search Results */}
        {!isLoading && !error && results.length > 0 && (
          <div className="space-y-4">
            {results.map((result) => (
              <div
                key={result.task.id}
                onClick={() => handleTaskClick(result.task.id)}
                className="bg-white rounded-lg shadow-sm p-6 hover:shadow-md transition-shadow cursor-pointer"
              >
                {/* Task Header */}
                <div className="flex items-start justify-between mb-3">
                  <div className="flex-1">
                    {/* Highlighted Title */}
                    <h3
                      className="text-lg font-semibold text-gray-900 mb-2"
                      dangerouslySetInnerHTML={{
                        __html: result.highlighted_title || result.task.title
                      }}
                    />

                    {/* Highlighted Description */}
                    {result.highlighted_description && (
                      <p
                        className="text-gray-600 text-sm"
                        dangerouslySetInnerHTML={{
                          __html: result.highlighted_description
                        }}
                      />
                    )}
                  </div>

                  {/* Relevance Score */}
                  <div className="ml-4 flex-shrink-0">
                    <div className="text-xs text-gray-500">
                      Score: {result.score.toFixed(2)}
                    </div>
                  </div>
                </div>

                {/* Task Metadata */}
                <div className="flex items-center space-x-4 text-sm text-gray-500">
                  {/* Priority Badge */}
                  <span className={`px-2 py-1 rounded-full text-xs font-medium ${getPriorityColor(result.task.priority)}`}>
                    {result.task.priority}
                  </span>

                  {/* Status */}
                  <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                    result.task.completed
                      ? 'bg-green-100 text-green-800'
                      : 'bg-blue-100 text-blue-800'
                  }`}>
                    {result.task.completed ? 'Completed' : 'Pending'}
                  </span>

                  {/* Due Date */}
                  {result.task.due_date && (
                    <div className="flex items-center space-x-1">
                      <Clock className="w-4 h-4" />
                      <span>{new Date(result.task.due_date).toLocaleDateString()}</span>
                    </div>
                  )}

                  {/* Tags */}
                  {result.task.tags.length > 0 && (
                    <div className="flex items-center space-x-1">
                      <Tag className="w-4 h-4" />
                      <span>{result.task.tags.slice(0, 3).join(', ')}</span>
                      {result.task.tags.length > 3 && (
                        <span className="text-gray-400">+{result.task.tags.length - 3}</span>
                      )}
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Custom styles for highlighting */}
      <style jsx global>{`
        mark {
          background-color: #fef08a;
          color: inherit;
          padding: 0 2px;
          border-radius: 2px;
        }
      `}</style>
    </div>
  );
}
