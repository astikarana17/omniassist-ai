export function TypingIndicator() {
  return (
    <div className="flex items-center gap-1 rounded-2xl border border-border bg-subtle px-3.5 py-3 w-fit">
      {[0, 1, 2].map((i) => (
        <span
          key={i}
          className="h-1.5 w-1.5 rounded-full bg-ai"
          style={{
            animation: "pulse-dot 1.2s ease-in-out infinite",
            animationDelay: `${i * 0.18}s`,
          }}
        />
      ))}
    </div>
  );
}
