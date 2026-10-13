import { describe, expect, it } from "vitest";

import { normalizeText } from "./textUtils";

describe("normalizeText", () => {
  it("removes leading and trailing spaces", () => {
    expect(normalizeText("  hello world  ")).toBe("hello world");
  });

  it("replaces multiple spaces with one space", () => {
    expect(normalizeText("hello     world")).toBe("hello world");
  });

  it("replaces tabs and new lines with one space", () => {
    expect(normalizeText("hello\n\tworld")).toBe("hello world");
  });

  it("returns an empty string for null or undefined", () => {
    expect(normalizeText(null)).toBe("");
    expect(normalizeText(undefined)).toBe("");
  });

  it("converts numbers to text", () => {
    expect(normalizeText(123)).toBe("123");
  });
});
