/**
 * @jest-environment jsdom
 */

import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import { useParams } from 'next/navigation';

// Mock next/navigation
jest.mock('next/navigation', () => ({
  useParams: jest.fn(),
}));

// Mock fetch globally
const mockFetch = jest.fn();
global.fetch = mockFetch;

const mockMovie = {
  id: 1,
  title: 'Inception',
  year: 2010,
  genre: 'Sci-Fi',
  description: 'A thief who steals corporate secrets...',
  poster_url: 'https://example.com/poster.jpg',
};

describe('Room Share Button', () => {
  let mockShare: jest.Mock;
  let mockWriteText: jest.Mock;
  const originalShare = navigator.share;
  const originalClipboard = navigator.clipboard;

  beforeEach(() => {
    jest.clearAllMocks();
    (useParams as jest.Mock).mockReturnValue({ code: 'ABC123' });

    mockShare = jest.fn().mockResolvedValue(undefined);
    mockWriteText = jest.fn().mockResolvedValue(undefined);

    Object.defineProperty(navigator, 'share', {
      writable: true,
      value: mockShare,
    });
    Object.defineProperty(navigator, 'clipboard', {
      writable: true,
      value: { writeText: mockWriteText },
    });

    mockFetch.mockImplementation((url: string) => {
      if (url.includes('/api/v1/movies?code=ABC123')) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve({ movies: [mockMovie], room: { code: 'ABC123', region: 'FR', provider_ids: [] } }),
        });
      }
      if (url.includes('/api/v1/votes/matches')) {
        return Promise.resolve({ ok: true, json: () => Promise.resolve([]) });
      }
      return Promise.resolve({ ok: true, json: () => Promise.resolve({}) });
    });
  });

  afterEach(() => {
    Object.defineProperty(navigator, 'share', { writable: true, value: originalShare });
    Object.defineProperty(navigator, 'clipboard', { writable: true, value: originalClipboard });
  });

  it('renders share button alongside copy button', async () => {
    const { default: RoomPage } = await import('../page');
    render(<RoomPage />);

    await waitFor(() => {
      expect(screen.getByTitle('Share room')).toBeInTheDocument();
    });

    const shareButton = screen.getByTitle('Share room');
    expect(shareButton).toHaveTextContent('Share');
  });

  it('uses native Web Share API when available', async () => {
    const { default: RoomPage } = await import('../page');
    render(<RoomPage />);

    await waitFor(() => {
      expect(screen.getByTitle('Share room')).toBeInTheDocument();
    });

    const shareButton = screen.getByTitle('Share room');
    fireEvent.click(shareButton);

    await waitFor(() => {
      expect(mockShare).toHaveBeenCalledWith({
        title: 'Join my CineMatch room',
        text: "Let's find a movie to watch together! Join my room with code ABC123",
        url: 'http://localhost/room/ABC123',
      });
    });

    expect(mockWriteText).not.toHaveBeenCalled();
  });

  it('falls back to clipboard when Web Share API is unavailable', async () => {
    Object.defineProperty(navigator, 'share', { writable: true, value: undefined });

    const { default: RoomPage } = await import('../page');
    render(<RoomPage />);

    await waitFor(() => {
      expect(screen.getByTitle('Share room')).toBeInTheDocument();
    });

    const shareButton = screen.getByTitle('Share room');
    fireEvent.click(shareButton);

    await waitFor(() => {
      expect(mockWriteText).toHaveBeenCalledWith('http://localhost/room/ABC123');
    });

    expect(mockShare).not.toHaveBeenCalled();
  });

  it('shows copied feedback when fallback clipboard succeeds', async () => {
    Object.defineProperty(navigator, 'share', { writable: true, value: undefined });

    const { default: RoomPage } = await import('../page');
    render(<RoomPage />);

    await waitFor(() => {
      expect(screen.getByTitle('Share room')).toBeInTheDocument();
    });

    const shareButton = screen.getByTitle('Share room');
    fireEvent.click(shareButton);

    await waitFor(() => {
      expect(screen.getByText('Link copied')).toBeInTheDocument();
    });
  });

  it('ignores AbortError when user cancels native share', async () => {
    const consoleError = jest.spyOn(console, 'error').mockImplementation(() => {});
    mockShare.mockRejectedValue(new DOMException('User cancelled', 'AbortError'));

    const { default: RoomPage } = await import('../page');
    render(<RoomPage />);

    await waitFor(() => {
      expect(screen.getByTitle('Share room')).toBeInTheDocument();
    });

    const shareButton = screen.getByTitle('Share room');
    fireEvent.click(shareButton);

    await waitFor(() => {
      expect(mockShare).toHaveBeenCalled();
    });

    expect(consoleError).not.toHaveBeenCalled();
    consoleError.mockRestore();
  });

  it('logs real errors from native share API', async () => {
    const consoleError = jest.spyOn(console, 'error').mockImplementation(() => {});
    mockShare.mockRejectedValue(new Error('Network failure'));

    const { default: RoomPage } = await import('../page');
    render(<RoomPage />);

    await waitFor(() => {
      expect(screen.getByTitle('Share room')).toBeInTheDocument();
    });

    const shareButton = screen.getByTitle('Share room');
    fireEvent.click(shareButton);

    await waitFor(() => {
      expect(consoleError).toHaveBeenCalledWith('Share failed:', expect.any(Error));
    });

    consoleError.mockRestore();
  });
});
