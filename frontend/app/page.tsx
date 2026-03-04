"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Film } from "lucide-react";

export default function Home() {
  const router = useRouter();
  const [name, setName] = useState("");
  const [roomCode, setRoomCode] = useState("");
  const [isCreating, setIsCreating] = useState(false);
  const [isJoining, setIsJoining] = useState(false);
  const [showJoin, setShowJoin] = useState(false);

  const createRoom = async () => {
    if (!name.trim()) return;
    setIsCreating(true);

    try {
      const response = await fetch("/api/v1/rooms", {
        method: "POST",
      });
      const data = await response.json();

      await fetch(`/api/v1/rooms/${data.code}/join`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name: name.trim() }),
      });

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
      const response = await fetch(`/api/v1/rooms/${roomCode.trim()}/join`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name: name.trim() }),
      });

      if (!response.ok) {
        throw new Error("Failed to join room");
      }

      router.push(`/room/${roomCode.trim()}`);
    } catch (error) {
      console.error("Failed to join room:", error);
      alert("Invalid room code");
      setIsJoining(false);
    }
  };

  return (
    <main className="min-h-screen flex items-center justify-center p-6">
      <div className="w-full max-w-sm space-y-8">
        {/* Logo */}
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
      </div>
    </main>
  );
}
