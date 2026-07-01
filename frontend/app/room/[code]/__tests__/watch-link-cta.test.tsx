/**
 * @jest-environment jsdom
 */

import { render, screen, waitFor, fireEvent } from "@testing-library/react";
import { useParams } from "next/navigation";

// Feature 00028 — Watch Now Deep Links: the match modal should offer a one-tap
// "Where to watch" CTA opening the TMDB region link, with graceful fallback when null.

jest.mock("next/navigation", () => ({
  useParams: jest.fn(),
}));

const mockFetch = jest.fn();
global.fetch = mockFetch;

const WATCH_LINK = "https://www.themoviedb.org/movie/27205/watch?locale=US";

function makeMovie(overrides = {}) {
  return {
    id: 1,
    title: "Inception",
    year: 2010,
    genre: "Sci-Fi",
    description: "A thief who steals corporate secrets...",
    poster_url: "https://example.com/poster.jpg",
    available_providers: [{ id: 8, name: "Netflix", logo_url: "" }],
    watch_link: WATCH_LINK,
    ...overrides,
  };
}

function mockRoomWithMatch(movie: { id: number; title: string }) {
  const match = { movie, participants: ["Alice", "Bob"] };
  // A second movie keeps the user off the "finished" screen so the match MODAL renders.
  const filler = { ...movie, id: 999, title: "Filler Movie" };
  const room = { code: "TEST", region: "US", provider_ids: [8] };
  mockFetch.mockImplementation((url: string) => {
    if (url.includes("/api/v1/movies?code=TEST")) {
      return Promise.resolve({
        ok: true,
        json: () => Promise.resolve({ movies: [movie, filler], room }),
      });
    }
    if (url.includes("/api/v1/votes/matches?code=TEST")) {
      return Promise.resolve({ ok: true, json: () => Promise.resolve([match]) });
    }
    if (url.includes("/api/v1/votes?code=TEST")) {
      return Promise.resolve({ ok: true, json: () => Promise.resolve({ id: 1, liked: true }) });
    }
    return Promise.resolve({ ok: true, json: () => Promise.resolve({}) });
  });
}

describe("Watch Now CTA on match", () => {
  beforeEach(() => {
    jest.clearAllMocks();
    (useParams as jest.Mock).mockReturnValue({ code: "TEST" });
  });

  it("renders a 'Where to watch' CTA linking to the TMDB watch link in a new tab", async () => {
    mockRoomWithMatch(makeMovie());
    const { default: RoomPage } = await import("../page");
    render(<RoomPage />);

    await waitFor(() => expect(screen.getByText("Inception")).toBeInTheDocument());
    fireEvent.click(screen.getByText("Like"));

    await waitFor(() => {
      expect(screen.getByText("It's a match!")).toBeInTheDocument();
    });

    const cta = screen.getByRole("link", { name: /where to watch/i });
    expect(cta).toHaveAttribute("href", WATCH_LINK);
    expect(cta).toHaveAttribute("target", "_blank");
    expect(cta).toHaveAttribute("rel", "noopener noreferrer");
  });

  it("does not render the CTA when watch_link is null (graceful fallback)", async () => {
    mockRoomWithMatch(makeMovie({ watch_link: null }));
    const { default: RoomPage } = await import("../page");
    render(<RoomPage />);

    await waitFor(() => expect(screen.getByText("Inception")).toBeInTheDocument());
    fireEvent.click(screen.getByText("Like"));

    await waitFor(() => {
      expect(screen.getByText("It's a match!")).toBeInTheDocument();
    });

    expect(screen.queryByRole("link", { name: /where to watch/i })).not.toBeInTheDocument();
    // Modal remains usable: the Continue action is still present.
    expect(screen.getByText("Continue")).toBeInTheDocument();
  });
});
