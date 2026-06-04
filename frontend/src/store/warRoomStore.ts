"use client";

import { create } from "zustand";
import {
  getFragilityMap,
  getHealth,
  getLatestReport,
  getReadinessSummary,
  runScenario,
} from "@/lib/api";
import type {
  CompetenceReport,
  HealthResponse,
  ManagerFragilityMap,
  ReadinessSummary,
  SimulationRun,
} from "@/lib/types";

type WarRoomState = {
  health: HealthResponse | null;
  session: SimulationRun | null;
  latestReport: CompetenceReport | null;
  fragilityMap: ManagerFragilityMap | null;
  readinessSummary: ReadinessSummary | null;
  isLoading: boolean;
  error: string | null;
  initialize: () => Promise<void>;
  runSreSimulation: () => Promise<void>;
};

export const useWarRoomStore = create<WarRoomState>((set) => ({
  health: null,
  session: null,
  latestReport: null,
  fragilityMap: null,
  readinessSummary: null,
  isLoading: false,
  error: null,
  initialize: async () => {
    set({ isLoading: true, error: null });
    try {
      const [health, latestReport, readinessSummary, fragilityMap] = await Promise.allSettled([
        getHealth(),
        getLatestReport(),
        getReadinessSummary(),
        getFragilityMap(),
      ]);

      set({
        health: health.status === "fulfilled" ? health.value : null,
        latestReport: latestReport.status === "fulfilled" ? latestReport.value : null,
        readinessSummary: readinessSummary.status === "fulfilled" ? readinessSummary.value : null,
        fragilityMap: fragilityMap.status === "fulfilled" ? fragilityMap.value : null,
        isLoading: false,
      });
    } catch (error) {
      set({ isLoading: false, error: error instanceof Error ? error.message : "Initialization failed" });
    }
  },
  runSreSimulation: async () => {
    set({ isLoading: true, error: null });
    try {
      const session = await runScenario("ROLE-SRE");
      const [fragilityMap, readinessSummary, latestReport] = await Promise.allSettled([
        getFragilityMap(),
        getReadinessSummary(),
        getLatestReport(),
      ]);

      set({
        session,
        latestReport: latestReport.status === "fulfilled" ? latestReport.value : session.final_score,
        fragilityMap: fragilityMap.status === "fulfilled" ? fragilityMap.value : null,
        readinessSummary: readinessSummary.status === "fulfilled" ? readinessSummary.value : null,
        isLoading: false,
      });
    } catch (error) {
      set({ isLoading: false, error: error instanceof Error ? error.message : "Simulation failed" });
    }
  },
}));
