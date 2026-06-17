"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard,
  Pill,
  CalendarClock,
  UsersRound,
  MessageCircleHeart,
} from "lucide-react";
import { cn } from "@/lib/utils";

const items = [
  { label: "Home", href: "/dashboard", icon: LayoutDashboard },
  { label: "Rx AI", href: "/prescriptions", icon: Pill },
  { label: "Appts", href: "/appointments", icon: CalendarClock },
  { label: "Patients", href: "/patients", icon: UsersRound },
];

export function BottomNav() {
  const pathname = usePathname();

  return (
    <nav className="fixed bottom-0 left-0 right-0 z-40 flex h-16 items-center justify-around border-t border-border bg-background/80 px-2 backdrop-blur-xl lg:hidden">
      {items.map((item) => {
        const active =
          pathname === item.href ||
          (item.href !== "/dashboard" && pathname.startsWith(item.href));
        const Icon = item.icon;
        return (
          <Link
            key={item.href}
            href={item.href}
            className={cn(
              "flex flex-1 flex-col items-center gap-0.5 py-1.5 text-[10px] font-medium transition-colors",
              active ? "text-primary" : "text-muted-foreground"
            )}
          >
            <Icon className="h-5 w-5" />
            {item.label}
          </Link>
        );
      })}
      <Link
        href="/health-assistant"
        className="flex flex-1 flex-col items-center gap-0.5 py-1.5 text-[10px] font-medium text-ai"
      >
        <span className="flex h-7 w-7 items-center justify-center rounded-full bg-gradient-ai">
          <MessageCircleHeart className="h-4 w-4 text-white" />
        </span>
        Assistant
      </Link>
    </nav>
  );
}
