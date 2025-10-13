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

const JupyterLogsPage: React.FC = () => {
  // Get environment from route parameters
  const search = useSearch({ from: '/jupyter-logs' });
  const environmentName = search.environment as string;
  
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
    console.log("JupyterLogsPage initialized with environment:", environmentName);

    if (!environmentName) {
      setError('No environment name provided');
      setLoading(false);
      return;
    }

    const processId = `jupyter-${environmentName}`;
    console.log(`Fetching logs for process: ${processId}`);
    
    // Register for process monitoring
    invoke("register_process_monitoring", { processId })
      .then(() => console.log(`Process ${processId} registered for monitoring`))
      .catch(err => console.error(`Failed to register process monitoring: ${err}`));
    
    // Fetch initial logs
    const fetchInitialLogs = async () => {
      try {
        setLoading(true);
        
        // Get logs for this specific environment/process
        const fetchedLogs = await invoke<LogEntry[]>("get_process_logs_history", { 
          processId 
        });
        
        console.log(`Received ${fetchedLogs?.length || 0} logs for ${environmentName}`);
        
        if (fetchedLogs && Array.isArray(fetchedLogs)) {
          setLogs(fetchedLogs.map(log => ({ ...log, content: cleanLogContent(log.content) })));
          
          // Check if any logs contain the specific shutdown message
          checkForShutdownMessage(fetchedLogs);
        } else {
          console.warn("No logs returned or invalid format");
          setLogs([]);
        }
        
        setLoading(false);
      } catch (err) {
        console.error(`Failed to fetch logs for ${environmentName}:`, err);
        setError(`Failed to load logs: ${err}`);
        setLoading(false);
      }
    };
    
    // Function to check for the specific shutdown message
    const checkForShutdownMessage = (logEntries: LogEntry[]) => {
      // Look specifically for the exact shutdown message
      const hasShutdownMessage = logEntries.some(log => 
        log.content.includes("Shutting down on /api/shutdown request")
      );
      
      if (hasShutdownMessage) {
        console.log(`Found API shutdown message for ${environmentName}, notifying parent`);
        notifyShutdown();
      }
    };
    
    // Function to notify parent window about server shutdown
    const notifyShutdown = () => {
      try {
        // Use postMessage to notify parent window about shutdown
        if (window.opener) {
          console.log("Notifying parent window via postMessage");
          window.opener.postMessage({
            type: 'jupyter-status-update',
            environmentName,
            status: 'stopped'
          }, '*');
        }
        
        // Also use localStorage as a backup communication channel
        // This helps when direct window communication might fail
        const shutdownKey = `jupyter-shutdown-${environmentName}`;
        localStorage.setItem(shutdownKey, Date.now().toString());
        
        console.log("Shutdown notification sent via postMessage and localStorage");
        
        // If this window was opened by another window, we can close it now
        // if (window.opener) {
        //   window.close();
        // }
      } catch (err) {
        console.error("Error sending shutdown notification:", err);
      }
    };
    
    fetchInitialLogs();
    
    // Listen for new log entries
    console.log(`Setting up process-output listener for ${processId}`);
    const unsubscribe = listen<{ processId: string, output: string, timestamp: number }>('process-output', (event) => {
      const { processId: eventProcessId, output, timestamp } = event.payload;
      
      if (eventProcessId === processId) {
        // Add the new log entry
        setLogs(prev => {
          const newLogs = [...prev, {
            timestamp,
            content: cleanLogContent(output),
            process_id: eventProcessId
          }];
          
          // Check specifically for the shutdown request message
          if (output.includes("Shutting down on /api/shutdown request")) {
            console.log("Detected Jupyter API shutdown request, notifying parent");
            notifyShutdown();
          }
          
          return newLogs;
        });
      }
    });
    
    // Cleanup
    return () => {
      console.log(`JupyterLogsPage unmounting for ${processId}`);
      unsubscribe.then(fn => fn()).catch(console.error);
    };
  }, [environmentName]);
  
  // Auto-scroll to bottom when new logs come in
  useEffect(() => {
    if (logContainerRef.current && !searchTerm) {
      const { scrollHeight, clientHeight } = logContainerRef.current;
      logContainerRef.current.scrollTop = scrollHeight - clientHeight;
    }
  }, [logs, searchTerm]);

  function cleanLogContent(content: string) {
    // eslint-disable-next-line no-control-regex
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
            <div className="text-theme-secondary">No logs available for this environment. Try starting a Jupyter server first.</div>
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

export default JupyterLogsPage;
