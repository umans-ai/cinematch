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
        {/* Primary provider - larger badge with logo */}
        <div
          className="flex items-center gap-1.5 px-2 py-1 rounded-full bg-white/95 shadow-md"
          title={primaryProvider.name}
        >
          <div className="w-5 h-5 rounded-full overflow-hidden bg-gray-100 flex items-center justify-center">
            <img
              src={primaryProvider.logo_url}
              alt={primaryProvider.name}
              className="w-4 h-4 object-contain"
              onError={(e) => {
                const target = e.target as HTMLImageElement;
                target.style.display = "none";
                const parent = target.parentElement;
                if (parent) {
                  parent.textContent = primaryProvider.name.charAt(0).toUpperCase();
                  parent.classList.add("text-xs", "font-bold", "text-gray-600");
                }
              }}
            />
          </div>
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
                  <div className="w-6 h-6 rounded-full overflow-hidden bg-white flex items-center justify-center">
                    <img
                      src={provider.logo_url}
                      alt={provider.name}
                      className="w-5 h-5 object-contain"
                      onError={(e) => {
                        const target = e.target as HTMLImageElement;
                        target.style.display = "none";
                        const parent = target.parentElement;
                        if (parent) {
                          parent.textContent = provider.name.charAt(0).toUpperCase();
                          parent.classList.add("text-xs", "font-bold", "text-gray-600");
                        }
                      }}
                    />
                  </div>
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
