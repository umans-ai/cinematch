"use client";

import { useState } from "react";

interface Provider {
  id: number;
  name: string;
  logo_url: string;
}

interface ProviderBadgesProps {
  providers: Provider[];
}

// Icon components for each platform - reliable static icons instead of external images
const NetflixIcon = () => (
  <div className="w-5 h-5 rounded bg-red-600 flex items-center justify-center flex-shrink-0">
    <span className="text-white font-bold text-xs">N</span>
  </div>
);

const PrimeIcon = () => (
  <div className="w-5 h-5 rounded bg-blue-500 flex items-center justify-center flex-shrink-0">
    <span className="text-white font-bold text-[8px]">prime</span>
  </div>
);

const DisneyIcon = () => (
  <div className="w-5 h-5 rounded bg-blue-900 flex items-center justify-center flex-shrink-0">
    <span className="text-white font-bold text-[7px]">D+</span>
  </div>
);

const HBOIcon = () => (
  <div className="w-5 h-5 rounded bg-purple-600 flex items-center justify-center flex-shrink-0">
    <span className="text-white font-bold text-[8px]">HBO</span>
  </div>
);

const AppleIcon = () => (
  <div className="w-5 h-5 rounded bg-gray-900 flex items-center justify-center flex-shrink-0">
    <span className="text-white font-bold text-[7px]">TV+</span>
  </div>
);

const HuluIcon = () => (
  <div className="w-5 h-5 rounded bg-green-500 flex items-center justify-center flex-shrink-0">
    <span className="text-white font-bold text-[9px]">hulu</span>
  </div>
);

const DefaultIcon = ({ name }: { name: string }) => (
  <div className="w-5 h-5 rounded bg-gray-500 flex items-center justify-center flex-shrink-0">
    <span className="text-white font-bold text-[8px]">{name.charAt(0)}</span>
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

export default function ProviderBadges({ providers }: ProviderBadgesProps) {
  const [showTooltip, setShowTooltip] = useState(false);

  if (!providers || providers.length === 0) {
    return null;
  }

  const primaryProvider = providers[0];
  const additionalCount = providers.length - 1;

  return (
    <div className="relative">
      <div
        className="flex items-center gap-1.5"
        onMouseEnter={() => setShowTooltip(true)}
        onMouseLeave={() => setShowTooltip(false)}
      >
        {/* Primary provider badge with icon */}
        <div
          className="flex items-center gap-1.5 px-2 py-1 rounded-full bg-white/95 shadow-md"
          title={primaryProvider.name}
        >
          {providerIcons[primaryProvider.id] || <DefaultIcon name={primaryProvider.name} />}
          <span className="text-xs font-semibold text-gray-800">{primaryProvider.name}</span>
        </div>

        {/* Additional count badge */}
        {additionalCount > 0 && (
          <div className="flex items-center justify-center px-2 py-1 rounded-full bg-black/70 text-white text-xs font-medium backdrop-blur-sm">
            +{additionalCount}
          </div>
        )}
      </div>

      {/* Tooltip showing all providers */}
      {showTooltip && additionalCount > 0 && (
        <div className="absolute top-full right-0 mt-2 z-50">
          <div className="bg-black/90 backdrop-blur-md rounded-xl p-3 shadow-xl border border-white/10 min-w-[160px]">
            <p className="text-xs text-white/60 mb-2">Available on:</p>
            <div className="space-y-2">
              {providers.map((provider) => (
                <div key={provider.id} className="flex items-center gap-2">
                  {providerIcons[provider.id] || <DefaultIcon name={provider.name} />}
                  <span className="text-sm text-white font-medium">{provider.name}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
