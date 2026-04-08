import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import ShareButton from "../ShareButton";

describe("ShareButton", () => {
  const mockRoomCode = "ABCD";

  beforeEach(() => {
    Object.assign(navigator, {
      clipboard: {
        writeText: jest.fn(() => Promise.resolve()),
      },
    });
  });

  afterEach(() => {
    jest.restoreAllMocks();
  });

  it("renders the room code", () => {
    render(<ShareButton roomCode={mockRoomCode} />);
    expect(screen.getByText(mockRoomCode)).toBeInTheDocument();
  });

  it("shows options menu when clicked", () => {
    render(<ShareButton roomCode={mockRoomCode} />);
    const button = screen.getByRole("button", { name: new RegExp(mockRoomCode) });

    fireEvent.click(button);

    expect(screen.getByText("Copy link")).toBeInTheDocument();
    expect(screen.getByText("Copy code")).toBeInTheDocument();
  });

  it("copies room code to clipboard", async () => {
    render(<ShareButton roomCode={mockRoomCode} />);
    const button = screen.getByRole("button", { name: new RegExp(mockRoomCode) });

    fireEvent.click(button);
    const copyCodeButton = screen.getByText("Copy code");
    fireEvent.click(copyCodeButton);

    await waitFor(() => {
      expect(navigator.clipboard.writeText).toHaveBeenCalledWith(mockRoomCode);
    });
  });

  it("copies room URL to clipboard", async () => {
    render(<ShareButton roomCode={mockRoomCode} />);
    const button = screen.getByRole("button", { name: new RegExp(mockRoomCode) });

    fireEvent.click(button);
    const copyLinkButton = screen.getByText("Copy link");
    fireEvent.click(copyLinkButton);

    await waitFor(() => {
      expect(navigator.clipboard.writeText).toHaveBeenCalledWith(
        expect.stringContaining(`/room/${mockRoomCode}`)
      );
    });
  });

  it("shows copied confirmation", async () => {
    render(<ShareButton roomCode={mockRoomCode} />);
    const button = screen.getByRole("button", { name: new RegExp(mockRoomCode) });

    fireEvent.click(button);
    const copyCodeButton = screen.getByText("Copy code");
    fireEvent.click(copyCodeButton);

    await waitFor(() => {
      expect(screen.getByText("Copied!")).toBeInTheDocument();
    });
  });

  it("closes options menu when backdrop is clicked", () => {
    render(<ShareButton roomCode={mockRoomCode} />);
    const button = screen.getByRole("button", { name: new RegExp(mockRoomCode) });

    fireEvent.click(button);
    expect(screen.getByText("Copy code")).toBeInTheDocument();

    // Click backdrop (the fixed inset-0 div)
    const backdrop = screen.getByText("Copy code").parentElement?.parentElement?.previousSibling;
    if (backdrop) {
      fireEvent.click(backdrop);
    }

    // Options should be hidden now
    expect(screen.queryByText("Copy code")).not.toBeInTheDocument();
  });

  it("shows native share button when available", () => {
    Object.assign(navigator, {
      share: jest.fn(() => Promise.resolve()),
    });

    render(<ShareButton roomCode={mockRoomCode} />);
    const button = screen.getByRole("button", { name: new RegExp(mockRoomCode) });

    fireEvent.click(button);

    expect(screen.getByText("Share invite")).toBeInTheDocument();
  });

  it("calls native share API when share button is clicked", async () => {
    const mockShare = jest.fn(() => Promise.resolve());
    Object.assign(navigator, {
      share: mockShare,
    });

    render(<ShareButton roomCode={mockRoomCode} />);
    const button = screen.getByRole("button", { name: new RegExp(mockRoomCode) });

    fireEvent.click(button);
    const shareButton = screen.getByText("Share invite");
    fireEvent.click(shareButton);

    await waitFor(() => {
      expect(mockShare).toHaveBeenCalledWith({
        title: "Join my CineMatch room",
        text: expect.stringContaining(mockRoomCode),
        url: expect.stringContaining(`/room/${mockRoomCode}`),
      });
    });
  });
});
