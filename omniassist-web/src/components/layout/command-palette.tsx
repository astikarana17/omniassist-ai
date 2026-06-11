"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { Command } from "cmdk";
import {
  LayoutDashboard,
  Inbox,
  Ticket,
  Target,
  BookOpen,
  BarChart3,
  Users,
  Settings,
  Sparkles,
  Plus,
  UserPlus,
  CheckCircle2,
  Search,
} from "lucide-react";
import { useUiStore } from "@/store/ui-store";
import { conversations, tickets, leads } from "@/lib/data";

const navActions = [
  { label: "Dashboard", href: "/dashboard", icon: LayoutDashboard },
  { label: "Inbox", href: "/inbox", icon: Inbox },
  { label: "Tickets", href: "/tickets", icon: Ticket },
  { label: "Leads", href: "/leads", icon: Target },
  { label: "CRM Pipeline", href: "/leads/pipeline", icon: Target },
  { label: "AI Agents", href: "/agents/support", icon: Sparkles },
  { label: "Knowledge Base", href: "/knowledge-base", icon: BookOpen },
  { label: "Analytics", href: "/analytics", icon: BarChart3 },
  { label: "Team", href: "/team", icon: Users },
  { label: "Settings", href: "/settings", icon: Settings },
];

const quickActions = [
  { label: "Create new ticket", icon: Plus, href: "/tickets?new=1" },
  { label: "Add a lead", icon: Target, href: "/leads?new=1" },
  { label: "Invite team member", icon: UserPlus, href: "/team?invite=1" },
  { label: "Resolve current conversation", icon: CheckCircle2, href: "/inbox" },
];

export function CommandPalette() {
  const { commandOpen, setCommandOpen, toggleCommand } = useUiStore();
  const router = useRouter();

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === "k") {
        e.preventDefault();
        toggleCommand();
      }
    };
    document.addEventListener("keydown", onKey);
    return () => document.removeEventListener("keydown", onKey);
  }, [toggleCommand]);

  const go = (href: string) => {
    setCommandOpen(false);
    router.push(href);
  };

  if (!commandOpen) return null;

  return (
    <div
      className="fixed inset-0 z-[1500] flex items-start justify-center bg-black/60 p-4 pt-[15vh] backdrop-blur-sm animate-in fade-in-0"
      onClick={() => setCommandOpen(false)}
    >
      <div
        className="w-full max-w-xl overflow-hidden rounded-xl border border-border-strong bg-popover shadow-xl animate-in zoom-in-95 slide-in-from-top-2"
        onClick={(e) => e.stopPropagation()}
      >
        <Command className="[&_[cmdk-group-heading]]:px-3 [&_[cmdk-group-heading]]:py-2 [&_[cmdk-group-heading]]:text-xs [&_[cmdk-group-heading]]:font-medium [&_[cmdk-group-heading]]:text-muted-foreground">
          <div className="flex items-center gap-2 border-b border-border px-4">
            <Search className="h-4 w-4 text-muted-foreground" />
            <Command.Input
              autoFocus
              placeholder="Search or jump to…"
              className="h-12 w-full bg-transparent text-sm outline-none placeholder:text-muted-foreground"
            />
            <kbd className="rounded border border-border-strong px-1.5 py-0.5 text-[10px] text-muted-foreground">
              ESC
            </kbd>
          </div>
          <Command.List className="max-h-[60vh] overflow-y-auto p-2">
            <Command.Empty className="py-8 text-center text-sm text-muted-foreground">
              No results found.
            </Command.Empty>

            <Command.Group heading="Navigation">
              {navActions.map((a) => (
                <Command.Item
                  key={a.href}
                  value={`nav ${a.label}`}
                  onSelect={() => go(a.href)}
                  className="flex cursor-pointer items-center gap-3 rounded-md px-3 py-2.5 text-sm aria-selected:bg-accent"
                >
                  <a.icon className="h-4 w-4 text-muted-foreground" />
                  {a.label}
                </Command.Item>
              ))}
            </Command.Group>

            <Command.Group heading="Quick actions">
              {quickActions.map((a) => (
                <Command.Item
                  key={a.label}
                  value={`action ${a.label}`}
                  onSelect={() => go(a.href)}
                  className="flex cursor-pointer items-center gap-3 rounded-md px-3 py-2.5 text-sm aria-selected:bg-accent"
                >
                  <a.icon className="h-4 w-4 text-primary" />
                  {a.label}
                </Command.Item>
              ))}
            </Command.Group>

            <Command.Group heading="Conversations">
              {conversations.slice(0, 4).map((c) => (
                <Command.Item
                  key={c.id}
                  value={`conversation ${c.contact.name} ${c.subject}`}
                  onSelect={() => go(`/inbox/${c.id}`)}
                  className="flex cursor-pointer items-center gap-3 rounded-md px-3 py-2.5 text-sm aria-selected:bg-accent"
                >
                  <Inbox className="h-4 w-4 text-muted-foreground" />
                  <span className="truncate">{c.subject}</span>
                  <span className="ml-auto text-xs text-muted-foreground">
                    {c.contact.name}
                  </span>
                </Command.Item>
              ))}
            </Command.Group>

            <Command.Group heading="Tickets">
              {tickets.slice(0, 4).map((t) => (
                <Command.Item
                  key={t.id}
                  value={`ticket ${t.number} ${t.subject}`}
                  onSelect={() => go(`/tickets/${t.id}`)}
                  className="flex cursor-pointer items-center gap-3 rounded-md px-3 py-2.5 text-sm aria-selected:bg-accent"
                >
                  <Ticket className="h-4 w-4 text-muted-foreground" />
                  <span className="truncate">#{t.number} · {t.subject}</span>
                </Command.Item>
              ))}
            </Command.Group>

            <Command.Group heading="Leads">
              {leads.slice(0, 3).map((l) => (
                <Command.Item
                  key={l.id}
                  value={`lead ${l.name} ${l.company}`}
                  onSelect={() => go(`/leads`)}
                  className="flex cursor-pointer items-center gap-3 rounded-md px-3 py-2.5 text-sm aria-selected:bg-accent"
                >
                  <Target className="h-4 w-4 text-muted-foreground" />
                  <span className="truncate">{l.name}</span>
                  <span className="ml-auto text-xs text-muted-foreground">
                    Score {l.score}
                  </span>
                </Command.Item>
              ))}
            </Command.Group>
          </Command.List>
        </Command>
      </div>
    </div>
  );
}
