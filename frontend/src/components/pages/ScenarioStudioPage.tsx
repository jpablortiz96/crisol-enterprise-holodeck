"use client";

import { ScenarioLibrary } from "@/components/ScenarioLibrary";
import { ScenarioEditor } from "@/components/ScenarioEditor";

export function ScenarioStudioPage() {
  return (
    <section className="product-page">
      <header className="page-header">
        <p>Scenario authoring</p>
        <h2>Create scenario-driven evaluations</h2>
        <span>Define the business context, dynamic personas, operational turns, and decision options in a guided workflow.</span>
      </header>
      <ScenarioLibrary />
      <ScenarioEditor />
    </section>
  );
}
