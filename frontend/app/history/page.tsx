"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@clerk/nextjs";
import { Film, ArrowLeft, Heart } from "lucide-react";
import { apiFetch } from "../lib/api";

interface Movie {
  id: number;
  title: string;
  year?: number;
  genre?: string;
  description?: string;
  poster_url?: string;
}

export default function HistoryPage() {
  const router = useRouter();
  const { getToken, isLoaded, isSignedIn } = useAuth();
  const [movies, setMovies] = useState<Movie[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!isLoaded) return;
    if (!isSignedIn) {
      router.replace("/");
      return;
    }

    apiFetch("/api/v1/users/me/history", {}, getToken)
      .then((r) => (r.ok ? r.json() : []))
      .then((data) => {
        setMovies(data);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, [isLoaded, isSignedIn, getToken, router]);

  if (loading) {
    return (
      <main className="min-h-screen flex items-center justify-center p-6">
        <p className="text-sm text-muted-foreground">Loading history...</p>
      </main>
    );
  }

  return (
    <main className="min-h-screen p-6">
      <div className="max-w-sm mx-auto space-y-6">
        {/* Header */}
        <div className="flex items-center gap-3">
          <button
            onClick={() => router.push("/")}
            className="w-9 h-9 flex items-center justify-center rounded-lg border border-input bg-card hover:bg-secondary transition-colors"
          >
            <ArrowLeft className="w-4 h-4" />
          </button>
          <h1 className="text-xl font-bold tracking-tight">Liked movies</h1>
        </div>

        {movies.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-16 space-y-4">
            <div className="w-14 h-14 rounded-full bg-muted flex items-center justify-center">
              <Film className="w-7 h-7 text-muted-foreground" />
            </div>
            <p className="text-sm text-muted-foreground text-center">
              No liked movies yet. Start swiping!
            </p>
            <button
              onClick={() => router.push("/")}
              className="h-10 px-5 rounded-lg bg-primary text-primary-foreground text-sm font-medium hover:opacity-90 transition-opacity"
            >
              Find a room
            </button>
          </div>
        ) : (
          <div className="space-y-3">
            {movies.map((movie) => (
              <div
                key={movie.id}
                className="flex items-start gap-4 p-4 rounded-xl border border-input bg-card"
              >
                {movie.poster_url ? (
                  <img
                    src={movie.poster_url}
                    alt={movie.title}
                    className="w-14 h-20 object-cover rounded-lg flex-shrink-0"
                  />
                ) : (
                  <div className="w-14 h-20 rounded-lg bg-muted flex items-center justify-center flex-shrink-0">
                    <Film className="w-6 h-6 text-muted-foreground" />
                  </div>
                )}
                <div className="flex-1 min-w-0 space-y-1">
                  <div className="flex items-start justify-between gap-2">
                    <h3 className="font-semibold text-sm leading-tight line-clamp-2">
                      {movie.title}
                    </h3>
                    <Heart className="w-4 h-4 text-primary fill-primary flex-shrink-0 mt-0.5" />
                  </div>
                  <p className="text-xs text-muted-foreground">
                    {[movie.year, movie.genre].filter(Boolean).join(" • ")}
                  </p>
                  {movie.description && (
                    <p className="text-xs text-muted-foreground line-clamp-2">
                      {movie.description}
                    </p>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </main>
  );
}
