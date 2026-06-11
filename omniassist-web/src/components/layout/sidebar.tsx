"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { motion, AnimatePresence } from "framer-motion";
import { ChevronDown, PanelLeftClose, PanelLeft } from "lucide-react";
import { useState } from "react";
import { navItems, type NavItem } from "@/lib/nav";
import { useUiStore } from "@/store/ui-store";
import { cn } from "@/lib/utils";
import { Logo } from "@/components/shared/logo";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip";

export function Sidebar() {
  const pathname = usePathname();
  const { sidebarCollapsed, toggleSidebar } = useUiStore();

  return (
    <motion.aside
      initial={false}
      animate={{ width: sidebarCollapsed ? 72 : 264 }}
      transition={{ type: "spring", stiffness: 320, damping: 32 }}
      className="relative z-30 hidden h-screen shrink-0 flex-col border-r border-border bg-subtle/60 lg:flex"
    >
      <div className="flex h-14 items-center gap-2 px-4">
        <Logo collapsed={sidebarCollapsed} />
      </div>

      <nav className="flex-1 space-y-1 overflow-y-auto no-scrollbar px-3 py-3">
        {navItems.map((item) => (
          <SidebarItem
            key={item.href}
            item={item}
            pathname={pathname}
            collapsed={sidebarCollapsed}
          />
        ))}
      </nav>

      <div className="border-t border-border p-3">
        <button
          onClick={toggleSidebar}
          className="flex w-full items-center gap-3 rounded-md px-3 py-2 text-sm text-muted-foreground transition-colors hover:bg-accent hover:text-foreground"
        >
          {sidebarCollapsed ? (
            <PanelLeft className="h-4 w-4" />
          ) : (
            <>
              <PanelLeftClose className="h-4 w-4" />
              <span>Collapse</span>
            </>
          )}
        </button>
      </div>
    </motion.aside>
  );
}

function SidebarItem({
  item,
  pathname,
  collapsed,
}: {
  item: NavItem;
  pathname: string;
  collapsed: boolean;
}) {
  const isActive =
    pathname === item.href ||
    (item.href !== "/dashboard" && pathname.startsWith(item.href));
  const hasChildren = !!item.children?.length;
  const [open, setOpen] = useState(isActive);
  const Icon = item.icon;

  const link = (
    <Link
      href={item.href}
      onClick={(e) => {
        if (hasChildren && !collapsed) {
          e.preventDefault();
          setOpen((o) => !o);
        }
      }}
      className={cn(
        "group relative flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium transition-colors",
        isActive
          ? "text-foreground"
          : "text-muted-foreground hover:bg-accent hover:text-foreground",
        collapsed && "justify-center"
      )}
    >
      {isActive && (
        <motion.span
          layoutId="nav-active"
          className="absolute inset-0 rounded-md bg-primary/10 ring-1 ring-primary/20"
          transition={{ type: "spring", stiffness: 380, damping: 32 }}
        />
      )}
      {isActive && (
        <span className="absolute left-0 top-1/2 h-5 w-0.5 -translate-y-1/2 rounded-full bg-gradient-brand" />
      )}
      <Icon
        className={cn(
          "relative h-4 w-4 shrink-0",
          isActive && "text-primary"
        )}
      />
      {!collapsed && (
        <>
          <span className="relative flex-1 truncate">{item.label}</span>
          {item.badge ? (
            <span className="relative rounded-full bg-primary/15 px-1.5 py-0.5 text-[10px] font-semibold text-primary">
              {item.badge}
            </span>
          ) : null}
          {hasChildren && (
            <ChevronDown
              className={cn(
                "relative h-3.5 w-3.5 transition-transform",
                open && "rotate-180"
              )}
            />
          )}
        </>
      )}
    </Link>
  );

  return (
    <div>
      {collapsed ? (
        <TooltipProvider delayDuration={0}>
          <Tooltip>
            <TooltipTrigger asChild>{link}</TooltipTrigger>
            <TooltipContent side="right">{item.label}</TooltipContent>
          </Tooltip>
        </TooltipProvider>
      ) : (
        link
      )}

      <AnimatePresence initial={false}>
        {hasChildren && open && !collapsed && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: "auto", opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.2 }}
            className="overflow-hidden"
          >
            <div className="ml-4 mt-1 space-y-0.5 border-l border-border pl-3">
              {item.children!.map((child) => {
                const childActive = pathname === child.href;
                return (
                  <Link
                    key={child.href}
                    href={child.href}
                    className={cn(
                      "block rounded-md px-3 py-1.5 text-sm transition-colors",
                      childActive
                        ? "bg-accent text-foreground"
                        : "text-muted-foreground hover:bg-accent/60 hover:text-foreground"
                    )}
                  >
                    {child.label}
                  </Link>
                );
              })}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
