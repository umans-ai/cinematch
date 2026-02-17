"use client";

import { useEffect, useState, useCallback } from "react";
import { useParams } from "next/navigation";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
} from "@/components/ui/card";
import { Heart, X, Check } from "lucide-react";

interface Movie {
  id: number;
  title: string;
  year?: number;
  genre?: string;
  description?: string;
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

      // Check for new matches
      await fetchMatches();

      // Move to next movie
      if (currentIndex < movies.length - 1) {
        setCurrentIndex(currentIndex + 1);
      } else {
        setFinished(true);
      }
    } catch (error) {
      console.error("Failed to vote:", error);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-pulse text-lg">Loading movies...</div>
      </div>
    );
  }

  if (finished) {
    return (
      <main className="min-h-screen bg-gradient-to-br from-rose-50 to-pink-100 p-4">
        <div className="max-w-md mx-auto pt-20">
          <div className="text-center space-y-4">
            <h2 className="text-3xl font-bold">All done!</h2>
            <p className="text-gray-600">
              {matches.length > 0
                ? `You found ${matches.length} match${matches.length > 1 ? "es" : ""}!`
                : "No matches yet. Maybe try again with different movies?"}
            </p>
            {matches.length > 0 && (
              <div className="space-y-2 mt-6">
                <h3 className="font-semibold">Your matches:</h3>
                {matches.map((match, idx) => (
                  <Card key={idx} className="bg-white">
                    <CardContent className="p-4">
                      <div className="font-semibold">{match.movie.title}</div>
                      <div className="text-sm text-gray-500">
                        {match.movie.year} • {match.movie.genre}
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            )}
            <Button onClick={() => window.location.href = "/"} className="mt-6">
              Start over
            </Button>
          </div>
        </div>
      </main>
    );
  }

  const currentMovie = movies[currentIndex];

  return (
    <main className="min-h-screen bg-gradient-to-br from-rose-50 to-pink-100 p-4">
      <div className="max-w-md mx-auto pt-4">
        <div className="text-center mb-4">
          <p className="text-sm text-gray-500">Room: {code}</p>
          <p className="text-sm text-gray-500">
            {currentIndex + 1} / {movies.length}
          </p>
        </div>

        {showMatch && (
          <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
            <Card className="max-w-sm w-full bg-white animate-in zoom-in">
              <CardContent className="p-6 text-center space-y-4">
                <div className="text-6xl">🎉</div>
                <h3 className="text-2xl font-bold">It&apos;s a Match!</h3>
                <div>
                  <p className="font-semibold text-lg">{showMatch.movie.title}</p>
                  <p className="text-gray-500">
                    {showMatch.movie.year} • {showMatch.movie.genre}
                  </p>
                </div>
                <Button onClick={() => setShowMatch(null)} className="w-full">
                  Continue swiping
                </Button>
              </CardContent>
            </Card>
          </div>
        )}

        <Card className="overflow-hidden shadow-xl">
          <div className="aspect-[2/3] bg-gradient-to-br from-gray-800 to-gray-900 flex items-center justify-center p-8">
            <div className="text-center text-white">
              <h2 className="text-3xl font-bold mb-2">{currentMovie.title}</h2>
              <p className="text-gray-300">
                {currentMovie.year} • {currentMovie.genre}
              </p>
            </div>
          </div>
          <CardContent className="p-6">
            <p className="text-gray-600 mb-6 line-clamp-3">
              {currentMovie.description}
            </p>
            <div className="flex gap-4 justify-center">
              <Button
                variant="outline"
                size="lg"
                onClick={() => handleVote(false)}
                className="rounded-full w-16 h-16 p-0 border-2 border-gray-300 hover:border-red-500 hover:bg-red-50"
              >
                <X className="w-8 h-8 text-gray-600" />
              </Button>
              <Button
                size="lg"
                onClick={() => handleVote(true)}
                className="rounded-full w-16 h-16 p-0 bg-gradient-to-r from-rose-500 to-pink-500 hover:from-rose-600 hover:to-pink-600"
              >
                <Heart className="w-8 h-8" />
              </Button>
            </div>
          </CardContent>
        </Card>

        {matches.length > 0 && (
          <div className="mt-6 text-center">
            <p className="text-sm text-gray-600">
              {matches.length} match{matches.length > 1 ? "es" : ""} found so far
            </p>
          </div>
        )}
      </div>
    </main>
  );
}
