import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import { Composer } from "../../src/components/Composer";

describe("Composer", () => {
  it("submits on Enter and keeps Shift+Enter as a newline", async () => {
    const user = userEvent.setup();
    const onSubmit = vi.fn();
    render(<Composer onSubmit={onSubmit} />);
    const input = screen.getByRole("textbox", { name: /message/i });

    await user.type(input, "Plan Goa");
    await user.keyboard("{Shift>}{Enter}{/Shift}");
    await user.type(input, "for four days");
    expect(onSubmit).not.toHaveBeenCalled();
    expect(input).toHaveValue("Plan Goa\nfor four days");

    await user.keyboard("{Enter}");
    expect(onSubmit).toHaveBeenCalledWith("Plan Goa\nfor four days");
  });

  it("exposes an accessible submit control and can be disabled", () => {
    render(<Composer onSubmit={vi.fn()} disabled />);

    expect(screen.getByRole("button", { name: /send/i })).toBeDisabled();
    expect(screen.getByRole("textbox", { name: /message/i })).toBeDisabled();
  });
});
