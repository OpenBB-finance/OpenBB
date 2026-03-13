import React, { useState, useEffect, useRef, useMemo } from 'react';
import { invoke } from '@tauri-apps/api/core';
import { listen } from '@tauri-apps/api/event';
import { useSearch } from '@tanstack/react-router';
import SearchBar from './SearchBar';
import '../styles/jupyter-logs.css';

interface LogEntry {
  timestamp: number;
  content: string;
  process_id: string;
}

const BackendLogsPage: React.FC = () => {
  const search = useSearch({ from: '/backend-logs' });
  const backendId = search.id as string;
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [searchVisible, setSearchVisible] = useState(false);
  const [currentMatchIndex, setCurrentMatchIndex] = useState(0);
  const [caseSensitive, setCaseSensitive] = useState(false);
  const logContainerRef = useRef<HTMLDivElement>(null);
  const searchInputRef = useRef<HTMLInputElement>(null);

  // Find all matches in the logs
  const searchMatches = useMemo(() => {
    if (!searchTerm) return [];
    
    const matches: { logIndex: number; startIndex: number; endIndex: number }[] = [];
    const searchRegex = new RegExp(
      searchTerm.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'), 
      caseSensitive ? 'g' : 'gi'
    );

    logs.forEach((log, logIndex) => {
      let match;
      while ((match = searchRegex.exec(log.content)) !== null) {
        matches.push({
          logIndex,
          startIndex: match.index,
          endIndex: match.index + match[0].length
        });
      }
    });

    return matches;
  }, [logs, searchTerm, caseSensitive]);

  // Highlight search terms in log content
  const highlightSearchTerm = (content: string, logIndex: number) => {
    if (!searchTerm) return content;

    const matches = searchMatches.filter(match => match.logIndex === logIndex);
    if (matches.length === 0) return content;

    let highlightedContent = '';
    let lastIndex = 0;

    matches.forEach((match) => {
      const globalMatchIndex = searchMatches.findIndex(
        m => m.logIndex === logIndex && m.startIndex === match.startIndex
      );
      const isCurrentMatch = globalMatchIndex === currentMatchIndex;
      
      highlightedContent += content.slice(lastIndex, match.startIndex);
      highlightedContent += `<span class="${isCurrentMatch ? 'search-highlight-current' : 'search-highlight'}">${content.slice(match.startIndex, match.endIndex)}</span>`;
      lastIndex = match.endIndex;
    });

    highlightedContent += content.slice(lastIndex);
    return highlightedContent;
  };

  // Scroll to current match
  const scrollToMatch = (matchIndex: number) => {
    if (matchIndex < 0 || matchIndex >= searchMatches.length || !logContainerRef.current) return;
    
    const match = searchMatches[matchIndex];
    const logElements = logContainerRef.current.querySelectorAll('[data-log-index]');
    const targetElement = logElements[match.logIndex] as HTMLElement;
    
    if (targetElement) {
      requestAnimationFrame(() => {
        targetElement.scrollIntoView({ behavior: 'smooth', block: 'center' });
        setTimeout(() => {
          if (searchInputRef.current && searchVisible) {
            searchInputRef.current.focus();
          }
        }, 100);
      });
    }
  };

  // Navigate to next match
  const nextMatch = () => {
    if (searchMatches.length === 0) return;
    const newIndex = (currentMatchIndex + 1) % searchMatches.length;
    setCurrentMatchIndex(newIndex);
    scrollToMatch(newIndex);
  };

  // Navigate to previous match
  const prevMatch = () => {
    if (searchMatches.length === 0) return;
    const newIndex = currentMatchIndex === 0 ? searchMatches.length - 1 : currentMatchIndex - 1;
    setCurrentMatchIndex(newIndex);
    scrollToMatch(newIndex);
  };

  // Handle keyboard shortcuts
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key === 'f') {
        e.preventDefault();
        setSearchVisible(true);
        setTimeout(() => searchInputRef.current?.focus(), 0);
      } else if (e.key === 'Escape' && searchVisible) {
        setSearchVisible(false);
        setSearchTerm('');
        setCurrentMatchIndex(0);
      } else if (searchVisible && e.key === 'Enter') {
        e.preventDefault();
        if (e.shiftKey) {
          prevMatch();
        } else {
          nextMatch();
        }
      }
    };

    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [searchVisible, currentMatchIndex, searchMatches.length]);

  // Reset match index when search term changes
  useEffect(() => {
    setCurrentMatchIndex(0);
  }, [searchTerm, caseSensitive]);

  // Scroll to current match when it changes
  useEffect(() => {
    if (searchMatches.length > 0) {
      scrollToMatch(currentMatchIndex);
    }
  }, [currentMatchIndex, searchMatches]);

  useEffect(() => {
    if (!backendId) {
      setError('No backend ID provided');
      setLoading(false);
      return;
    }
    const processId = `backend-${backendId}`;
    invoke("register_process_monitoring", { processId }).catch(() => {});
    const fetchInitialLogs = async () => {
      try {
        setLoading(true);
        const fetchedLogs = await invoke<LogEntry[]>("get_process_logs_history", { processId });
        if (fetchedLogs && Array.isArray(fetchedLogs)) {
          setLogs(fetchedLogs.map(log => ({ ...log, content: cleanLogContent(log.content) })));
        } else {
          setLogs([]);
        }
        setLoading(false);
      } catch (err) {
        setError(`Failed to load logs: ${err}`);
        setLoading(false);
      }
    };
    fetchInitialLogs();
    const unsubscribe = listen<{ processId: string, output: string, timestamp: number }>('process-output', (event) => {
      const { processId: eventProcessId, output, timestamp } = event.payload;
      if (eventProcessId === processId) {
        setLogs(prev => ([...prev, { timestamp, content: cleanLogContent(output), process_id: eventProcessId }]));
      }
    });
    return () => {
      unsubscribe.then(fn => fn()).catch(() => {});
    };
  }, [backendId]);

  useEffect(() => {
    if (logContainerRef.current && !searchTerm) {
      const { scrollHeight, clientHeight } = logContainerRef.current;
      logContainerRef.current.scrollTop = scrollHeight - clientHeight;
    }
  }, [logs, searchTerm]);

  function cleanLogContent(content: string) {
    return content.replace(/\u001b\[[0-9;]*m/g, '').replace(/[\x00-\x1F\x7F-\x9F]/g, '');
  }

  return (
    <div className="h-full w-full flex flex-col bg-theme-secondary relative flex-grow">
      {!searchVisible && (
        <div className="search-help-container opacity-0 hover:opacity-100 transition-opacity hover:cursor-default">
          <div className="body-xs-regular text-theme-muted items-center justify-center">
            Press Ctrl+F (Cmd+F) to search
          </div>
        </div>
      )}

      <SearchBar
        searchTerm={searchTerm}
        setSearchTerm={setSearchTerm}
        caseSensitive={caseSensitive}
        setCaseSensitive={setCaseSensitive}
        searchVisible={searchVisible}
        setSearchVisible={setSearchVisible}
        prevMatch={prevMatch}
        nextMatch={nextMatch}
        currentMatchIndex={currentMatchIndex}
        totalMatches={searchMatches.length}
        searchInputRef={searchInputRef}
      />

      <div className="jupyter-logs-content-section flex-grow flex flex-col">
        <div
          ref={logContainerRef} 
          className="jupyter-logs-content w-full flex-grow overflow-auto bg-theme-secondary font-mono text-xs whitespace-pre-wrap"
        >
          {loading && logs.length === 0 ? (
            <div className="flex justify-center py-4">
              <div data-testid="loading-spinner" className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
            </div>
          ) : error ? (
            <div className="text-red-500 py-2 px-2">{error}</div>
          ) : logs.length === 0 ? (
            <div className="text-theme-secondary">No logs available for this backend. Try starting a backend service first.</div>
          ) : (
            <div>
              {logs.map((log, index) => (
                <div 
                  key={index} 
                  className="py-0.5"
                  data-log-index={index}
                  dangerouslySetInnerHTML={{
                    __html: highlightSearchTerm(log.content, index)
                  }}
                />
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default BackendLogsPage;
