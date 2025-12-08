import { ChatInterface } from "@/components/chat/ChatInterface";
import { DashboardLayout } from "@/components/layout/DashboardLayout";
import { StatsRow } from "@/components/dashboard/StatsRow";

export default function Home() {
  return (
    <DashboardLayout>
      <StatsRow />
      <div className="flex-1 overflow-hidden">
        <ChatInterface />
      </div>
    </DashboardLayout>
  );
}
