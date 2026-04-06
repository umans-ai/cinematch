import { render, screen } from "@testing-library/react";
import ProviderBadges from "../ProviderBadges";

describe("ProviderBadges", () => {
  const mockProviders = [
    { id: 8, name: "Netflix", logo_url: "https://image.tmdb.org/t/p/original/netflix.png" },
    { id: 337, name: "Disney+", logo_url: "https://image.tmdb.org/t/p/original/disney.png" },
    { id: 9, name: "Prime Video", logo_url: "https://image.tmdb.org/t/p/original/prime.png" },
    { id: 384, name: "HBO Max", logo_url: "https://image.tmdb.org/t/p/original/hbo.png" },
  ];

  it("renders primary provider name", () => {
    render(<ProviderBadges providers={mockProviders.slice(0, 2)} />);

    // Only the primary provider is shown directly
    expect(screen.getByText("Netflix")).toBeInTheDocument();
  });

  it("shows additional count when more than one provider", () => {
    render(<ProviderBadges providers={mockProviders} />);

    // Should show +3 for the remaining providers (4 total, 1 visible)
    expect(screen.getByText("+3")).toBeInTheDocument();
  });

  it("does not show count for single provider", () => {
    render(<ProviderBadges providers={mockProviders.slice(0, 1)} />);

    expect(screen.queryByText(/\+/)).not.toBeInTheDocument();
  });

  it("returns null when providers is empty", () => {
    const { container } = render(<ProviderBadges providers={[]} />);
    expect(container.firstChild).toBeNull();
  });

  it("returns null when providers is undefined", () => {
    const { container } = render(<ProviderBadges providers={undefined as unknown as []} />);
    expect(container.firstChild).toBeNull();
  });

  it("displays provider name with title attribute", () => {
    render(<ProviderBadges providers={mockProviders.slice(0, 1)} />);

    const badge = screen.getByTitle("Netflix");
    expect(badge).toBeInTheDocument();
  });
});
