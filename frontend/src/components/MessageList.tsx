import type { Message } from "../types/domain";
import { SuggestedPrompts } from "./SuggestedPrompts";

interface MessageListProps {
  messages: Message[];
  suggestedPrompts?: string[];
  onSuggestedPrompt?: (prompt: string) => void;
}

const defaultPrompts = [
  "Plan a 4-day Goa trip for two people under INR 25000",
  "What should I pack for Kerala?",
  "Suggest a family-friendly weekend escape",
];

export function MessageList({
  messages,
  suggestedPrompts = defaultPrompts,
  onSuggestedPrompt,
}: MessageListProps) {
  if (messages.length === 0) {
    return (
      <div className="message-list message-list-empty">
        <div className="welcome-mark" aria-hidden="true">
          V
        </div>
        <h1>Plan somewhere worth remembering.</h1>
        <p className="welcome-copy">
          Tell Voyager where you want to go, how long you have, and what you want to feel along the way.
        </p>
        <SuggestedPrompts onSelect={onSuggestedPrompt ?? (() => undefined)} prompts={suggestedPrompts} />
      </div>
    );
  }

  return (
    <ol className="message-list" aria-live="polite" aria-label="Conversation">
      {messages.map((message, index) => (
        <li
          className={`message message-${message.role}`}
          aria-label={`${message.role === "user" ? "User" : "Assistant"} message`}
          key={`${message.timestamp}-${index}`}
        >
          <span className="message-label">{message.role === "user" ? "You" : "Voyager"}</span>
          <p>{message.content}</p>
        </li>
      ))}
    </ol>
  );
}
