interface SuggestedPromptsProps {
  prompts: string[];
  onSelect: (prompt: string) => void;
}

export function SuggestedPrompts({ prompts, onSelect }: SuggestedPromptsProps) {
  return (
    <section className="suggested-prompts" aria-labelledby="suggested-prompts-title">
      <p id="suggested-prompts-title" className="eyebrow">
        Start with a trip idea
      </p>
      <div className="prompt-list">
        {prompts.map((prompt) => (
          <button key={prompt} type="button" onClick={() => onSelect(prompt)}>
            {prompt}
          </button>
        ))}
      </div>
    </section>
  );
}
