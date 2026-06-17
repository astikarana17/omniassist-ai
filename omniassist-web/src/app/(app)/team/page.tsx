"use client";

import { useState } from "react";
import { UserPlus, MoreHorizontal, Mail, Users } from "lucide-react";
import { PageHeader } from "@/components/shared/page-header";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
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
import type { Role } from "@/types";
import { relativeTime } from "@/lib/utils";
import { useMembers, useInviteMember, apiConfigured } from "@/lib/api-hooks";

const roleVariant: Record<Role, React.ComponentProps<typeof Badge>["variant"]> = {
  owner: "default",
  admin: "ai",
  agent: "info",
  viewer: "secondary",
};

export default function TeamPage() {
  const [open, setOpen] = useState(false);
  const { data, isLoading } = useMembers();
  const users = data ?? [];
  const invite = useInviteMember();
  const [inviteEmail, setInviteEmail] = useState("");
  const [inviteRole, setInviteRole] = useState("admin");

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
          toast.success(`${email} invited to your clinic`);
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
      <PageHeader title="Staff" description="Manage who can access your clinic workspace.">
        <Dialog open={open} onOpenChange={setOpen}>
          <DialogTrigger asChild>
            <Button variant="gradient"><UserPlus className="h-4 w-4" /> Invite staff</Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Invite a staff member</DialogTitle>
              <DialogDescription>They&apos;ll receive an email to join your clinic workspace.</DialogDescription>
            </DialogHeader>
            <div className="space-y-4 py-2">
              <div className="space-y-2">
                <Label htmlFor="invite-email">Email address</Label>
                <Input
                  id="invite-email"
                  type="email"
                  placeholder="colleague@clinic.com"
                  value={inviteEmail}
                  onChange={(e) => setInviteEmail(e.target.value)}
                  onKeyDown={(e) => e.key === "Enter" && sendInvite()}
                />
              </div>
              <div className="space-y-2">
                <Label>Access level</Label>
                <Select value={inviteRole} onValueChange={setInviteRole}>
                  <SelectTrigger><SelectValue /></SelectTrigger>
                  <SelectContent>
                    <SelectItem value="admin">Admin — full access</SelectItem>
                    <SelectItem value="viewer">Viewer — read only</SelectItem>
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

      <Card>
        {users.length === 0 ? (
          <div className="flex flex-col items-center justify-center gap-3 px-6 py-16 text-center">
            <span className="flex h-12 w-12 items-center justify-center rounded-full bg-secondary">
              <Users className="h-6 w-6 text-muted-foreground" />
            </span>
            <div>
              <p className="font-medium">{isLoading ? "Loading staff…" : "No staff yet"}</p>
              <p className="mt-1 text-sm text-muted-foreground">
                Invite doctors, receptionists or admins to collaborate in your clinic workspace.
              </p>
            </div>
            {!isLoading && (
              <Button variant="secondary" onClick={() => setOpen(true)}>
                <UserPlus className="h-4 w-4" /> Invite your first staff member
              </Button>
            )}
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full min-w-[720px] text-sm">
              <thead>
                <tr className="border-b border-border text-left text-xs text-muted-foreground">
                  <th className="px-4 py-3 font-medium">Member</th>
                  <th className="px-2 py-3 font-medium">Access</th>
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
        )}
      </Card>
    </div>
  );
}
