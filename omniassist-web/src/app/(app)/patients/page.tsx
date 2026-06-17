"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { UserPlus, Mail, Phone, Droplet, Cake, Trash2 } from "lucide-react";
import { PageHeader } from "@/components/shared/page-header";
import { Breadcrumb } from "@/components/shared/breadcrumb";
import { IllustratedEmpty } from "@/components/shared/illustrated-empty";
import { ErrorState } from "@/components/shared/error-state";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import {
  Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter, DialogTrigger,
} from "@/components/ui/dialog";
import {
  Select, SelectContent, SelectItem, SelectTrigger, SelectValue,
} from "@/components/ui/select";
import { Field, DemoNote } from "@/components/shared/form-bits";
import { usePatients, useCreatePatient, useDeletePatient, apiConfigured, type PatientDTO } from "@/lib/api-hooks";
import { toast } from "sonner";

const BLOOD = ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"];

export default function PatientsPage() {
  const { data: patients, isError, refetch } = usePatients();
  const del = useDeletePatient();

  return (
    <div className="mx-auto max-w-[1400px] space-y-5 p-4 sm:p-6">
      <Breadcrumb items={[{ label: "Dashboard", href: "/dashboard" }, { label: "Patients" }]} />
      <PageHeader title="Patients" description="Manage your clinic's patient records.">
        <AddPatientDialog />
      </PageHeader>

      {!apiConfigured() && <DemoNote />}

      {isError ? (
        <ErrorState
          title="Couldn't load patients"
          description="We couldn't reach your patient records. Check your connection and try again."
          onRetry={() => refetch()}
        />
      ) : !patients || patients.length === 0 ? (
        <IllustratedEmpty
          src="/illustrations/patients.svg"
          title="No patients yet"
          description="Add your first patient to start booking appointments and analysing their prescriptions."
        >
          <AddPatientDialog />
        </IllustratedEmpty>
      ) : (
        <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-3">
          {patients.map((p, i) => (
            <motion.div key={p.id} initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.04 }}>
              <Card className="p-4">
                <div className="flex items-start justify-between">
                  <div className="flex items-center gap-3">
                    <span className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-ai text-sm font-semibold text-white">
                      {p.name.slice(0, 1).toUpperCase()}
                    </span>
                    <div>
                      <p className="font-medium leading-tight">{p.name}</p>
                      <p className="text-xs text-muted-foreground">
                        {[p.gender, p.blood_group].filter(Boolean).join(" · ") || "—"}
                      </p>
                    </div>
                  </div>
                  <button
                    onClick={() =>
                      del.mutate(p.id, {
                        onSuccess: () => toast.success("Patient removed"),
                        onError: (e: Error) => toast.error(e.message || "Could not remove patient"),
                      })
                    }
                    className="text-muted-foreground transition-colors hover:text-danger"
                  >
                    <Trash2 className="h-4 w-4" />
                  </button>
                </div>
                <div className="mt-3 space-y-1.5 text-xs text-muted-foreground">
                  {p.email && <p className="flex items-center gap-2"><Mail className="h-3.5 w-3.5" /> {p.email}</p>}
                  {p.phone && <p className="flex items-center gap-2"><Phone className="h-3.5 w-3.5" /> {p.phone}</p>}
                  {p.date_of_birth && <p className="flex items-center gap-2"><Cake className="h-3.5 w-3.5" /> {p.date_of_birth}</p>}
                  {p.allergies && (
                    <p className="flex items-center gap-2 text-warning"><Droplet className="h-3.5 w-3.5" /> Allergies: {p.allergies}</p>
                  )}
                </div>
              </Card>
            </motion.div>
          ))}
        </div>
      )}
    </div>
  );
}

function AddPatientDialog() {
  const [open, setOpen] = useState(false);
  const create = useCreatePatient();
  const [form, setForm] = useState<Partial<PatientDTO>>({});

  const set = (k: keyof PatientDTO, v: string) => setForm((f) => ({ ...f, [k]: v || null }));

  const submit = () => {
    if (!form.name?.trim()) return toast.error("Patient name is required");
    create.mutate(form, {
      onSuccess: () => {
        toast.success("Patient added");
        setForm({});
        setOpen(false);
      },
      onError: (e: Error) => toast.error(e.message || "Could not add patient"),
    });
  };

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button variant="gradient" className="gap-2"><UserPlus className="h-4 w-4" /> Add Patient</Button>
      </DialogTrigger>
      <DialogContent className="max-w-lg">
        <DialogHeader><DialogTitle>New Patient</DialogTitle></DialogHeader>
        <div className="grid grid-cols-2 gap-3">
          <Field label="Full name *" className="col-span-2">
            <Input value={form.name ?? ""} onChange={(e) => set("name", e.target.value)} placeholder="Ramesh Sharma" />
          </Field>
          <Field label="Email"><Input value={form.email ?? ""} onChange={(e) => set("email", e.target.value)} /></Field>
          <Field label="Phone"><Input value={form.phone ?? ""} onChange={(e) => set("phone", e.target.value)} /></Field>
          <Field label="Date of birth">
            <Input type="date" value={form.date_of_birth ?? ""} onChange={(e) => set("date_of_birth", e.target.value)} />
          </Field>
          <Field label="Gender">
            <Select value={form.gender ?? ""} onValueChange={(v) => set("gender", v)}>
              <SelectTrigger><SelectValue placeholder="Select" /></SelectTrigger>
              <SelectContent>
                {["Male", "Female", "Other"].map((g) => <SelectItem key={g} value={g}>{g}</SelectItem>)}
              </SelectContent>
            </Select>
          </Field>
          <Field label="Blood group">
            <Select value={form.blood_group ?? ""} onValueChange={(v) => set("blood_group", v)}>
              <SelectTrigger><SelectValue placeholder="Select" /></SelectTrigger>
              <SelectContent>{BLOOD.map((b) => <SelectItem key={b} value={b}>{b}</SelectItem>)}</SelectContent>
            </Select>
          </Field>
          <Field label="Allergies" className="col-span-2">
            <Input value={form.allergies ?? ""} onChange={(e) => set("allergies", e.target.value)} placeholder="e.g. Penicillin" />
          </Field>
          <Field label="Medical history" className="col-span-2">
            <Textarea rows={2} value={form.medical_history ?? ""} onChange={(e) => set("medical_history", e.target.value)} />
          </Field>
        </div>
        <DialogFooter>
          <Button variant="secondary" onClick={() => setOpen(false)}>Cancel</Button>
          <Button variant="gradient" onClick={submit} loading={create.isPending}>Save patient</Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}

