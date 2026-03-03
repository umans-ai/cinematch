"use client";

import { useEffect, useState, useCallback } from "react";
import { useParams } from "next/navigation";
import { Check, Copy, Heart, X } from "lucide-react";

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
  const [loading, setLoading] = useState(true);
  const [finished, setFinished] = useState(false);
  const [copied, setCopied] = useState(false);

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
      setMatches(data);
    } catch (error) {
      console.error("Failed to fetch matches:", error);
    }
  }, [code]);

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

  const copyRoomCode = () => {
    navigator.clipboard.writeText(code);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  if (loading) {
    return (
      <main className="min-h-screen flex items-center justify-center p-6">
        <p className="text-sm text-muted-foreground">Loading movies...</p>
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
            className="w-full h-11 px-4 rounded-lg bg-foreground text-background text-sm font-medium hover:opacity-90 transition-opacity"
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
      <header className="px-6 py-4 flex items-center justify-between border-b">
        <button
          onClick={() => (window.location.href = "/")}
          className="text-sm font-medium hover:opacity-70 transition-opacity"
        >
          CineMatch
        </button>

        <button
          onClick={copyRoomCode}
          className="flex items-center gap-2 px-3 py-1.5 rounded-lg border border-input text-sm hover:bg-secondary transition-colors"
        >
          {copied ? (
            <>
              <Check className="w-4 h-4" />
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
            className="h-full bg-foreground rounded-full transition-all duration-300"
            style={{ width: `${progress}%` }}
          />
        </div>
      </div>

      {/* Movie Card */}
      <div className="flex-1 px-6 pb-6">
        <div className="max-w-sm mx-auto h-full flex flex-col">
          {/* Card */}
          <div className="flex-1 rounded-2xl border border-input overflow-hidden bg-card flex flex-col">
            {/* Poster Area */}
            <div className="aspect-[4/5] bg-muted relative">
              {currentMovie.poster_url ? (
                <img
                  src={currentMovie.poster_url}
                  alt={currentMovie.title}
                  className="w-full h-full object-cover"
                />
              ) : (
                <div className="w-full h-full flex items-center justify-center">
                  <span className="text-4xl opacity-20">🎬</span>
                </div>
              )}
            </div>

            {/* Info */}
            <div className="p-5 space-y-4">
              <div>
                <h2 className="text-xl font-semibold tracking-tight">
                  {currentMovie.title}
                </h2>
                <p className="text-sm text-muted-foreground mt-1">
                  {currentMovie.year} • {currentMovie.genre}
                </p>
              </div>

              {currentMovie.description && (
                <p className="text-sm text-muted-foreground line-clamp-3">
                  {currentMovie.description}
                </p>
              )}
            </div>
          </div>

          {/* Actions */}
          <div className="flex gap-3 mt-4">
            <button
              onClick={() => handleVote(false)}
              className="flex-1 h-12 rounded-xl border border-input flex items-center justify-center gap-2 hover:bg-secondary transition-colors"
            >
              <X className="w-5 h-5" />
              <span className="text-sm font-medium">Pass</span>
            </button>

            <button
              onClick={() => handleVote(true)}
              className="flex-1 h-12 rounded-xl bg-foreground text-background flex items-center justify-center gap-2 hover:opacity-90 transition-opacity"
            >
              <Heart className="w-5 h-5" />
              <span className="text-sm font-medium">Like</span>
            </button>
          </div>
        </div>
      </div>

      {/* Match Modal */}
      {showMatch && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-6 bg-black/50">
          <div className="w-full max-w-sm rounded-2xl bg-background p-6 space-y-6">
            <div className="text-center space-y-2">
              <div className="inline-flex items-center justify-center w-12 h-12 rounded-full bg-muted">
                <Heart className="w-6 h-6 fill-foreground" />
              </div>
              <h2 className="text-xl font-semibold">It's a match!</h2>
              <p className="text-sm text-muted-foreground">
                You and your friends liked
              </p>
            </div>

            <div className="p-4 rounded-xl border border-input bg-card">
              <h3 className="font-medium">{showMatch.movie.title}</h3>
              <p className="text-sm text-muted-foreground mt-1">
                {showMatch.movie.year} • {showMatch.movie.genre}
              </p>
            </div>

            <button
              onClick={() => setShowMatch(null)}
              className="w-full h-11 rounded-lg bg-foreground text-background text-sm font-medium hover:opacity-90 transition-opacity"
            >
              Continue
            </button>
          </div>
        </div>
      )}
    </main>
  );
}
