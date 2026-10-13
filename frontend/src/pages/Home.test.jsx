// @vitest-environment jsdom

import "@testing-library/jest-dom/vitest";

import { cleanup, render, screen } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import Home from "./Home";
import { useAutoScroll } from "../hooks/useAutoScroll";
import { useChatMessages } from "../hooks/useChatMessages";

vi.mock("../hooks/useAutoScroll", () => ({
  useAutoScroll: vi.fn(),
}));

vi.mock("../hooks/useChatMessages", () => ({
  useChatMessages: vi.fn(),
}));

vi.mock("../components/Navbar", () => ({
  default: () => <div data-testid="navbar">Navbar</div>,
}));

vi.mock("../components/QuestionResponse", () => ({
  default: ({ messages, isLoading }) => (
    <div data-testid="question-response">
      QuestionResponse - {messages.length} messages - loading:{" "}
      {String(isLoading)}
    </div>
  ),
}));

vi.mock("../components/InputText", () => ({
  default: ({ onSendMessage, onClearChat, isLoading, onAddVoiceMessage }) => (
    <div data-testid="input-text">
      <button onClick={() => onSendMessage("Hello")}>send</button>
      <button onClick={onClearChat}>clear</button>
      <button
        onClick={() =>
          onAddVoiceMessage({
            role: "user",
            text: "voice message",
          })
        }
      >
        voice
      </button>
      <span>input loading: {String(isLoading)}</span>
    </div>
  ),
}));

describe("Home", () => {
  const mockHandleSendMessage = vi.fn();
  const mockHandleClearChat = vi.fn();
  const mockHandleAddVoiceMessage = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();

    useChatMessages.mockReturnValue({
      messages: [
        {
          id: 1,
          role: "bot",
          text: "Hey, I am your chocolate chatbot 🍫 How can I help you?",
        },
      ],
      isLoading: false,
      isTyping: false,
      handleSendMessage: mockHandleSendMessage,
      handleClearChat: mockHandleClearChat,
      handleAddVoiceMessage: mockHandleAddVoiceMessage,
    });
  });

  afterEach(() => {
    cleanup();
  });

  it("renders the main home layout", () => {
    render(<Home />);

    expect(screen.getByTestId("navbar")).toBeInTheDocument();
    expect(screen.getByTestId("question-response")).toBeInTheDocument();
    expect(screen.getByTestId("input-text")).toBeInTheDocument();
  });

  it("passes messages and loading state to QuestionResponse", () => {
    render(<Home />);

    expect(
      screen.getByText(/QuestionResponse - 1 messages - loading: false/i),
    ).toBeInTheDocument();
  });

  it("calls useAutoScroll with chat state", () => {
    render(<Home />);

    expect(useAutoScroll).toHaveBeenCalledWith({
      messages: [
        {
          id: 1,
          role: "bot",
          text: "Hey, I am your chocolate chatbot 🍫 How can I help you?",
        },
      ],
      isLoading: false,
      isTyping: false,
    });
  });

  it("passes send handler to InputText", async () => {
    render(<Home />);

    screen.getByText("send").click();

    expect(mockHandleSendMessage).toHaveBeenCalledWith("Hello");
  });

  it("passes clear handler to InputText", async () => {
    render(<Home />);

    screen.getByText("clear").click();

    expect(mockHandleClearChat).toHaveBeenCalled();
  });

  it("passes voice message handler to InputText", async () => {
    render(<Home />);

    screen.getByText("voice").click();

    expect(mockHandleAddVoiceMessage).toHaveBeenCalledWith({
      role: "user",
      text: "voice message",
    });
  });

  it("passes loading true to InputText when chat is loading", () => {
    useChatMessages.mockReturnValue({
      messages: [],
      isLoading: true,
      isTyping: false,
      handleSendMessage: mockHandleSendMessage,
      handleClearChat: mockHandleClearChat,
      handleAddVoiceMessage: mockHandleAddVoiceMessage,
    });

    render(<Home />);

    expect(screen.getByText(/input loading: true/i)).toBeInTheDocument();
  });

  it("passes loading true to InputText when bot is typing", () => {
    useChatMessages.mockReturnValue({
      messages: [],
      isLoading: false,
      isTyping: true,
      handleSendMessage: mockHandleSendMessage,
      handleClearChat: mockHandleClearChat,
      handleAddVoiceMessage: mockHandleAddVoiceMessage,
    });

    render(<Home />);

    expect(screen.getByText(/input loading: true/i)).toBeInTheDocument();
  });
});
