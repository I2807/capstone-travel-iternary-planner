import { useChat } from "../hooks/useChat";
import { Composer } from "./Composer";
import { ItineraryView } from "./ItineraryView";
import { MessageList } from "./MessageList";
import { StatusBanner } from "./StatusBanner";

export function ChatShell() {
  const chat = useChat();

  return (
    <main className="app-shell">
      <header className="app-header">
        <a className="brand" href="/" aria-label="Voyager AI home">
          <span className="brand-symbol" aria-hidden="true">
            V
          </span>
          <span>
            <strong>Voyager AI</strong>
            <small>Travel, considered.</small>
          </span>
        </a>
        <button className="new-chat-button" type="button" onClick={chat.newChat}>
          New chat
        </button>
      </header>

      <div className="workspace">
        <section className="conversation-panel" aria-label="Travel planning conversation">
          <MessageList messages={chat.messages} onSuggestedPrompt={chat.sendMessage} />
          {chat.isLoading ? <StatusBanner message="Voyager is shaping your route..." /> : null}
          {chat.error ? (
            <StatusBanner
              message={`${chat.error.message}${chat.error.requestId ? ` Request ID: ${chat.error.requestId}` : ""}`}
              tone="error"
              actionLabel={chat.canRetry ? "Retry" : undefined}
              onAction={chat.canRetry ? chat.retry : undefined}
            />
          ) : null}
          <Composer onSubmit={chat.sendMessage} disabled={chat.isLoading} />
        </section>

        <aside className="itinerary-panel" aria-label="Itinerary preview">
          {chat.itinerary ? (
            <ItineraryView itinerary={chat.itinerary} />
          ) : (
            <div className="itinerary-placeholder">
              <span className="placeholder-line" aria-hidden="true" />
              <p className="eyebrow">Itinerary preview</p>
              <h2>Your days will take shape here.</h2>
              <p>Once Voyager has your destination and constraints, the plan will stay beside the conversation.</p>
            </div>
          )}
        </aside>
      </div>
    </main>
  );
}
