"use client";

import { useEffect } from "react";
import { AppShell } from "@/components/AppShell";
import { useWarRoomStore } from "@/store/warRoomStore";

export function WarRoom() {
  const initialize = useWarRoomStore((state) => state.initialize);

  useEffect(() => {
    void initialize();
  }, [initialize]);

  return <AppShell />;
}
