"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { Film, History, LogIn } from "lucide-react";
import { useAuth, useUser, SignInButton } from "@clerk/nextjs";
import { apiFetch } from "./lib/api";

interface RoomSummary {
  code: string;
  created_at: string;
  is_active: boolean;
}

export default function Home() {
  const router = useRouter();
  const { getToken, isSignedIn } = useAuth();
  const { user } = useUser();

  const [name, setName] = useState("");
  const [roomCode, setRoomCode] = useState("");
  const [isCreating, setIsCreating] = useState(false);
  const [isJoining, setIsJoining] = useState(false);
  const [showJoin, setShowJoin] = useState(false);
  const [previousRooms, setPreviousRooms] = useState<RoomSummary[]>([]);

  // Pre-fill name from Clerk user profile
  useEffect(() => {
    if (isSignedIn && user && !name) {
      const displayName =
        user.fullName ?? user.primaryEmailAddress?.emailAddress ?? "";
      setName(displayName);
    }
  }, [isSignedIn, user, name]);

  // Load previous rooms when signed in
  useEffect(() => {
    if (!isSignedIn) return;
    apiFetch("/api/v1/users/me/rooms", {}, getToken)
      .then((r) => (r.ok ? r.json() : []))
      .then(setPreviousRooms)
      .catch(() => {});
  }, [isSignedIn, getToken]);

  const createRoom = async () => {
    if (!name.trim()) return;
    setIsCreating(true);

    try {
      const response = await apiFetch("/api/v1/rooms", { method: "POST" });
      const data = await response.json();

      await apiFetch(
        `/api/v1/rooms/${data.code}/join`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ name: name.trim() }),
        },
        getToken
      );

      router.push(`/room/${data.code}`);
    } catch (error) {
      console.error("Failed to create room:", error);
      setIsCreating(false);
    }
  };

  const joinRoom = async () => {
    if (!name.trim() || !roomCode.trim()) return;
    setIsJoining(true);

    try {
      const response = await apiFetch(
        `/api/v1/rooms/${roomCode.trim()}/join`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ name: name.trim() }),
        },
        getToken
      );

      if (!response.ok) {
        throw new Error("Failed to join room");
      }

      router.push(`/room/${roomCode.trim()}`);
    } catch (error) {
      console.error("Failed to join room:", error);
      alert("Invalid room code or room is full");
      setIsJoining(false);
    }
  };

  return (
    <main className="min-h-screen flex items-center justify-center p-6">
      <div className="w-full max-w-sm space-y-8">
        {/* Logo + auth */}
        <div className="text-center space-y-3">
          <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-gradient-to-br from-primary to-primary/70 shadow-lg shadow-primary/20">
            <Film className="w-8 h-8 text-primary-foreground" />
          </div>
          <h1 className="text-3xl font-bold tracking-tight">
            Cine<span className="text-primary">Match</span>
          </h1>
          <p className="text-sm text-muted-foreground">
            Find a movie to watch together
          </p>

          {!isSignedIn && (
            <SignInButton mode="modal">
              <button className="inline-flex items-center gap-2 px-4 py-2 rounded-lg border border-input bg-card text-sm hover:bg-secondary transition-colors">
                <LogIn className="w-4 h-4" />
                Sign in to save history
              </button>
            </SignInButton>
          )}

          {isSignedIn && (
            <button
              onClick={() => router.push("/history")}
              className="inline-flex items-center gap-2 px-4 py-2 rounded-lg border border-input bg-card text-sm hover:bg-secondary transition-colors"
            >
              <History className="w-4 h-4" />
              View history
            </button>
          )}
        </div>

        {/* Form */}
        <div className="space-y-4">
          <div className="space-y-2">
            <label className="text-sm font-medium" htmlFor="name">
              Your name
            </label>
            <input
              id="name"
              type="text"
              placeholder="Enter your name"
              value={name}
              onChange={(e) => setName(e.target.value)}
              className="w-full h-12 px-4 rounded-xl border border-input bg-card text-sm placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary transition-all"
            />
          </div>

          {!showJoin ? (
            <div className="space-y-3 pt-2">
              <button
                onClick={createRoom}
                disabled={!name.trim() || isCreating}
                className="w-full h-12 px-4 rounded-xl bg-primary text-primary-foreground text-sm font-semibold hover:opacity-90 disabled:opacity-50 disabled:cursor-not-allowed transition-all active:scale-95 shadow-lg shadow-primary/20"
              >
                {isCreating ? "Creating..." : "Create room"}
              </button>

              <button
                onClick={() => setShowJoin(true)}
                className="w-full h-12 px-4 rounded-xl border-2 border-input bg-card text-sm font-semibold hover:bg-secondary transition-all active:scale-95"
              >
                Join room
              </button>
            </div>
          ) : (
            <div className="space-y-3 pt-2">
              <div className="space-y-2">
                <label className="text-sm font-medium" htmlFor="code">
                  Room code
                </label>
                <input
                  id="code"
                  type="text"
                  placeholder="Enter 4-digit code"
                  value={roomCode}
                  onChange={(e) => setRoomCode(e.target.value.toUpperCase())}
                  maxLength={4}
                  className="w-full h-12 px-4 rounded-xl border border-input bg-card text-sm text-center tracking-[0.3em] font-bold placeholder:text-muted-foreground placeholder:tracking-normal placeholder:font-normal focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary transition-all"
                />
              </div>

              <button
                onClick={joinRoom}
                disabled={!name.trim() || !roomCode.trim() || isJoining}
                className="w-full h-12 px-4 rounded-xl bg-primary text-primary-foreground text-sm font-semibold hover:opacity-90 disabled:opacity-50 disabled:cursor-not-allowed transition-all active:scale-95 shadow-lg shadow-primary/20"
              >
                {isJoining ? "Joining..." : "Join room"}
              </button>

              <button
                onClick={() => setShowJoin(false)}
                className="w-full h-12 px-4 rounded-xl text-sm font-medium text-muted-foreground hover:text-foreground transition-colors"
              >
                Go back
              </button>
            </div>
          )}
        </div>

        {/* Previous rooms (signed-in users) */}
        {isSignedIn && previousRooms.length > 0 && (
          <div className="space-y-3">
            <p className="text-sm font-medium text-muted-foreground">
              Your rooms
            </p>
            <div className="space-y-2">
              {previousRooms.map((room) => (
                <button
                  key={room.code}
                  onClick={() => router.push(`/room/${room.code}`)}
                  className="w-full flex items-center justify-between px-4 py-3 rounded-xl border border-input bg-card hover:bg-secondary transition-colors"
                >
                  <span className="font-mono tracking-wider font-bold text-sm">
                    {room.code}
                  </span>
                  <span className="text-xs text-muted-foreground">
                    {room.is_active ? "Active" : "Ended"}
                  </span>
                </button>
              ))}
            </div>
          </div>
        )}
      </div>
    </main>
  );
}
