import { Hero } from "@/components/Hero";
import { Workbench } from "@/components/Workbench";
import { Footer } from "@/components/Footer";
import { MethodologySection } from "@/components/MethodologySection";

export default function Page() {
  return (
    <main className="relative mx-auto max-w-7xl px-6 pb-32 pt-8 sm:px-10">
      <Hero />
      <Workbench />
      <MethodologySection />
      <Footer />
    </main>
  );
}
