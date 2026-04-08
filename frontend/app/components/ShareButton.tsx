"use client";

import { useState } from "react";
import { Check, Copy, Share2, Link2 } from "lucide-react";

interface ShareButtonProps {
  roomCode: string;
}

export default function ShareButton({ roomCode }: ShareButtonProps) {
  const [copied, setCopied] = useState(false);
  const [showOptions, setShowOptions] = useState(false);

  const roomUrl = typeof window !== "undefined"
    ? `${window.location.origin}/room/${roomCode}`
    : "";

  const copyCode = async () => {
    try {
      await navigator.clipboard.writeText(roomCode);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error("Failed to copy code:", err);
    }
  };

  const copyLink = async () => {
    try {
      await navigator.clipboard.writeText(roomUrl);
      setCopied(true);
      setTimeout(() => {
        setCopied(false);
        setShowOptions(false);
      }, 2000);
    } catch (err) {
      console.error("Failed to copy link:", err);
    }
  };

  const shareNative = async () => {
    if (navigator.share) {
      try {
        await navigator.share({
          title: "Join my CineMatch room",
          text: `Let's find a movie to watch together! Join my room with code ${roomCode}`,
          url: roomUrl,
        });
        setShowOptions(false);
      } catch (err) {
        // User cancelled share - ignore silently
        if ((err as Error).name !== "AbortError") {
          console.error("Failed to share:", err);
        }
      }
    }
  };

  const hasNativeShare = typeof navigator !== "undefined" && !!navigator.share;

  return (
    <div className="relative">
      <button
        onClick={() => setShowOptions(!showOptions)}
        className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-secondary text-sm hover:bg-secondary/80 transition-colors"
      >
        {copied ? (
          <>
            <Check className="w-4 h-4 text-primary" />
            <span>Copied!</span>
          </>
        ) : (
          <>
            <Share2 className="w-4 h-4" />
            <span className="font-mono tracking-wider">{roomCode}</span>
          </>
        )}
      </button>

      {showOptions && (
        <>
          {/* Backdrop */}
          <div
            className="fixed inset-0 z-40"
            onClick={() => setShowOptions(false)}
          />

          {/* Options menu */}
          <div className="absolute top-full right-0 mt-2 w-56 rounded-xl border border-input bg-card shadow-xl z-50 overflow-hidden">
            {hasNativeShare && (
              <button
                onClick={shareNative}
                className="w-full px-4 py-3 flex items-center gap-3 hover:bg-secondary transition-colors text-left"
              >
                <Share2 className="w-4 h-4" />
                <div>
                  <div className="text-sm font-medium">Share invite</div>
                  <div className="text-xs text-muted-foreground">Send via apps</div>
                </div>
              </button>
            )}

            <button
              onClick={copyLink}
              className="w-full px-4 py-3 flex items-center gap-3 hover:bg-secondary transition-colors text-left border-t border-input"
            >
              <Link2 className="w-4 h-4" />
              <div>
                <div className="text-sm font-medium">Copy link</div>
                <div className="text-xs text-muted-foreground">Share the URL</div>
              </div>
            </button>

            <button
              onClick={copyCode}
              className="w-full px-4 py-3 flex items-center gap-3 hover:bg-secondary transition-colors text-left border-t border-input"
            >
              <Copy className="w-4 h-4" />
              <div>
                <div className="text-sm font-medium">Copy code</div>
                <div className="text-xs text-muted-foreground font-mono">{roomCode}</div>
              </div>
            </button>
          </div>
        </>
      )}
    </div>
  );
}
