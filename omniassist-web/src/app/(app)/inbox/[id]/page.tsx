import { redirect } from "next/navigation";

// Conversation deep-links open the live inbox; selection happens client-side.
export default function InboxConversationPage() {
  redirect("/inbox");
}
