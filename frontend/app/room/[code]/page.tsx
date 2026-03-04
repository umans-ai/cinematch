"use client";

import { useEffect, useState, useCallback } from "react";
import { useParams } from "next/navigation";
import { Check, Copy, Heart, X, Info } from "lucide-react";

interface Movie {
  id: number;
  title: string;
  year?: number;
  genre?: string;
  description?: string;
  poster_url?: string;
}

interface Match {
  movie: Movie;
  participants: string[];
}

export default function RoomPage() {
  const params = useParams();
  const code = params.code as string;

  const [movies, setMovies] = useState<Movie[]>([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [matches, setMatches] = useState<Match[]>([]);
  const [showMatch, setShowMatch] = useState<Match | null>(null);
  const [showDetail, setShowDetail] = useState(false);
  const [loading, setLoading] = useState(true);
  const [finished, setFinished] = useState(false);
  const [copied, setCopied] = useState(false);
  const [previousMatchIds, setPreviousMatchIds] = useState<Set<number>>(new Set());

  const fetchMovies = useCallback(async () => {
    try {
      const response = await fetch(`/api/v1/movies?code=${code}`);
      const data = await response.json();
      setMovies(data);
      setLoading(false);
    } catch (error) {
      console.error("Failed to fetch movies:", error);
    }
  }, [code]);

  const fetchMatches = useCallback(async () => {
    try {
      const response = await fetch(`/api/v1/votes/matches?code=${code}`);
      const data = await response.json();

      // Detect NEW matches by comparing with previously seen match IDs
      const currentMatchIds = new Set<number>(data.map((m: Match) => m.movie.id));
      const newMatches = data.filter(
        (m: Match) => !previousMatchIds.has(m.movie.id)
      );

      // If there are new matches, show the first one immediately
      if (newMatches.length > 0 && !finished) {
        setShowMatch(newMatches[0]);
      }

      // Update previous match IDs for next comparison
      setPreviousMatchIds(currentMatchIds);
      setMatches(data);
    } catch (error) {
      console.error("Failed to fetch matches:", error);
    }
  }, [code, previousMatchIds, finished]);

  useEffect(() => {
    fetchMovies();
  }, [fetchMovies]);

  const handleVote = async (liked: boolean) => {
    const movie = movies[currentIndex];
    if (!movie) return;

    try {
      await fetch(`/api/v1/votes?code=${code}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ movie_id: movie.id, liked }),
      });

      await fetchMatches();

      if (currentIndex < movies.length - 1) {
        setCurrentIndex(currentIndex + 1);
      } else {
        setFinished(true);
      }
    } catch (error) {
      console.error("Failed to vote:", error);
    }
  };

  const copyRoomCode = async () => {
    try {
      await navigator.clipboard.writeText(code);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error("Failed to copy:", err);
    }
  };

  if (loading) {
    return (
      <main className="min-h-screen flex items-center justify-center p-6">
        <p className="text-sm text-muted-foreground">Loading movies...</p>
      </main>
    );
  }

  if (movies.length === 0) {
    return (
      <main className="min-h-screen flex items-center justify-center p-6">
        <div className="text-center space-y-4">
          <p className="text-sm text-muted-foreground">No movies found in this room.</p>
          <button
            onClick={() => (window.location.href = "/")}
            className="h-11 px-6 rounded-lg bg-primary text-primary-foreground text-sm font-medium hover:opacity-90 transition-opacity"
          >
            Go back
          </button>
        </div>
      </main>
    );
  }

  if (finished) {
    return (
      <main className="min-h-screen p-6">
        <div className="max-w-sm mx-auto pt-12 space-y-8">
          <div className="text-center space-y-3">
            <div className="inline-flex items-center justify-center w-12 h-12 rounded-full bg-muted">
              <Check className="w-6 h-6" />
            </div>
            <h1 className="text-2xl font-semibold tracking-tight">
              {matches.length > 0 ? "You found a match!" : "No matches yet"}
            </h1>
            <p className="text-sm text-muted-foreground">
              {matches.length > 0
                ? `You and your friends agreed on ${matches.length} movie${matches.length > 1 ? "s" : ""}`
                : "Try swiping through more movies next time"}
            </p>
          </div>

          {matches.length > 0 && (
            <div className="space-y-3">
              {matches.map((match, idx) => (
                <div
                  key={idx}
                  className="p-4 rounded-xl border border-input bg-card"
                >
                  <h3 className="font-medium">{match.movie.title}</h3>
                  <p className="text-sm text-muted-foreground mt-1">
                    {match.movie.year} • {match.movie.genre}
                  </p>
                </div>
              ))}
            </div>
          )}

          <button
            onClick={() => (window.location.href = "/")}
            className="w-full h-11 px-4 rounded-lg bg-primary text-primary-foreground text-sm font-medium hover:opacity-90 transition-opacity"
          >
            Start over
          </button>
        </div>
      </main>
    );
  }

  const currentMovie = movies[currentIndex];
  const progress = ((currentIndex + 1) / movies.length) * 100;

  return (
    <main className="min-h-screen flex flex-col">
      {/* Header */}
      <header className="px-6 py-4 flex items-center justify-between border-b border-input">
        <button
          onClick={() => (window.location.href = "/")}
          className="text-lg font-bold tracking-tight hover:opacity-80 transition-opacity"
        >
          Cine<span className="text-primary">Match</span>
        </button>

        <button
          onClick={copyRoomCode}
          className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-secondary text-sm hover:bg-secondary/80 transition-colors"
        >
          {copied ? (
            <>
              <Check className="w-4 h-4 text-primary" />
              <span>Copied</span>
            </>
          ) : (
            <>
              <Copy className="w-4 h-4" />
              <span className="font-mono tracking-wider">{code}</span>
            </>
          )}
        </button>
      </header>

      {/* Progress */}
      <div className="px-6 py-4">
        <div className="flex items-center justify-between text-sm mb-2">
          <span className="text-muted-foreground">
            {currentIndex + 1} of {movies.length}
          </span>
          <span className="text-muted-foreground">
            {matches.length} match{matches.length !== 1 ? "es" : ""}
          </span>
        </div>
        <div className="h-1 bg-muted rounded-full overflow-hidden">
          <div
            className="h-full bg-primary rounded-full transition-all duration-300"
            style={{ width: `${progress}%` }}
          />
        </div>
      </div>

      {/* Fixed Card Container */}
      <div className="flex-1 px-6 pb-4 flex items-center justify-center min-h-0">
        <div className="w-full max-w-sm flex flex-col">
          {/* Card - Fixed dimensions - Clickable for details */}
          <div
            onClick={() => setShowDetail(true)}
            className="rounded-2xl border border-input overflow-hidden bg-card shadow-2xl shadow-black/50 cursor-pointer hover:border-primary/50 transition-colors flex-shrink-0"
          >
            {/* Poster Area - Fixed aspect ratio */}
            <div className="aspect-[3/4] bg-muted relative">
              {currentMovie?.poster_url ? (
                <img
                  src={currentMovie.poster_url}
                  alt={currentMovie.title}
                  className="w-full h-full object-cover"
                />
              ) : (
                <div className="w-full h-full flex items-center justify-center bg-gradient-to-br from-muted to-muted/50">
                  <span className="text-6xl opacity-30">🎬</span>
                </div>
              )}
              {/* Gradient overlay at bottom */}
              <div className="absolute inset-x-0 bottom-0 h-32 bg-gradient-to-t from-card to-transparent" />
              {/* Tap for more indicator */}
              <div className="absolute bottom-3 right-3 flex items-center gap-1 px-2 py-1 rounded-full bg-black/60 text-white text-xs backdrop-blur-sm">
                <Info className="w-3 h-3" />
                <span>Tap for details</span>
              </div>
            </div>

            {/* Info - Compact height */}
            <div className="p-4 flex flex-col">
              <h2 className="text-lg font-bold tracking-tight line-clamp-1">
                {currentMovie?.title}
              </h2>
              <p className="text-xs text-muted-foreground mt-0.5">
                {currentMovie?.year} • {currentMovie?.genre}
              </p>
              <p className="text-sm text-muted-foreground mt-2 line-clamp-2">
                {currentMovie?.description || "No description available."}
                {(currentMovie?.description?.length || 0) > 100 && (
                  <span className="text-primary"> more</span>
                )}
              </p>
            </div>
          </div>

          {/* Actions - Always visible below card */}
          <div className="flex gap-3 mt-4 flex-shrink-0">
            <button
              onClick={() => handleVote(false)}
              className="flex-1 h-14 rounded-xl border-2 border-input bg-card flex items-center justify-center gap-2 hover:bg-secondary transition-all active:scale-95"
            >
              <X className="w-5 h-5" />
              <span className="text-sm font-semibold">Pass</span>
            </button>

            <button
              onClick={() => handleVote(true)}
              className="flex-1 h-14 rounded-xl bg-primary text-primary-foreground flex items-center justify-center gap-2 hover:opacity-90 transition-all active:scale-95 shadow-lg shadow-primary/25"
            >
              <Heart className="w-5 h-5 fill-current" />
              <span className="text-sm font-semibold">Like</span>
            </button>
          </div>
        </div>
      </div>

      {/* Match Modal */}
      {showMatch && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-6 bg-black/80 backdrop-blur-sm">
          <div className="w-full max-w-sm rounded-2xl bg-card p-6 space-y-6 border border-input shadow-2xl">
            <div className="text-center space-y-2">
              <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-primary/20">
                <Heart className="w-8 h-8 text-primary fill-primary" />
              </div>
              <h2 className="text-2xl font-bold">It's a match!</h2>
              <p className="text-sm text-muted-foreground">
                You and your friends liked
              </p>
            </div>

            <div className="p-4 rounded-xl border border-input bg-background">
              <h3 className="font-semibold">{showMatch.movie.title}</h3>
              <p className="text-sm text-muted-foreground mt-1">
                {showMatch.movie.year} • {showMatch.movie.genre}
              </p>
            </div>

            <button
              onClick={() => setShowMatch(null)}
              className="w-full h-12 rounded-lg bg-primary text-primary-foreground text-sm font-semibold hover:opacity-90 transition-opacity"
            >
              Continue
            </button>
          </div>
        </div>
      )}

      {/* Movie Detail Modal */}
      {showDetail && currentMovie && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center p-6 bg-black/90 backdrop-blur-md"
          onClick={() => setShowDetail(false)}
        >
          <div
            className="w-full max-w-md rounded-3xl bg-card border border-input shadow-2xl overflow-hidden"
            onClick={(e) => e.stopPropagation()}
          >
            {/* Modal Poster */}
            <div className="aspect-[16/9] bg-muted relative">
              {currentMovie.poster_url ? (
                <img
                  src={currentMovie.poster_url}
                  alt={currentMovie.title}
                  className="w-full h-full object-cover"
                />
              ) : (
                <div className="w-full h-full flex items-center justify-center bg-gradient-to-br from-muted to-muted/50">
                  <span className="text-6xl opacity-30">🎬</span>
                </div>
              )}
              <div className="absolute inset-0 bg-gradient-to-t from-card via-transparent to-transparent" />

              {/* Close button */}
              <button
                onClick={() => setShowDetail(false)}
                className="absolute top-4 right-4 w-10 h-10 rounded-full bg-black/50 flex items-center justify-center text-white hover:bg-black/70 transition-colors"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Modal Content */}
            <div className="p-6 space-y-4 -mt-12 relative">
              <div>
                <h2 className="text-2xl font-bold">{currentMovie.title}</h2>
                <p className="text-sm text-muted-foreground mt-1">
                  {currentMovie.year} • {currentMovie.genre}
                </p>
              </div>

              <div className="max-h-48 overflow-y-auto pr-2 scrollbar-thin">
                <p className="text-sm text-muted-foreground leading-relaxed">
                  {currentMovie.description || "No description available."}
                </p>
              </div>

              <button
                onClick={() => setShowDetail(false)}
                className="w-full h-12 rounded-xl bg-primary text-primary-foreground text-sm font-semibold hover:opacity-90 transition-opacity"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </main>
  );
}
