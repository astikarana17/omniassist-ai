"use client";

import { useEffect, useState } from "react";
import { Search, ChevronsUpDown, LogOut, User as UserIcon, Settings, Bell } from "lucide-react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useUiStore } from "@/store/ui-store";
import { useAuthStore } from "@/store/auth-store";
import { useLogout } from "@/lib/api-hooks";
import { UserAvatar } from "@/components/shared/user-avatar";
import { ThemeToggle } from "@/components/shared/theme-toggle";
import { NotificationsPopover } from "@/components/layout/notifications-popover";
import { MobileNav } from "@/components/layout/mobile-nav";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { currentUser } from "@/lib/data";

export function Navbar() {
  const { setCommandOpen } = useUiStore();
  const router = useRouter();
  const logout = useLogout();
  const { user, org } = useAuthStore();
  // Persisted store rehydrates on the client, so gate behind mount to match SSR.
  const [mounted, setMounted] = useState(false);
  useEffect(() => setMounted(true), []);

  // Show the signed-in user/org when authenticated; fall back to demo data.
  const name = (mounted && user?.fullName) || currentUser.name;
  const email = (mounted && user?.email) || currentUser.email;
  const avatar = mounted ? user?.avatarUrl ?? (user ? undefined : currentUser.avatar) : currentUser.avatar;
  const orgName = (mounted && org?.name) || "Acme Inc";
  const orgInitial = (orgName[0] ?? "A").toUpperCase();

  const signOut = async () => {
    await logout.mutateAsync();
    router.push("/login");
  };

  return (
    <header className="sticky top-0 z-40 flex h-14 items-center gap-2 border-b border-border bg-background/70 px-4 backdrop-blur-xl">
      <MobileNav />

      {/* Org switcher */}
      <DropdownMenu>
        <DropdownMenuTrigger asChild>
          <button className="hidden items-center gap-2 rounded-md px-2 py-1.5 text-sm font-medium transition-colors hover:bg-accent sm:flex">
            <span className="flex h-6 w-6 items-center justify-center rounded-md bg-gradient-brand text-[11px] font-bold text-white">
              {orgInitial}
            </span>
            {orgName}
            <ChevronsUpDown className="h-3.5 w-3.5 text-muted-foreground" />
          </button>
        </DropdownMenuTrigger>
        <DropdownMenuContent align="start" className="w-56">
          <DropdownMenuLabel>Workspace</DropdownMenuLabel>
          <DropdownMenuItem>
            <span className="flex h-5 w-5 items-center justify-center rounded bg-gradient-brand text-[10px] font-bold text-white">
              {orgInitial}
            </span>
            {orgName}
          </DropdownMenuItem>
          <DropdownMenuSeparator />
          <DropdownMenuItem>Create workspace</DropdownMenuItem>
        </DropdownMenuContent>
      </DropdownMenu>

      {/* Search trigger */}
      <button
        onClick={() => setCommandOpen(true)}
        className="group ml-1 flex h-9 flex-1 items-center gap-2 rounded-md border border-border-strong bg-background/40 px-3 text-sm text-muted-foreground transition-colors hover:border-primary/40 sm:max-w-xs"
      >
        <Search className="h-4 w-4" />
        <span className="flex-1 text-left">Search…</span>
        <kbd className="hidden rounded border border-border-strong px-1.5 py-0.5 text-[10px] sm:inline">
          ⌘K
        </kbd>
      </button>

      <div className="ml-auto flex items-center gap-1">
        <ThemeToggle />
        <NotificationsPopover />

        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <button className="ml-1 rounded-full outline-none ring-offset-background focus-visible:ring-2 focus-visible:ring-ring">
              <UserAvatar name={name} src={avatar} className="h-8 w-8" />
            </button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end" className="w-60">
            <div className="flex items-center gap-3 px-2 py-2">
              <UserAvatar name={name} src={avatar} className="h-9 w-9" />
              <div className="min-w-0">
                <p className="truncate text-sm font-medium">{name}</p>
                <p className="truncate text-xs text-muted-foreground">{email}</p>
              </div>
            </div>
            <DropdownMenuSeparator />
            <DropdownMenuItem asChild>
              <Link href="/profile">
                <UserIcon /> Profile
              </Link>
            </DropdownMenuItem>
            <DropdownMenuItem asChild>
              <Link href="/settings">
                <Settings /> Settings
              </Link>
            </DropdownMenuItem>
            <DropdownMenuItem asChild>
              <Link href="/notifications">
                <Bell /> Notifications
              </Link>
            </DropdownMenuItem>
            <DropdownMenuSeparator />
            <DropdownMenuItem
              onClick={signOut}
              className="text-danger focus:text-danger"
            >
              <LogOut /> Sign out
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>
    </header>
  );
}
