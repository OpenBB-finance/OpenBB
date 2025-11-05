/// <reference types="vitest/globals" />
import { expect, test, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import CustomIcon, { HelpIcon, FileIcon, ODPLogo, OpenBBLogo, CopyIcon, ThemeToggleButton, SettingsIcon, ChevronIcon } from '../../components/Icon';
import { GamestonkIcon } from '../../components/GamestonkIcon';

// Mock the Tooltip component from @openbb/ui-pro
vi.mock('@openbb/ui-pro', () => ({
  Tooltip: vi.fn(({ children, content }) => (
    <div data-tooltip-content={content}>{children}</div>
  )),
  Button: vi.fn(({ children, ...props }) => (
    <button {...props}>{children}</button>
  )),
}));

test('CustomIcon renders with correct id and default class', () => {
  render(<CustomIcon id="test-icon" />);
  const svgElement = screen.getByRole('img', { hidden: true });
  expect(svgElement).toBeInTheDocument();
  expect(svgElement).toHaveClass('w-4 h-4');
  expect(svgElement).toHaveAttribute('aria-hidden', 'true');
  expect(svgElement).toHaveAttribute('role', 'img');
  expect(svgElement).toHaveAttribute('viewBox', '0 0 24 24');
  expect(svgElement.querySelector('use')).toHaveAttribute('href', '/assets/icons/sprite.svg#test-icon');
});

test('CustomIcon applies additional className', () => {
  render(<CustomIcon id="test-icon" className="extra-class" />);
  const svgElement = screen.getByRole('img', { hidden: true });
  expect(svgElement).toHaveClass('w-4 h-4 extra-class');
});

test('CustomIcon handles jupyter-logo viewBox correctly', () => {
  render(<CustomIcon id="jupyter-logo" />);
  const svgElement = screen.getByRole('img', { hidden: true });
  expect(svgElement).toHaveAttribute('viewBox', '0 0 256 300');
});

test('HelpIcon renders with tooltip and correct styling', () => {
  const tooltipText = 'This is a helpful tooltip';
  render(<HelpIcon tooltip={tooltipText} />);
  const helpDiv = screen.getByText('i');
  expect(helpDiv).toBeInTheDocument();
  expect(helpDiv.parentElement).toHaveAttribute('data-tooltip-content', tooltipText);
  expect(helpDiv).toHaveClass('info-icon cursor-help opacity-80 hover:opacity-100 transition-opacity duration-200 shadow-sm');
});

test('HelpIcon applies additional className', () => {
  render(<HelpIcon tooltip="test" className="custom-help-class" />);
  const helpDiv = screen.getByText('i');
  expect(helpDiv).toHaveClass('custom-help-class');
});

test('FileIcon renders with correct SVG structure', () => {
  const { container } = render(<FileIcon className="file-icon-class" />);
  const svgElement = container.querySelector('svg');
  expect(svgElement).toBeInTheDocument();
  expect(svgElement).toHaveClass('file-icon-class');
});

test('ODPLogo renders correctly', () => {
  const { container } = render(<ODPLogo />);
  expect(container.querySelector('svg')).toBeInTheDocument();
});

test('OpenBBLogo renders correctly', () => {
  render(<OpenBBLogo />);
  expect(screen.getByRole('img', { name: 'OpenBB Logo' })).toBeInTheDocument();
});

test('CopyIcon renders correctly', () => {
  const { container } = render(<CopyIcon />);
  expect(container.querySelector('svg')).toBeInTheDocument();
});

test('ThemeToggleButton renders correctly for dark mode', () => {
  render(<ThemeToggleButton isDarkMode={true} toggleTheme={() => {}} />);
  expect(screen.getByRole('button', { name: 'Switch to light mode' })).toBeInTheDocument();
});

test('ThemeToggleButton renders correctly for light mode', () => {
  render(<ThemeToggleButton isDarkMode={false} toggleTheme={() => {}} />);
  expect(screen.getByRole('button', { name: 'Switch to dark mode' })).toBeInTheDocument();
});

test('SettingsIcon renders correctly', () => {
  const { container } = render(<SettingsIcon />);
  expect(container.querySelector('svg')).toBeInTheDocument();
});

test('ChevronIcon renders correctly', () => {
  const { container } = render(<ChevronIcon />);
  expect(container.querySelector('svg')).toBeInTheDocument();
});

test('GamestonkIcon renders correctly', () => {
  const { container } = render(<GamestonkIcon />);
  expect(container.querySelector('svg')).toBeInTheDocument();
});
