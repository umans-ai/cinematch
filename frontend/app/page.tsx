"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Film, Plus, Users } from "lucide-react";

export default function Home() {
  const router = useRouter();
  const [roomCode, setRoomCode] = useState("");
  const [name, setName] = useState("");
  const [isCreating, setIsCreating] = useState(false);
  const [isJoining, setIsJoining] = useState(false);

  const createRoom = async () => {
    if (!name.trim()) return;
    setIsCreating(true);

    try {
      const response = await fetch("/api/v1/rooms", {
        method: "POST",
      });
      const data = await response.json();

      // Join the room immediately
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
      alert("Invalid room code or room is full");
      setIsJoining(false);
    }
  };

  return (
    <main className="min-h-screen bg-gradient-to-br from-rose-50 to-pink-100 flex items-center justify-center p-4">
      <div className="max-w-md w-full space-y-6">
        <div className="text-center space-y-2">
          <div className="flex items-center justify-center gap-2">
            <Film className="w-10 h-10 text-rose-500" />
            <h1 className="text-4xl font-bold text-gray-900">CineMatch</h1>
          </div>
          <p className="text-gray-600">
            Swipe through movies with your partner and find the perfect match
          </p>
        </div>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Users className="w-5 h-5" />
              Join the fun
            </CardTitle>
            <CardDescription>
              Enter your name to create a room or join an existing one
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <Input
              placeholder="Your name"
              value={name}
              onChange={(e) => setName(e.target.value)}
            />

            <Button
              onClick={createRoom}
              disabled={!name.trim() || isCreating}
              className="w-full"
              size="lg"
            >
              <Plus className="w-4 h-4 mr-2" />
              {isCreating ? "Creating..." : "Create Room"}
            </Button>

            <div className="relative">
              <div className="absolute inset-0 flex items-center">
                <span className="w-full border-t" />
              </div>
              <div className="relative flex justify-center text-xs uppercase">
                <span className="bg-background px-2 text-muted-foreground">
                  Or join existing
                </span>
              </div>
            </div>

            <div className="flex gap-2">
              <Input
                placeholder="Room code (4 digits)"
                value={roomCode}
                onChange={(e) => setRoomCode(e.target.value)}
                maxLength={4}
                className="uppercase"
              />
              <Button
                onClick={joinRoom}
                disabled={!name.trim() || !roomCode.trim() || isJoining}
              >
                {isJoining ? "..." : "Join"}
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    </main>
  );
}
