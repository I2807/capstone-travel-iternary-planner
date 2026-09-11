interface StatusBannerProps {
  message: string;
  tone?: "status" | "error";
  actionLabel?: string;
  onAction?: () => void;
}

export function StatusBanner({
  message,
  tone = "status",
  actionLabel,
  onAction,
}: StatusBannerProps) {
  return (
    <div className={`status-banner status-${tone}`} role={tone === "error" ? "alert" : "status"}>
      <span>{message}</span>
      {actionLabel && onAction ? (
        <button type="button" onClick={onAction}>
          {actionLabel}
        </button>
      ) : null}
    </div>
  );
}
