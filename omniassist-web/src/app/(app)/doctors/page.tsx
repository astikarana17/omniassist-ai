"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { Stethoscope, Mail, Phone, BadgeCheck, Trash2, Plus } from "lucide-react";
import { PageHeader } from "@/components/shared/page-header";
import { Breadcrumb } from "@/components/shared/breadcrumb";
import { IllustratedEmpty } from "@/components/shared/illustrated-empty";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import {
  Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter, DialogTrigger,
} from "@/components/ui/dialog";
import { Field, DemoNote } from "@/components/shared/form-bits";
import { ErrorState } from "@/components/shared/error-state";
import { useDoctors, useCreateDoctor, useDeleteDoctor, apiConfigured, type DoctorDTO } from "@/lib/api-hooks";
import { toast } from "sonner";

export default function DoctorsPage() {
  const { data: doctors, isError, refetch } = useDoctors();
  const del = useDeleteDoctor();

  return (
    <div className="mx-auto max-w-[1400px] space-y-5 p-4 sm:p-6">
      <Breadcrumb items={[{ label: "Dashboard", href: "/dashboard" }, { label: "Doctors" }]} />
      <PageHeader title="Doctors" description="Manage your clinic's doctors and specialists.">
        <AddDoctorDialog />
      </PageHeader>

      {!apiConfigured() && <DemoNote />}

      {isError ? (
        <ErrorState
          title="Couldn't load doctors"
          description="We couldn't reach your doctor records. Check your connection and try again."
          onRetry={() => refetch()}
        />
      ) : !doctors || doctors.length === 0 ? (
        <IllustratedEmpty
          src="/illustrations/doctors.svg"
          title="No doctors yet"
          description="Add the doctors and specialists in your clinic so you can assign them to appointments."
        >
          <AddDoctorDialog />
        </IllustratedEmpty>
      ) : (
        <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-3">
          {doctors.map((d, i) => (
            <motion.div key={d.id} initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.04 }}>
              <Card className="p-4">
                <div className="flex items-start justify-between">
                  <div className="flex items-center gap-3">
                    <span className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-ai">
                      <Stethoscope className="h-5 w-5 text-white" />
                    </span>
                    <div>
                      <p className="font-medium leading-tight">Dr. {d.name}</p>
                      <p className="text-xs text-ai">{d.specialty || "General"}</p>
                    </div>
                  </div>
                  <button
                    onClick={() =>
                      del.mutate(d.id, {
                        onSuccess: () => toast.success("Doctor removed"),
                        onError: (e: Error) => toast.error(e.message || "Could not remove doctor"),
                      })
                    }
                    className="text-muted-foreground transition-colors hover:text-danger"
                  >
                    <Trash2 className="h-4 w-4" />
                  </button>
                </div>
                <div className="mt-3 space-y-1.5 text-xs text-muted-foreground">
                  {d.department && <p>{d.department}</p>}
                  {d.email && <p className="flex items-center gap-2"><Mail className="h-3.5 w-3.5" /> {d.email}</p>}
                  {d.phone && <p className="flex items-center gap-2"><Phone className="h-3.5 w-3.5" /> {d.phone}</p>}
                  {d.license_no && <p className="flex items-center gap-2"><BadgeCheck className="h-3.5 w-3.5" /> {d.license_no}</p>}
                </div>
              </Card>
            </motion.div>
          ))}
        </div>
      )}
    </div>
  );
}

function AddDoctorDialog() {
  const [open, setOpen] = useState(false);
  const create = useCreateDoctor();
  const [form, setForm] = useState<Partial<DoctorDTO>>({});
  const set = (k: keyof DoctorDTO, v: string) => setForm((f) => ({ ...f, [k]: v || null }));

  const submit = () => {
    if (!form.name?.trim()) return toast.error("Doctor name is required");
    create.mutate(form, {
      onSuccess: () => {
        toast.success("Doctor added");
        setForm({});
        setOpen(false);
      },
      onError: (e: Error) => toast.error(e.message || "Could not add doctor"),
    });
  };

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button variant="gradient" className="gap-2"><Plus className="h-4 w-4" /> Add Doctor</Button>
      </DialogTrigger>
      <DialogContent className="max-w-lg">
        <DialogHeader><DialogTitle>New Doctor</DialogTitle></DialogHeader>
        <div className="grid grid-cols-2 gap-3">
          <Field label="Full name *" className="col-span-2">
            <Input value={form.name ?? ""} onChange={(e) => set("name", e.target.value)} placeholder="Anjali Verma" />
          </Field>
          <Field label="Specialty"><Input value={form.specialty ?? ""} onChange={(e) => set("specialty", e.target.value)} placeholder="Cardiologist" /></Field>
          <Field label="Department"><Input value={form.department ?? ""} onChange={(e) => set("department", e.target.value)} placeholder="Cardiology" /></Field>
          <Field label="Email"><Input value={form.email ?? ""} onChange={(e) => set("email", e.target.value)} /></Field>
          <Field label="Phone"><Input value={form.phone ?? ""} onChange={(e) => set("phone", e.target.value)} /></Field>
          <Field label="License no." className="col-span-2">
            <Input value={form.license_no ?? ""} onChange={(e) => set("license_no", e.target.value)} />
          </Field>
        </div>
        <DialogFooter>
          <Button variant="secondary" onClick={() => setOpen(false)}>Cancel</Button>
          <Button variant="gradient" onClick={submit} loading={create.isPending}>Save doctor</Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
