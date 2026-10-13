// @vitest-environment jsdom

import "@testing-library/jest-dom/vitest";

import { cleanup, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it } from "vitest";

import QuestionResponse from "./QuestionResponse";

describe("QuestionResponse", () => {
  afterEach(() => {
    cleanup();
  });

  it("renders user messages", () => {
    const messages = [
      {
        id: 1,
        role: "user",
        text: "I want chocolate",
      },
    ];

    render(<QuestionResponse messages={messages} isLoading={false} />);

    expect(screen.getByText("I want chocolate")).toBeInTheDocument();
  });

  it("renders bot messages", () => {
    const messages = [
      {
        id: 1,
        role: "bot",
        text: "German chocolate is available.",
      },
    ];

    render(<QuestionResponse messages={messages} isLoading={false} />);

    expect(
      screen.getByText("German chocolate is available."),
    ).toBeInTheDocument();
  });

  it("renders markdown in bot messages", () => {
    const messages = [
      {
        id: 1,
        role: "bot",
        text: "**Chocolate is available**",
      },
    ];

    render(<QuestionResponse messages={messages} isLoading={false} />);

    const markdownText = screen.getByText("Chocolate is available");

    expect(markdownText).toBeInTheDocument();
    expect(markdownText.tagName).toBe("STRONG");
  });

  it("renders loading state", () => {
    render(<QuestionResponse messages={[]} isLoading={true} />);

    expect(screen.getByText(/thinking/i)).toBeInTheDocument();
  });

  it("does not render loading state when isLoading is false", () => {
    render(<QuestionResponse messages={[]} isLoading={false} />);

    expect(screen.queryByText(/thinking/i)).not.toBeInTheDocument();
  });

  it("renders the chat section with accessible label", () => {
    render(<QuestionResponse messages={[]} isLoading={false} />);

    expect(
      screen.getByRole("region", {
        name: /chat messages/i,
      }),
    ).toBeInTheDocument();
  });

  it("renders error messages", () => {
    const messages = [
      {
        id: 1,
        role: "bot",
        text: "Sorry, something went wrong.",
        isError: true,
      },
    ];

    render(<QuestionResponse messages={messages} isLoading={false} />);

    expect(
      screen.getByText("Sorry, something went wrong."),
    ).toBeInTheDocument();
  });
});
