"use client";

interface Provider {
  id: number;
  name: string;
  logo_url: string;
}

interface ProviderBadgesProps {
  providers: Provider[];
  maxVisible?: number;
}

export default function ProviderBadges({ providers, maxVisible = 3 }: ProviderBadgesProps) {
  if (!providers || providers.length === 0) {
    return null;
  }

  const visibleProviders = providers.slice(0, maxVisible);
  const remainingCount = providers.length - maxVisible;

  return (
    <div className="flex items-center gap-1">
      {visibleProviders.map((provider) => (
        <div
          key={provider.id}
          className="flex items-center justify-center w-6 h-6 rounded-full bg-white/90 shadow-sm overflow-hidden"
          title={provider.name}
        >
          <img
            src={provider.logo_url}
            alt={provider.name}
            className="w-5 h-5 object-contain"
            onError={(e) => {
              // Fallback to first letter if image fails
              const target = e.target as HTMLImageElement;
              target.style.display = "none";
              const parent = target.parentElement;
              if (parent) {
                parent.textContent = provider.name.charAt(0).toUpperCase();
                parent.classList.add("text-xs", "font-bold", "text-gray-700");
              }
            }}
          />
        </div>
      ))}
      {remainingCount > 0 && (
        <div className="flex items-center justify-center w-6 h-6 rounded-full bg-black/60 text-white text-xs font-medium">
          +{remainingCount}
        </div>
      )}
    </div>
  );
}
