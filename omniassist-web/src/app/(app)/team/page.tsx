"use client";

import { useState } from "react";
import { UserPlus, Check, Shield, MoreHorizontal, Mail } from "lucide-react";
import { PageHeader } from "@/components/shared/page-header";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { UserAvatar } from "@/components/shared/user-avatar";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { toast } from "sonner";
import { users as mockUsers } from "@/lib/data";
import type { Role } from "@/types";
import { relativeTime } from "@/lib/utils";
import { useMembers, useInviteMember, apiConfigured } from "@/lib/api-hooks";

const roleVariant: Record<Role, React.ComponentProps<typeof Badge>["variant"]> = {
  owner: "default",
  admin: "ai",
  agent: "info",
  viewer: "secondary",
};

const permissions = [
  { group: "Conversations", items: ["View", "Reply", "Handoff", "Delete"] },
  { group: "Tickets", items: ["View", "Edit", "Assign", "Resolve"] },
  { group: "Knowledge Base", items: ["View", "Edit", "Delete"] },
  { group: "Analytics", items: ["View", "Export"] },
  { group: "Settings", items: ["View", "Manage", "Billing"] },
];

const roleMatrix: Record<Role, (g: string, i: string) => boolean> = {
  owner: () => true,
  admin: (g) => g !== "Settings",
  agent: (g, i) => ["Conversations", "Tickets"].includes(g) || (g === "Knowledge Base" && i === "View") || (g === "Analytics" && i === "View"),
  viewer: (_g, i) => i === "View",
};

const invites = [
  { email: "newhire@acme.com", role: "agent" as Role, sentAt: new Date(Date.now() - 3600_000).toISOString() },
  { email: "analyst@acme.com", role: "viewer" as Role, sentAt: new Date(Date.now() - 86400_000).toISOString() },
];

export default function TeamPage() {
  const [open, setOpen] = useState(false);
  const { data } = useMembers();
  const users = data ?? mockUsers;
  const invite = useInviteMember();
  const [inviteEmail, setInviteEmail] = useState("");
  const [inviteRole, setInviteRole] = useState("support_agent");

  const sendInvite = () => {
    const email = inviteEmail.trim();
    if (!email) return;
    if (!apiConfigured()) {
      toast.success("Invitation sent (demo)");
      setOpen(false);
      return;
    }
    invite.mutate(
      { email, role: inviteRole },
      {
        onSuccess: () => {
          toast.success(`${email} added to the workspace`);
          setOpen(false);
          setInviteEmail("");
        },
        onError: (e) =>
          toast.error(e instanceof Error ? e.message : "Could not invite this member"),
      }
    );
  };

  return (
    <div className="mx-auto max-w-[1400px] space-y-6 p-4 sm:p-6">
      <PageHeader title="Team" description="Manage members, roles and permissions.">
        <Dialog open={open} onOpenChange={setOpen}>
          <DialogTrigger asChild>
            <Button variant="gradient"><UserPlus className="h-4 w-4" /> Invite member</Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Invite a team member</DialogTitle>
              <DialogDescription>They&apos;ll receive an email to join your workspace.</DialogDescription>
            </DialogHeader>
            <div className="space-y-4 py-2">
              <div className="space-y-2">
                <Label htmlFor="invite-email">Email address</Label>
                <Input
                  id="invite-email"
                  type="email"
                  placeholder="teammate@acme.com"
                  value={inviteEmail}
                  onChange={(e) => setInviteEmail(e.target.value)}
                  onKeyDown={(e) => e.key === "Enter" && sendInvite()}
                />
              </div>
              <div className="space-y-2">
                <Label>Role</Label>
                <Select value={inviteRole} onValueChange={setInviteRole}>
                  <SelectTrigger><SelectValue /></SelectTrigger>
                  <SelectContent>
                    <SelectItem value="admin">Admin</SelectItem>
                    <SelectItem value="support_manager">Support Manager</SelectItem>
                    <SelectItem value="support_agent">Support Agent</SelectItem>
                    <SelectItem value="sales_agent">Sales Agent</SelectItem>
                    <SelectItem value="viewer">Viewer</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>
            <DialogFooter>
              <Button variant="secondary" onClick={() => setOpen(false)}>Cancel</Button>
              <Button
                variant="gradient"
                onClick={sendInvite}
                disabled={!inviteEmail.trim()}
                loading={invite.isPending}
              >
                <Mail className="h-4 w-4" /> Send invite
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </PageHeader>

      <Tabs defaultValue="members">
        <TabsList>
          <TabsTrigger value="members">Members ({users.length})</TabsTrigger>
          <TabsTrigger value="roles">Roles & Permissions</TabsTrigger>
          <TabsTrigger value="invites">Invites ({invites.length})</TabsTrigger>
        </TabsList>

        <TabsContent value="members">
          <Card>
            <div className="overflow-x-auto">
              <table className="w-full min-w-[720px] text-sm">
                <thead>
                  <tr className="border-b border-border text-left text-xs text-muted-foreground">
                    <th className="px-4 py-3 font-medium">Member</th>
                    <th className="px-2 py-3 font-medium">Role</th>
                    <th className="px-2 py-3 font-medium">Status</th>
                    <th className="px-2 py-3 font-medium">Last seen</th>
                    <th className="w-10 px-2 py-3" />
                  </tr>
                </thead>
                <tbody>
                  {users.map((u) => (
                    <tr key={u.id} className="group border-b border-border/60 transition-colors last:border-0 hover:bg-accent/40">
                      <td className="px-4 py-3">
                        <div className="flex items-center gap-3">
                          <UserAvatar name={u.name} src={u.avatar} status={u.status} className="h-9 w-9" />
                          <div>
                            <p className="font-medium">{u.name}</p>
                            <p className="text-xs text-muted-foreground">{u.email}</p>
                          </div>
                        </div>
                      </td>
                      <td className="px-2 py-3">
                        <Badge variant={roleVariant[u.role as Role]} className="capitalize">{u.role}</Badge>
                      </td>
                      <td className="px-2 py-3">
                        <span className="flex items-center gap-1.5 text-xs capitalize">
                          <span className={`h-1.5 w-1.5 rounded-full ${u.status === "online" ? "bg-success" : u.status === "away" ? "bg-warning" : "bg-muted-foreground"}`} />
                          {u.status}
                        </span>
                      </td>
                      <td className="px-2 py-3 text-xs text-muted-foreground">{relativeTime(u.lastSeen)}</td>
                      <td className="px-2 py-3">
                        <button className="text-muted-foreground opacity-0 transition-opacity group-hover:opacity-100">
                          <MoreHorizontal className="h-4 w-4" />
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </Card>
        </TabsContent>

        <TabsContent value="roles">
          <Card>
            <CardHeader className="flex-row items-center gap-2 space-y-0">
              <Shield className="h-4 w-4 text-primary" />
              <CardTitle className="text-base">Permission Matrix</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="overflow-x-auto">
                <table className="w-full min-w-[640px] text-sm">
                  <thead>
                    <tr className="border-b border-border text-left text-xs text-muted-foreground">
                      <th className="py-3 pr-4 font-medium">Permission</th>
                      {(["owner", "admin", "agent", "viewer"] as Role[]).map((r) => (
                        <th key={r} className="px-3 py-3 text-center font-medium capitalize">{r}</th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {permissions.map((group) =>
                      group.items.map((item, idx) => (
                        <tr key={`${group.group}-${item}`} className="border-b border-border/60 last:border-0">
                          <td className="py-2.5 pr-4">
                            {idx === 0 && <span className="mr-2 text-xs font-semibold text-muted-foreground">{group.group}</span>}
                            <span className="text-sm">{item}</span>
                          </td>
                          {(["owner", "admin", "agent", "viewer"] as Role[]).map((r) => (
                            <td key={r} className="px-3 py-2.5 text-center">
                              {roleMatrix[r](group.group, item) ? (
                                <Check className="mx-auto h-4 w-4 text-success" />
                              ) : (
                                <span className="mx-auto block h-1 w-3 rounded-full bg-border-strong" />
                              )}
                            </td>
                          ))}
                        </tr>
                      ))
                    )}
                  </tbody>
                </table>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="invites">
          <Card>
            <CardContent className="divide-y divide-border p-0">
              {invites.map((inv) => (
                <div key={inv.email} className="flex items-center gap-3 px-4 py-3.5">
                  <span className="flex h-9 w-9 items-center justify-center rounded-full bg-secondary">
                    <Mail className="h-4 w-4 text-muted-foreground" />
                  </span>
                  <div className="flex-1">
                    <p className="text-sm font-medium">{inv.email}</p>
                    <p className="text-xs text-muted-foreground">Invited {relativeTime(inv.sentAt)}</p>
                  </div>
                  <Badge variant="secondary" className="capitalize">{inv.role}</Badge>
                  <Button size="sm" variant="ghost">Resend</Button>
                  <Button size="sm" variant="ghost" className="text-danger">Revoke</Button>
                </div>
              ))}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
