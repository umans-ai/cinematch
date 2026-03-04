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

// Mock match data
const mockMovie = {
  id: 1,
  title: 'Inception',
  year: 2010,
  genre: 'Sci-Fi',
  description: 'A thief who steals corporate secrets...',
  poster_url: 'https://example.com/poster.jpg',
};

const mockMatch = {
  movie: mockMovie,
  participants: ['Alice', 'Bob'],
};

describe('Match Notification Flow', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    (useParams as jest.Mock).mockReturnValue({ code: 'TEST' });
  });

  /**
   * This test demonstrates the real-world scenario where two participants
   * both like the same movie, but the match modal does not automatically appear.
   *
   * Expected behavior: When the backend returns a match, the UI should
   * immediately show the match modal to both participants.
   *
   * Current behavior: The match is fetched but the modal doesn't trigger.
   */
  it('should show match modal immediately when backend returns a match', async () => {
    // Setup: Mock movies endpoint
    mockFetch.mockImplementation((url: string) => {
      if (url.includes('/api/v1/movies?code=TEST')) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve([mockMovie]),
        });
      }

      if (url.includes('/api/v1/votes/matches?code=TEST')) {
        // Return a match - both participants liked the movie
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve([mockMatch]),
        });
      }

      if (url.includes('/api/v1/votes?code=TEST')) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve({ id: 1, liked: true }),
        });
      }

      return Promise.resolve({ ok: true, json: () => Promise.resolve({}) });
    });

    // Import and render the component
    const { default: RoomPage } = await import('../room/[code]/page');
    render(<RoomPage />);

    // Wait for movies to load
    await waitFor(() => {
      expect(screen.getByText('Inception')).toBeInTheDocument();
    });

    // Simulate user liking a movie
    const likeButton = screen.getByText('Like');
    fireEvent.click(likeButton);

    // Wait for vote to be processed
    await waitFor(() => {
      expect(mockFetch).toHaveBeenCalledWith(
        '/api/v1/votes?code=TEST',
        expect.objectContaining({
          method: 'POST',
          body: JSON.stringify({ movie_id: 1, liked: true }),
        })
      );
    });

    // The critical assertion: Match modal should be visible
    // FIXME: This currently fails - the match modal doesn't show even though
    // the backend correctly returns a match
    await waitFor(() => {
      const matchModal = screen.queryByText("It's a match!");
      // This assertion will fail, demonstrating the bug
      expect(matchModal).toBeInTheDocument();
    }, { timeout: 2000 });
  });

  /**
   * Test that the matches count updates in the UI when a match occurs,
   * but the modal doesn't auto-trigger.
   */
  it('should update matches count but not show modal automatically', async () => {
    let matchesCount = 0;

    mockFetch.mockImplementation((url: string) => {
      if (url.includes('/api/v1/movies?code=TEST')) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve([mockMovie]),
        });
      }

      if (url.includes('/api/v1/votes/matches?code=TEST')) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve(matchesCount > 0 ? [mockMatch] : []),
        });
      }

      if (url.includes('/api/v1/votes?code=TEST')) {
        // Simulate match being created after vote
        matchesCount = 1;
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve({ id: 1, liked: true }),
        });
      }

      return Promise.resolve({ ok: true, json: () => Promise.resolve({}) });
    });

    const { default: RoomPage } = await import('../page');
    render(<RoomPage />);

    // Wait for movies to load
    await waitFor(() => {
      expect(screen.getByText('Inception')).toBeInTheDocument();
    });

    // Initially no matches
    expect(screen.getByText('0 matches')).toBeInTheDocument();

    // Like a movie
    const likeButton = screen.getByText('Like');
    fireEvent.click(likeButton);

    // Wait for vote to process
    await waitFor(() => {
      expect(mockFetch).toHaveBeenCalledWith(
        '/api/v1/votes?code=TEST',
        expect.any(Object)
      );
    });

    // Matches count should update
    await waitFor(() => {
      expect(screen.getByText('1 match')).toBeInTheDocument();
    });

    // BUT: Match modal should NOT be visible (this demonstrates the issue)
    // The user has to manually notice the "1 match" text instead of
    // getting an immediate celebration modal
    const matchModal = screen.queryByText("It's a match!");
    expect(matchModal).not.toBeInTheDocument();
  });

  /**
   * Test that after finishing all movies, the match summary is shown,
   * but real-time match notification during swiping doesn't work.
   */
  it('should show matches in summary after finishing but not during swiping', async () => {
    mockFetch.mockImplementation((url: string) => {
      if (url.includes('/api/v1/movies?code=TEST')) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve([mockMovie]), // Only 1 movie
        });
      }

      if (url.includes('/api/v1/votes/matches?code=TEST')) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve([mockMatch]),
        });
      }

      if (url.includes('/api/v1/votes?code=TEST')) {
        return Promise.resolve({ ok: true, json: () => Promise.resolve({}) });
      }

      return Promise.resolve({ ok: true, json: () => Promise.resolve({}) });
    });

    const { default: RoomPage } = await import('../page');
    render(<RoomPage />);

    // Wait for movies to load
    await waitFor(() => {
      expect(screen.getByText('Inception')).toBeInTheDocument();
    });

    // Like the movie
    const likeButton = screen.getByText('Like');
    fireEvent.click(likeButton);

    // Wait for "finished" screen
    await waitFor(() => {
      expect(screen.getByText('You found a match!')).toBeInTheDocument();
    });

    // Match is shown in summary
    expect(screen.getByText('Inception')).toBeInTheDocument();

    // But during the swiping (before finishing), the match modal
    // did not automatically appear - this is the bug
  });
});
