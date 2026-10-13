// @vitest-environment jsdom

import { act, renderHook } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { useChatMessages } from "./useChatMessages";
import { askChatbot } from "../services/api";
import { initialMessages } from "../constants/chatMessages";

vi.mock("../services/api", () => ({
  askChatbot: vi.fn(),
}));

describe("useChatMessages", () => {
  beforeEach(() => {
    vi.useFakeTimers();
    vi.clearAllMocks();
  });

  afterEach(() => {
    vi.clearAllTimers();
    vi.useRealTimers();
  });

  it("starts with initial messages", () => {
    const { result } = renderHook(() => useChatMessages());

    expect(result.current.messages).toEqual(initialMessages);
    expect(result.current.isLoading).toBe(false);
    expect(result.current.isTyping).toBe(false);
  });

  it("does not send an empty message", async () => {
    const { result } = renderHook(() => useChatMessages());

    await act(async () => {
      await result.current.handleSendMessage("   ");
    });

    expect(askChatbot).not.toHaveBeenCalled();
    expect(result.current.messages).toEqual(initialMessages);
  });

  it("sends a message and adds the bot response", async () => {
    askChatbot.mockResolvedValue("Hello, how can I help you?");

    const { result } = renderHook(() => useChatMessages());

    await act(async () => {
      await result.current.handleSendMessage("Hello");
    });

    expect(askChatbot).toHaveBeenCalledWith("Hello", initialMessages);

    expect(result.current.isLoading).toBe(false);
    expect(result.current.isTyping).toBe(true);

    await act(async () => {
      vi.advanceTimersByTime(1000);
    });

    expect(result.current.isTyping).toBe(false);

    expect(result.current.messages).toHaveLength(2);

    expect(result.current.messages[0]).toMatchObject({
      role: "user",
      text: "Hello",
    });

    expect(result.current.messages[1]).toMatchObject({
      role: "bot",
      text: "Hello, how can I help you?",
      isTyping: false,
    });
  });

  it("adds an error message when the API request fails", async () => {
    const consoleErrorSpy = vi
      .spyOn(console, "error")
      .mockImplementation(() => {});

    askChatbot.mockRejectedValue(new Error("API error"));

    const { result } = renderHook(() => useChatMessages());

    await act(async () => {
      await result.current.handleSendMessage("Hello");
    });

    expect(result.current.isLoading).toBe(false);
    expect(result.current.isTyping).toBe(false);

    expect(result.current.messages).toHaveLength(2);
    expect(result.current.messages[1]).toMatchObject({
      role: "bot",
      text: "Sorry, something went wrong. Please try again 🍫",
      isError: true,
    });

    consoleErrorSpy.mockRestore();
  });

  it("clears the chat and restores the initial messages", async () => {
    askChatbot.mockResolvedValue("Bot response");

    const { result } = renderHook(() => useChatMessages());

    await act(async () => {
      await result.current.handleSendMessage("Hello");
    });

    await act(async () => {
      result.current.handleClearChat();
    });

    expect(result.current.messages).toEqual(initialMessages);
    expect(result.current.isLoading).toBe(false);
    expect(result.current.isTyping).toBe(false);
  });

  it("adds a voice message and removes the initial welcome message", () => {
    const { result } = renderHook(() => useChatMessages());

    act(() => {
      result.current.handleAddVoiceMessage({
        role: "user",
        text: "I want chocolate",
      });
    });

    expect(result.current.messages).toHaveLength(1);
    expect(result.current.messages[0]).toMatchObject({
      role: "user",
      text: "I want chocolate",
      source: "voice",
    });
  });
});
