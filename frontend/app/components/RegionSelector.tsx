"use client";

import { useState, useCallback } from "react";
import { MapPin, Loader2 } from "lucide-react";

interface Region {
  code: string;
  name: string;
  flag: string;
}

interface RegionSelectorProps {
  selectedRegion: string | null;
  onSelect: (region: string) => void;
}

// Static list of regions matching the backend
const regions: Region[] = [
  { code: "US", name: "United States", flag: "🇺🇸" },
  { code: "FR", name: "France", flag: "🇫🇷" },
  { code: "GB", name: "United Kingdom", flag: "🇬🇧" },
  { code: "DE", name: "Germany", flag: "🇩🇪" },
  { code: "ES", name: "Spain", flag: "🇪🇸" },
  { code: "IT", name: "Italy", flag: "🇮🇹" },
  { code: "CA", name: "Canada", flag: "🇨🇦" },
  { code: "AU", name: "Australia", flag: "🇦🇺" },
  { code: "JP", name: "Japan", flag: "🇯🇵" },
  { code: "BR", name: "Brazil", flag: "🇧🇷" },
];

export default function RegionSelector({ selectedRegion, onSelect }: RegionSelectorProps) {
  const [isDetecting, setIsDetecting] = useState(false);
  const [detectError, setDetectError] = useState<string | null>(null);

  const detectRegion = useCallback(async () => {
    setIsDetecting(true);
    setDetectError(null);

    if (!navigator.geolocation) {
      setDetectError("Geolocation is not supported by your browser");
      setIsDetecting(false);
      return;
    }

    navigator.geolocation.getCurrentPosition(
      async (position) => {
        try {
          const { latitude, longitude } = position.coords;

          const response = await fetch("/api/v1/providers/detect-region", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ lat: latitude, lng: longitude }),
          });

          if (!response.ok) {
            throw new Error("Failed to detect region");
          }

          const data = await response.json();

          if (data.detected && data.code) {
            onSelect(data.code);
          } else {
            setDetectError("Could not detect your region. Please select manually.");
          }
        } catch (error) {
          setDetectError("Error detecting region. Please select manually.");
        } finally {
          setIsDetecting(false);
        }
      },
      (error) => {
        let message = "Could not access your location.";
        if (error.code === error.PERMISSION_DENIED) {
          message = "Location access denied. Please enable location services or select manually.";
        }
        setDetectError(message);
        setIsDetecting(false);
      }
    );
  }, [onSelect]);

  return (
    <div className="space-y-3">
      {/* Region dropdown with detect button */}
      <div className="flex gap-2">
        <select
          value={selectedRegion || ""}
          onChange={(e) => onSelect(e.target.value)}
          className="flex-1 h-12 px-4 rounded-xl border border-input bg-card text-sm focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary transition-all"
        >
          <option value="">Select your region</option>
          {regions.map((region) => (
            <option key={region.code} value={region.code}>
              {region.flag} {region.name}
            </option>
          ))}
        </select>

        <button
          onClick={detectRegion}
          disabled={isDetecting}
          className="h-12 px-4 rounded-xl border-2 border-input bg-card flex items-center gap-2 hover:bg-secondary transition-all disabled:opacity-50"
          title="Detect my location"
        >
          {isDetecting ? (
            <Loader2 className="w-4 h-4 animate-spin" />
          ) : (
            <MapPin className="w-4 h-4" />
          )}
          <span className="text-sm font-medium hidden sm:inline">
            {isDetecting ? "Detecting..." : "Detect"}
          </span>
        </button>
      </div>

      {/* Error message */}
      {detectError && (
        <p className="text-xs text-red-500">{detectError}</p>
      )}
    </div>
  );
}
