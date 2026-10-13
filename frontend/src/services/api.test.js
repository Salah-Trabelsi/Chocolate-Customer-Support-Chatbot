import { beforeEach, describe, expect, it, vi } from "vitest";

import { askChatbot } from "./api";
import { postRequest } from "./httpClient";

vi.mock("./httpClient", () => ({
  postRequest: vi.fn(),
}));

describe("askChatbot", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("sends the user message to the chat API", async () => {
    postRequest.mockResolvedValue({
      message: "Hello from bot",
    });

    const result = await askChatbot("Hello");

    expect(postRequest).toHaveBeenCalledWith(
      "http://localhost:8000/api/chat/ask",
      {
        message: "Hello",
        history: [],
      },
    );

    expect(result).toBe("Hello from bot");
  });

  it("formats bot role as assistant in history", async () => {
    postRequest.mockResolvedValue({
      message: "Bot response",
    });

    const history = [
      {
        role: "user",
        text: "Hi",
      },
      {
        role: "bot",
        text: "Hello, how can I help?",
      },
    ];

    await askChatbot("I want chocolate", history);

    expect(postRequest).toHaveBeenCalledWith(
      "http://localhost:8000/api/chat/ask",
      {
        message: "I want chocolate",
        history: [
          {
            role: "user",
            content: "Hi",
          },
          {
            role: "assistant",
            content: "Hello, how can I help?",
          },
        ],
      },
    );
  });

  it("removes the initial welcome message from history", async () => {
    postRequest.mockResolvedValue({
      message: "Bot response",
    });

    const history = [
      {
        id: 1,
        role: "bot",
        text: "Welcome to ChocoWise!",
      },
      {
        id: 2,
        role: "user",
        text: "Hello",
      },
    ];

    await askChatbot("I want chocolate", history);

    expect(postRequest).toHaveBeenCalledWith(
      "http://localhost:8000/api/chat/ask",
      {
        message: "I want chocolate",
        history: [
          {
            role: "user",
            content: "Hello",
          },
        ],
      },
    );
  });

  it("sends only the last 8 history messages", async () => {
    postRequest.mockResolvedValue({
      message: "Bot response",
    });

    const history = Array.from({ length: 10 }, (_, index) => ({
      id: index + 2,
      role: index % 2 === 0 ? "user" : "bot",
      text: `Message ${index + 1}`,
    }));

    await askChatbot("Next message", history);

    expect(postRequest).toHaveBeenCalledWith(
      "http://localhost:8000/api/chat/ask",
      {
        message: "Next message",
        history: [
          { role: "user", content: "Message 3" },
          { role: "assistant", content: "Message 4" },
          { role: "user", content: "Message 5" },
          { role: "assistant", content: "Message 6" },
          { role: "user", content: "Message 7" },
          { role: "assistant", content: "Message 8" },
          { role: "user", content: "Message 9" },
          { role: "assistant", content: "Message 10" },
        ],
      },
    );
  });

  it("uses content when text is missing in history", async () => {
    postRequest.mockResolvedValue({
      message: "Bot response",
    });

    const history = [
      {
        role: "user",
        content: "Message from content",
      },
    ];

    await askChatbot("Next message", history);

    expect(postRequest).toHaveBeenCalledWith(
      "http://localhost:8000/api/chat/ask",
      {
        message: "Next message",
        history: [
          {
            role: "user",
            content: "Message from content",
          },
        ],
      },
    );
  });

  it("returns the chatbot response message", async () => {
    postRequest.mockResolvedValue({
      message: "German White Chocolate Raspberry Crisp is available.",
    });

    const result = await askChatbot("Do you have white chocolate?");

    expect(result).toBe("German White Chocolate Raspberry Crisp is available.");
  });
});
