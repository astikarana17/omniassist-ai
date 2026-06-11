"use client";

import { useState, useRef } from "react";
import {
  Send,
  Paperclip,
  Smile,
  Mic,
  Sparkles,
  Languages,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

const quickQuestions = [
  "What does OmniAssist do?",
  "What's included in the Growth plan?",
  "How do I set up the WhatsApp agent?",
  "What's your refund policy?",
  "Do you support SSO?",
  "How does the AI Sales Agent work?",
  "Is my data secure?",
];

export function ChatComposer({ onSend }: { onSend: (text: string) => void }) {
  const [value, setValue] = useState("");
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const submit = () => {
    if (!value.trim()) return;
    onSend(value.trim());
    setValue("");
    if (textareaRef.current) textareaRef.current.style.height = "auto";
  };

  return (
    <div className="border-t border-border bg-background/60 p-3 backdrop-blur">
      {value.trim() === "" && (
        <div className="mb-2 flex flex-wrap items-center gap-2">
          <span className="flex items-center gap-1 text-[11px] font-medium text-ai">
            <Sparkles className="h-3 w-3" /> Try asking
          </span>
          {quickQuestions.map((s) => (
            <button
              key={s}
              onClick={() => onSend(s)}
              className="rounded-full border border-border-strong bg-subtle px-3 py-1 text-xs transition-colors hover:border-ai/40 hover:text-ai"
            >
              {s}
            </button>
          ))}
        </div>
      )}

      <div className="flex items-end gap-2 rounded-xl border border-border-strong bg-card p-2 focus-within:border-primary/50">
        <div className="flex items-center gap-0.5">
          <Button variant="ghost" size="icon-sm" type="button" aria-label="Attach">
            <Paperclip className="h-4 w-4" />
          </Button>
          <Button variant="ghost" size="icon-sm" type="button" aria-label="Emoji">
            <Smile className="h-4 w-4" />
          </Button>
        </div>
        <textarea
          ref={textareaRef}
          value={value}
          onChange={(e) => {
            setValue(e.target.value);
            e.target.style.height = "auto";
            e.target.style.height = Math.min(e.target.scrollHeight, 140) + "px";
          }}
          onKeyDown={(e) => {
            if (e.key === "Enter" && !e.shiftKey) {
              e.preventDefault();
              submit();
            }
          }}
          rows={1}
          placeholder="Type a message…  (use / for AI commands)"
          className="max-h-[140px] flex-1 resize-none bg-transparent py-1.5 text-sm outline-none placeholder:text-muted-foreground"
        />
        <div className="flex items-center gap-0.5">
          <Button variant="ghost" size="icon-sm" type="button" aria-label="Translate">
            <Languages className="h-4 w-4" />
          </Button>
          <Button variant="ghost" size="icon-sm" type="button" aria-label="Voice message">
            <Mic className="h-4 w-4" />
          </Button>
          <Button
            size="icon-sm"
            variant="gradient"
            onClick={submit}
            disabled={!value.trim()}
            className={cn(!value.trim() && "opacity-50")}
            aria-label="Send"
          >
            <Send className="h-4 w-4" />
          </Button>
        </div>
      </div>
    </div>
  );
}
