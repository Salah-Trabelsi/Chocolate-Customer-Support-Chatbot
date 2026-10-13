// @vitest-environment jsdom

import { act, renderHook } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { RTVIEvent } from "@pipecat-ai/client-js";
import { useVoiceChat } from "./useVoiceChat";

const mockState = vi.hoisted(() => ({
  pipecatClient: {
    startBotAndConnect: vi.fn(),
    disconnect: vi.fn(),
  },
  transportState: "disconnected",
  eventHandlers: {},
}));

vi.mock("@pipecat-ai/client-js", () => ({
  RTVIEvent: {
    UserTranscript: "UserTranscript",
    UserLlmText: "UserLlmText",
    BotOutput: "BotOutput",
    BotTranscript: "BotTranscript",
    UserStartedSpeaking: "UserStartedSpeaking",
    UserStoppedSpeaking: "UserStoppedSpeaking",
    BotStartedSpeaking: "BotStartedSpeaking",
    BotStoppedSpeaking: "BotStoppedSpeaking",
  },
}));

vi.mock("@pipecat-ai/client-react", () => ({
  usePipecatClient: () => mockState.pipecatClient,
  usePipecatClientTransportState: () => mockState.transportState,
  useRTVIClientEvent: (eventName, handler) => {
    mockState.eventHandlers[eventName] = handler;
  },
}));

vi.mock("../config/voiceConfig", () => ({
  CONNECTED_VOICE_STATES: ["connected", "ready"],
  CONNECTING_VOICE_STATES: ["connecting"],
  VOICE_API_URL: "http://localhost:7860/start",
}));

describe("useVoiceChat", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockState.transportState = "disconnected";
    mockState.eventHandlers = {};
  });

  it("returns the initial voice state", () => {
    const onAddVoiceMessage = vi.fn();

    const { result } = renderHook(() =>
      useVoiceChat({
        onAddVoiceMessage,
      }),
    );

    expect(result.current.voiceError).toBe(null);
    expect(result.current.isVoiceConnected).toBe(false);
    expect(result.current.isVoiceConnecting).toBe(false);
    expect(result.current.isUserSpeaking).toBe(false);
    expect(result.current.isBotSpeaking).toBe(false);
    expect(result.current.isVoiceActive).toBe(false);
  });

  it("starts the voice connection when disconnected", async () => {
    const onAddVoiceMessage = vi.fn();

    const { result } = renderHook(() =>
      useVoiceChat({
        onAddVoiceMessage,
      }),
    );

    await act(async () => {
      await result.current.handleVoiceClick();
    });

    expect(mockState.pipecatClient.startBotAndConnect).toHaveBeenCalledWith({
      endpoint: "http://localhost:7860/start",
    });

    expect(mockState.pipecatClient.disconnect).not.toHaveBeenCalled();
  });

  it("disconnects when voice is already connected", async () => {
    mockState.transportState = "connected";

    const onAddVoiceMessage = vi.fn();

    const { result } = renderHook(() =>
      useVoiceChat({
        onAddVoiceMessage,
      }),
    );

    await act(async () => {
      await result.current.handleVoiceClick();
    });

    expect(mockState.pipecatClient.disconnect).toHaveBeenCalled();
    expect(mockState.pipecatClient.startBotAndConnect).not.toHaveBeenCalled();
  });

  it("sets an error message when voice connection fails", async () => {
    const consoleErrorSpy = vi
      .spyOn(console, "error")
      .mockImplementation(() => {});

    mockState.pipecatClient.startBotAndConnect.mockRejectedValue(
      new Error("Connection failed"),
    );

    const onAddVoiceMessage = vi.fn();

    const { result } = renderHook(() =>
      useVoiceChat({
        onAddVoiceMessage,
      }),
    );

    await act(async () => {
      await result.current.handleVoiceClick();
    });

    expect(result.current.voiceError).toBe(
      "Voice connection failed. Please check the voice server.",
    );

    consoleErrorSpy.mockRestore();
  });

  it("adds a final user transcript as a voice message", () => {
    const onAddVoiceMessage = vi.fn();

    renderHook(() =>
      useVoiceChat({
        onAddVoiceMessage,
      }),
    );

    act(() => {
      mockState.eventHandlers[RTVIEvent.UserTranscript]({
        final: true,
        text: "I want chocolate",
      });
    });

    expect(onAddVoiceMessage).toHaveBeenCalledWith(
      expect.objectContaining({
        role: "user",
        text: "I want chocolate",
        source: "voice",
      }),
    );
  });

  it("ignores non-final user transcripts", () => {
    const onAddVoiceMessage = vi.fn();

    renderHook(() =>
      useVoiceChat({
        onAddVoiceMessage,
      }),
    );

    act(() => {
      mockState.eventHandlers[RTVIEvent.UserTranscript]({
        final: false,
        text: "partial text",
      });
    });

    expect(onAddVoiceMessage).not.toHaveBeenCalled();
  });

  it("adds completed bot output as a voice message", () => {
    const onAddVoiceMessage = vi.fn();

    renderHook(() =>
      useVoiceChat({
        onAddVoiceMessage,
      }),
    );

    act(() => {
      mockState.eventHandlers[RTVIEvent.BotOutput]({
        spoken_status: "completed",
        text: "German chocolate is available.",
      });
    });

    expect(onAddVoiceMessage).toHaveBeenCalledWith(
      expect.objectContaining({
        role: "bot",
        text: "German chocolate is available.",
        source: "voice",
      }),
    );
  });

  it("ignores incomplete bot output", () => {
    const onAddVoiceMessage = vi.fn();

    renderHook(() =>
      useVoiceChat({
        onAddVoiceMessage,
      }),
    );

    act(() => {
      mockState.eventHandlers[RTVIEvent.BotOutput]({
        spoken_status: "started",
        text: "partial bot text",
      });
    });

    expect(onAddVoiceMessage).not.toHaveBeenCalled();
  });

  it("updates speaking state for user and bot events", () => {
    mockState.transportState = "connected";

    const onAddVoiceMessage = vi.fn();

    const { result } = renderHook(() =>
      useVoiceChat({
        onAddVoiceMessage,
      }),
    );

    act(() => {
      mockState.eventHandlers[RTVIEvent.UserStartedSpeaking]();
    });

    expect(result.current.isUserSpeaking).toBe(true);
    expect(result.current.isVoiceActive).toBe(true);

    act(() => {
      mockState.eventHandlers[RTVIEvent.UserStoppedSpeaking]();
    });

    expect(result.current.isUserSpeaking).toBe(false);

    act(() => {
      mockState.eventHandlers[RTVIEvent.BotStartedSpeaking]();
    });

    expect(result.current.isBotSpeaking).toBe(true);
    expect(result.current.isVoiceActive).toBe(true);

    act(() => {
      mockState.eventHandlers[RTVIEvent.BotStoppedSpeaking]();
    });

    expect(result.current.isBotSpeaking).toBe(false);
    expect(result.current.isVoiceActive).toBe(false);
  });
});
