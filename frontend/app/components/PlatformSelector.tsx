"use client";

interface Provider {
  id: number;
  name: string;
  logo_url: string;
}

interface PlatformSelectorProps {
  selectedProviderIds: number[];
  onSelect: (providerIds: number[]) => void;
}

// Enhanced colored icons for each platform with gradients
const NetflixIcon = () => (
  <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-red-600 to-red-700 flex items-center justify-center shadow-md shadow-red-600/30 transition-all group-hover:shadow-lg group-hover:shadow-red-600/40">
    <span className="text-white font-bold text-xl">N</span>
  </div>
);

const PrimeIcon = () => (
  <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-blue-500 to-blue-600 flex items-center justify-center shadow-md shadow-blue-500/30 transition-all group-hover:shadow-lg group-hover:shadow-blue-500/40">
    <span className="text-white font-bold text-sm">prime</span>
  </div>
);

const DisneyIcon = () => (
  <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-blue-900 to-blue-950 flex items-center justify-center shadow-md shadow-blue-900/30 transition-all group-hover:shadow-lg group-hover:shadow-blue-900/40">
    <span className="text-white font-bold text-xs">Disney+</span>
  </div>
);

const HBOIcon = () => (
  <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-purple-600 to-purple-700 flex items-center justify-center shadow-md shadow-purple-600/30 transition-all group-hover:shadow-lg group-hover:shadow-purple-600/40">
    <span className="text-white font-bold text-xs">HBO</span>
  </div>
);

const AppleIcon = () => (
  <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-gray-900 to-black flex items-center justify-center shadow-md shadow-gray-900/30 transition-all group-hover:shadow-lg group-hover:shadow-gray-900/40">
    <span className="text-white font-bold text-xs">TV+</span>
  </div>
);

const HuluIcon = () => (
  <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-green-500 to-green-600 flex items-center justify-center shadow-md shadow-green-500/30 transition-all group-hover:shadow-lg group-hover:shadow-green-500/40">
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

export default function PlatformSelector({ selectedProviderIds, onSelect }: PlatformSelectorProps) {
  // Static list of providers matching the backend
  const providers: Provider[] = [
    { id: 8, name: "Netflix", logo_url: "" },
    { id: 9, name: "Prime Video", logo_url: "" },
    { id: 337, name: "Disney+", logo_url: "" },
    { id: 384, name: "HBO Max", logo_url: "" },
    { id: 350, name: "Apple TV+", logo_url: "" },
    { id: 15, name: "Hulu", logo_url: "" },
  ];

  const MAX_PROVIDERS = 5;

  const toggleProvider = (providerId: number) => {
    if (selectedProviderIds.includes(providerId)) {
      // Don't allow deselecting the last provider
      if (selectedProviderIds.length > 1) {
        onSelect(selectedProviderIds.filter((id) => id !== providerId));
      }
    } else if (selectedProviderIds.length < MAX_PROVIDERS) {
      onSelect([...selectedProviderIds, providerId]);
    }
  };

  return (
    <div className="space-y-4">
      <div className="grid grid-cols-2 gap-3">
        {providers.map((provider) => {
          const isSelected = selectedProviderIds.includes(provider.id);
          const isDisabled = !isSelected && selectedProviderIds.length >= MAX_PROVIDERS;
          return (
            <button
              key={provider.id}
              onClick={() => toggleProvider(provider.id)}
              disabled={isDisabled}
              className={`group relative flex items-center gap-3 p-4 rounded-2xl border-2 transition-all duration-200 overflow-hidden ${
                isSelected
                  ? "border-primary bg-gradient-to-br from-primary/10 via-primary/5 to-transparent shadow-lg shadow-primary/20 scale-[1.02]"
                  : isDisabled
                    ? "border-input/50 opacity-40 cursor-not-allowed"
                    : "border-input hover:border-primary/50 hover:shadow-md hover:scale-[1.02] active:scale-100"
              }`}
            >
              {/* Animated background gradient on hover */}
              {!isDisabled && !isSelected && (
                <div className="absolute inset-0 bg-gradient-to-br from-primary/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-200" />
              )}

              {/* Selected indicator glow */}
              {isSelected && (
                <div className="absolute inset-0 bg-gradient-to-br from-primary/20 via-transparent to-transparent animate-pulse" />
              )}

              <div className="relative z-10 transition-transform duration-200 group-hover:scale-110">
                {providerIcons[provider.id]}
              </div>

              <span className={`relative z-10 font-semibold text-sm transition-colors ${
                isSelected ? "text-foreground" : "text-foreground/80 group-hover:text-foreground"
              }`}>
                {provider.name}
              </span>

              {isSelected && (
                <div className="relative z-10 ml-auto w-6 h-6 rounded-full bg-gradient-to-br from-primary to-primary/80 flex items-center justify-center shadow-md shadow-primary/30 animate-in zoom-in-50 duration-200">
                  <svg
                    className="w-3.5 h-3.5 text-primary-foreground"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={3}
                      d="M5 13l4 4L19 7"
                    />
                  </svg>
                </div>
              )}
            </button>
          );
        })}
      </div>

      <div className="flex items-center justify-center gap-2 px-4 py-3 rounded-xl bg-muted/50">
        <div className="flex gap-1">
          {Array.from({ length: MAX_PROVIDERS }).map((_, i) => (
            <div
              key={i}
              className={`w-2 h-2 rounded-full transition-all duration-300 ${
                i < selectedProviderIds.length
                  ? "bg-primary scale-110 shadow-sm shadow-primary/50"
                  : "bg-muted-foreground/20"
              }`}
            />
          ))}
        </div>
        <p className="text-xs font-medium text-muted-foreground">
          {selectedProviderIds.length} / {MAX_PROVIDERS}
        </p>
        {selectedProviderIds.length >= MAX_PROVIDERS && (
          <span className="text-xs font-semibold text-amber-600 animate-in fade-in-50 duration-200">
            Max
          </span>
        )}
      </div>
    </div>
  );
}
