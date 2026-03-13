import React from 'react';
import { Button, Tooltip } from '@openbb/ui-pro';
import CustomIcon from './Icon';

interface SearchBarProps {
  searchTerm: string;
  setSearchTerm: (term: string) => void;
  caseSensitive: boolean;
  setCaseSensitive: (sensitive: boolean) => void;
  searchVisible: boolean;
  setSearchVisible: (visible: boolean) => void;
  prevMatch: () => void;
  nextMatch: () => void;
  currentMatchIndex: number;
  totalMatches: number;
  searchInputRef: React.RefObject<HTMLInputElement>;
}

const SearchBar: React.FC<SearchBarProps> = ({
  searchTerm,
  setSearchTerm,
  caseSensitive,
  setCaseSensitive,
  searchVisible,
  setSearchVisible,
  prevMatch,
  nextMatch,
  currentMatchIndex,
  totalMatches,
  searchInputRef,
}) => {
  if (!searchVisible) {
    return null;
  }

  return (
    <div className="search-container-fixed">
      <div className="search-bar border-none flex items-center gap-2 p-0">
        <div className="flex-1 search-input-wrapper">
          <div className="relative">
            <input
              ref={searchInputRef}
              type="text"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder="Search logs..."
              spellCheck={false}
              autoComplete="off"
              autoCorrect="off"
              autoCapitalize="off"
              className="!pl-6 shadow-sm w-full search-input"
            />
            <span className="absolute left-1 top-1/2 -translate-y-1/2 text-theme-muted">
              <CustomIcon id="search" className="h-4 w-4 ml-0.5" />
            </span>
          </div>
        </div>
        <div className="search-controls flex items-center">
          <Tooltip
            content={caseSensitive ? "Case sensitive search (enabled)" : "Case sensitive search (disabled)"}
            className="tooltip-theme"
          >
            <Button
              onClick={() => setCaseSensitive(!caseSensitive)}
              className="button-secondary px-2 py-1"
              variant="secondary"
              size="xs"
            >
              {caseSensitive ? 'Aa' : 'aa'}
            </Button>
          </Tooltip>
          
          <Tooltip
            content="Previous match (Shift+Enter)"
            className="tooltip-theme"
          >
            <Button
              onClick={prevMatch}
              disabled={totalMatches === 0}
              className={`${totalMatches === 0 ? 'text-theme-muted' : 'button-ghost'} ml-2`}
              variant="ghost"
              size="icon"
            >
              ↑
            </Button>
          </Tooltip>

          <span className={`search-counter ${totalMatches === 0 ? 'text-theme-muted body-xs-regular' : 'text-theme-secondary body-xs-medium px-1'}`}>
            {totalMatches > 0 ? `${currentMatchIndex + 1}/${totalMatches}` : ' 0/0 '}
          </span>

          <Tooltip
            content="Next match (Enter)"
            className="tooltip-theme"
          >
            <Button
              onClick={nextMatch}
              disabled={totalMatches === 0}
              className={`${totalMatches === 0 ? 'text-theme-muted' : 'button-ghost'}`}
              variant="ghost"
              size="icon"
            >
              ↓
            </Button>
          </Tooltip>

          
          <Tooltip
            content="Close search (Escape)"
            className="tooltip-theme"
          >
            <Button
              onClick={() => {
                setSearchVisible(false);
                setSearchTerm('');
              }}
              className="button-outline px-1 py-1 ml-2"
              size="icon"
              variant="outline"
              aria-label="close search"
            >
              <CustomIcon id="close" className="body-lg-regular w-5 h-5"/>
            </Button>
          </Tooltip>
        </div>
      </div>
    </div>
  );
};

export default SearchBar;
