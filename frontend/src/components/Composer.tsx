import { useState, type FormEvent, type KeyboardEvent } from "react";

interface ComposerProps {
  onSubmit: (content: string) => void | Promise<void>;
  disabled?: boolean;
}

export function Composer({ onSubmit, disabled = false }: ComposerProps) {
  const [value, setValue] = useState("");

  const submit = () => {
    const normalizedValue = value.trim();
    if (!normalizedValue || disabled) {
      return;
    }
    setValue("");
    void onSubmit(normalizedValue);
  };

  const handleSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    submit();
  };

  const handleKeyDown = (event: KeyboardEvent<HTMLTextAreaElement>) => {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      submit();
    }
  };

  return (
    <form className="composer" onSubmit={handleSubmit}>
      <label className="sr-only" htmlFor="chat-message">
        Message
      </label>
      <textarea
        id="chat-message"
        name="message"
        value={value}
        onChange={(event) => setValue(event.target.value)}
        onKeyDown={handleKeyDown}
        placeholder="Where would you like to go?"
        rows={2}
        disabled={disabled}
        aria-describedby="composer-hint"
      />
      <div className="composer-footer">
        <span id="composer-hint">Press Enter to send. Use Shift+Enter for a new line.</span>
        <button type="submit" disabled={disabled || !value.trim()} aria-label="Send message">
          Send
        </button>
      </div>
    </form>
  );
}
