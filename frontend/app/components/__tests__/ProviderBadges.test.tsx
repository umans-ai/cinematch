import { render, screen } from "@testing-library/react";
import ProviderBadges from "../ProviderBadges";

describe("ProviderBadges", () => {
  const mockProviders = [
    { id: 8, name: "Netflix", logo_url: "https://image.tmdb.org/t/p/original/netflix.png" },
    { id: 337, name: "Disney+", logo_url: "https://image.tmdb.org/t/p/original/disney.png" },
    { id: 9, name: "Prime Video", logo_url: "https://image.tmdb.org/t/p/original/prime.png" },
    { id: 384, name: "HBO Max", logo_url: "https://image.tmdb.org/t/p/original/hbo.png" },
  ];

  it("renders provider logos", () => {
    render(<ProviderBadges providers={mockProviders.slice(0, 2)} />);

    const images = screen.getAllByRole("img");
    expect(images).toHaveLength(2);
    expect(images[0]).toHaveAttribute("alt", "Netflix");
    expect(images[1]).toHaveAttribute("alt", "Disney+");
  });

  it("limits visible providers to maxVisible", () => {
    render(<ProviderBadges providers={mockProviders} maxVisible={3} />);

    const images = screen.getAllByRole("img");
    expect(images).toHaveLength(3);

    // Should show +1 for the remaining provider
    expect(screen.getByText("+1")).toBeInTheDocument();
  });

  it("shows correct count for multiple remaining providers", () => {
    const fiveProviders = [
      ...mockProviders,
      { id: 350, name: "Apple TV+", logo_url: "https://example.com/apple.png" },
    ];
    render(<ProviderBadges providers={fiveProviders} maxVisible={2} />);

    const images = screen.getAllByRole("img");
    expect(images).toHaveLength(2);
    expect(screen.getByText("+3")).toBeInTheDocument();
  });

  it("returns null when providers is empty", () => {
    const { container } = render(<ProviderBadges providers={[]} />);
    expect(container.firstChild).toBeNull();
  });

  it("returns null when providers is undefined", () => {
    const { container } = render(<ProviderBadges providers={undefined as unknown as []} />);
    expect(container.firstChild).toBeNull();
  });

  it("displays provider names as tooltip", () => {
    render(<ProviderBadges providers={mockProviders.slice(0, 1)} />);

    const badge = screen.getByTitle("Netflix");
    expect(badge).toBeInTheDocument();
  });
});
