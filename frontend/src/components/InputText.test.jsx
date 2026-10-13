// @vitest-environment jsdom

import "@testing-library/jest-dom/vitest";

import { cleanup, render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import InputText from "./InputText";
import { useVoiceChat } from "../hooks/useVoiceChat";

vi.mock("../hooks/useVoiceChat", () => ({
  useVoiceChat: vi.fn(),
}));

const createDefaultVoiceState = (overrides = {}) => ({
  voiceError: null,
  isVoiceConnected: false,
  isVoiceConnecting: false,
  isUserSpeaking: false,
  isVoiceActive: false,
  handleVoiceClick: vi.fn(),
  ...overrides,
});

describe("InputText", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    useVoiceChat.mockReturnValue(createDefaultVoiceState());
  });

  afterEach(() => {
    cleanup();
  });

  it("renders the text input and action buttons", () => {
    render(
      <InputText
        onSendMessage={vi.fn()}
        onClearChat={vi.fn()}
        onAddVoiceMessage={vi.fn()}
        isLoading={false}
      />,
    );

    expect(screen.getByLabelText(/question input/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/send message/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/clear chat/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/voice input/i)).toBeInTheDocument();
  });

  it("sends a message and clears the input on submit", async () => {
    const user = userEvent.setup();
    const onSendMessage = vi.fn();

    render(
      <InputText
        onSendMessage={onSendMessage}
        onClearChat={vi.fn()}
        onAddVoiceMessage={vi.fn()}
        isLoading={false}
      />,
    );

    const input = screen.getByLabelText(/question input/i);

    await user.type(input, "I want chocolate");
    await user.click(screen.getByLabelText(/send message/i));

    expect(onSendMessage).toHaveBeenCalledWith("I want chocolate");
    expect(input).toHaveValue("");
  });

  it("does not send an empty message", async () => {
    const user = userEvent.setup();
    const onSendMessage = vi.fn();

    render(
      <InputText
        onSendMessage={onSendMessage}
        onClearChat={vi.fn()}
        onAddVoiceMessage={vi.fn()}
        isLoading={false}
      />,
    );

    await user.click(screen.getByLabelText(/send message/i));

    expect(onSendMessage).not.toHaveBeenCalled();
  });

  it("calls onClearChat when clear button is clicked", async () => {
    const user = userEvent.setup();
    const onClearChat = vi.fn();

    render(
      <InputText
        onSendMessage={vi.fn()}
        onClearChat={onClearChat}
        onAddVoiceMessage={vi.fn()}
        isLoading={false}
      />,
    );

    await user.click(screen.getByLabelText(/clear chat/i));

    expect(onClearChat).toHaveBeenCalled();
  });

  it("disables text input and send button while loading", () => {
    render(
      <InputText
        onSendMessage={vi.fn()}
        onClearChat={vi.fn()}
        onAddVoiceMessage={vi.fn()}
        isLoading={true}
      />,
    );

    expect(screen.getByLabelText(/question input/i)).toBeDisabled();
    expect(screen.getByLabelText(/send message/i)).toBeDisabled();
    expect(screen.getByLabelText(/voice input/i)).toBeDisabled();
  });

  it("calls handleVoiceClick when voice button is clicked", async () => {
    const user = userEvent.setup();
    const handleVoiceClick = vi.fn();

    useVoiceChat.mockReturnValue(
      createDefaultVoiceState({
        handleVoiceClick,
      }),
    );

    render(
      <InputText
        onSendMessage={vi.fn()}
        onClearChat={vi.fn()}
        onAddVoiceMessage={vi.fn()}
        isLoading={false}
      />,
    );

    await user.click(screen.getByLabelText(/voice input/i));

    expect(handleVoiceClick).toHaveBeenCalled();
  });

  it("shows voice live panel when voice is active", () => {
    useVoiceChat.mockReturnValue(
      createDefaultVoiceState({
        isVoiceActive: true,
        isUserSpeaking: true,
      }),
    );

    render(
      <InputText
        onSendMessage={vi.fn()}
        onClearChat={vi.fn()}
        onAddVoiceMessage={vi.fn()}
        isLoading={false}
      />,
    );

    expect(screen.queryByLabelText(/question input/i)).not.toBeInTheDocument();
    expect(screen.getByText(/listening/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/send message/i)).toBeDisabled();
  });

  it("shows assistant responding text when bot is speaking", () => {
    useVoiceChat.mockReturnValue(
      createDefaultVoiceState({
        isVoiceActive: true,
        isUserSpeaking: false,
      }),
    );

    render(
      <InputText
        onSendMessage={vi.fn()}
        onClearChat={vi.fn()}
        onAddVoiceMessage={vi.fn()}
        isLoading={false}
      />,
    );

    expect(screen.getByText(/assistant is responding/i)).toBeInTheDocument();
  });

  it("shows voice error message", () => {
    useVoiceChat.mockReturnValue(
      createDefaultVoiceState({
        voiceError: "Voice connection failed. Please check the voice server.",
      }),
    );

    render(
      <InputText
        onSendMessage={vi.fn()}
        onClearChat={vi.fn()}
        onAddVoiceMessage={vi.fn()}
        isLoading={false}
      />,
    );

    expect(
      screen.getByText(
        "Voice connection failed. Please check the voice server.",
      ),
    ).toBeInTheDocument();
  });

  it("shows correct voice button title when connected", () => {
    useVoiceChat.mockReturnValue(
      createDefaultVoiceState({
        isVoiceConnected: true,
      }),
    );

    render(
      <InputText
        onSendMessage={vi.fn()}
        onClearChat={vi.fn()}
        onAddVoiceMessage={vi.fn()}
        isLoading={false}
      />,
    );

    expect(screen.getByLabelText(/voice input/i)).toHaveAttribute(
      "title",
      "Stop voice chat",
    );
  });

  it("shows correct voice button title when connecting", () => {
    useVoiceChat.mockReturnValue(
      createDefaultVoiceState({
        isVoiceConnecting: true,
      }),
    );

    render(
      <InputText
        onSendMessage={vi.fn()}
        onClearChat={vi.fn()}
        onAddVoiceMessage={vi.fn()}
        isLoading={false}
      />,
    );

    expect(screen.getByLabelText(/voice input/i)).toHaveAttribute(
      "title",
      "Connecting voice...",
    );
  });
});
