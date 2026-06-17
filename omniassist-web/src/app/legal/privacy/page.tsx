export const metadata = { title: "Privacy Policy — OmniAssist Health" };

export default function PrivacyPage() {
  return (
    <>
      <h1>Privacy Policy</h1>
      <p><strong>Last updated:</strong> June 2026</p>

      <p>
        OmniAssist Health (&quot;we&quot;, &quot;us&quot;) provides an AI-powered platform that helps
        people understand prescriptions, lab reports and general health questions. This policy
        explains what data we collect, how we use it, and your rights.
      </p>

      <h2>1. Data we collect</h2>
      <p>
        <strong>Account data</strong> — name, email, and clinic/organization details you provide at
        signup. <strong>Health content</strong> — prescription and lab-report images, extracted
        values, patient records and assistant conversations you create. <strong>Usage data</strong>{" "}
        — logs, device and IP information used to operate and secure the service.
      </p>

      <h2>2. How we use data</h2>
      <p>
        To deliver the service — read and explain prescriptions and reports, answer general health
        questions, and secure the platform. We do not sell your data, and we do not use your health
        content to train third-party foundation models. OmniAssist Health provides AI-generated
        information only and is not a substitute for professional medical advice or diagnosis.
      </p>

      <h2>3. Sub-processors</h2>
      <p>
        We rely on trusted infrastructure providers (cloud hosting, database, vector search, and
        LLM inference) bound by data-processing agreements. A current list is available on request.
      </p>

      <h2>4. Security</h2>
      <p>
        Data is encrypted in transit (TLS) and at rest, with role-based access control and
        per-organization isolation. We align to SOC 2 / ISO 27001 practices.
      </p>

      <h2>5. Data retention &amp; your rights</h2>
      <p>
        You control retention of your workspace content and can export or delete it. Subject to
        applicable law (including GDPR/CCPA), you may request access, correction, or deletion of
        your personal data.
      </p>

      <h2>6. Contact</h2>
      <p>
        Questions about privacy? Email <strong>privacy@omniassist.ai</strong>.
      </p>

      <p className="mt-8 text-xs">
        This document is a template for demonstration. Have it reviewed by legal counsel before
        production use.
      </p>
    </>
  );
}
