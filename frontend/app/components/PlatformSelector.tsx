"use client";

interface Provider {
  id: number;
  name: string;
  logo_url: string;
}

interface PlatformSelectorProps {
  selectedProviderId: number | null;
  onSelect: (providerId: number) => void;
}

// Simple colored icons for each platform
const NetflixIcon = () => (
  <div className="w-10 h-10 rounded-lg bg-red-600 flex items-center justify-center">
    <span className="text-white font-bold text-lg">N</span>
  </div>
);

const PrimeIcon = () => (
  <div className="w-10 h-10 rounded-lg bg-blue-500 flex items-center justify-center">
    <span className="text-white font-bold text-sm">prime</span>
  </div>
);

const DisneyIcon = () => (
  <div className="w-10 h-10 rounded-lg bg-blue-900 flex items-center justify-center">
    <span className="text-white font-bold text-xs">Disney+</span>
  </div>
);

const HBOIcon = () => (
  <div className="w-10 h-10 rounded-lg bg-purple-600 flex items-center justify-center">
    <span className="text-white font-bold text-xs">HBO</span>
  </div>
);

const AppleIcon = () => (
  <div className="w-10 h-10 rounded-lg bg-gray-900 flex items-center justify-center">
    <span className="text-white font-bold text-xs">TV+</span>
  </div>
);

const HuluIcon = () => (
  <div className="w-10 h-10 rounded-lg bg-green-500 flex items-center justify-center">
    <span className="text-white font-bold text-sm">hulu</span>
  </div>
);

const providerIcons: Record<number, React.ReactNode> = {
  8: <NetflixIcon />,    // Netflix
  9: <PrimeIcon />,      // Prime Video
  337: <DisneyIcon />,   // Disney+
  384: <HBOIcon />,      // HBO Max
  350: <AppleIcon />,    // Apple TV+
  15: <HuluIcon />,      // Hulu
};

export default function PlatformSelector({ selectedProviderId, onSelect }: PlatformSelectorProps) {
  // Static list of providers matching the backend
  const providers: Provider[] = [
    { id: 8, name: "Netflix", logo_url: "" },
    { id: 9, name: "Prime Video", logo_url: "" },
    { id: 337, name: "Disney+", logo_url: "" },
    { id: 384, name: "HBO Max", logo_url: "" },
    { id: 350, name: "Apple TV+", logo_url: "" },
    { id: 15, name: "Hulu", logo_url: "" },
  ];

  return (
    <div className="grid grid-cols-2 gap-3">
      {providers.map((provider) => (
        <button
          key={provider.id}
          onClick={() => onSelect(provider.id)}
          className={`flex items-center gap-3 p-3 rounded-xl border-2 transition-all ${
            selectedProviderId === provider.id
              ? "border-primary bg-primary/5"
              : "border-input hover:border-primary/50"
          }`}
        >
          {providerIcons[provider.id]}
          <span className="font-medium text-sm">{provider.name}</span>
        </button>
      ))}
    </div>
  );
}
