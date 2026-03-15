"use client";

import { useState } from "react";
import dynamic from "next/dynamic";
import Link from "next/link";
import { useQuery } from "@apollo/client/react";
import { TimeSlider } from "@/components/TimeSlider";
import { GET_DELAY_HEATMAP } from "@/gql/queries";

const HeatmapMap = dynamic(
  () => import("@/components/HeatmapMap").then((m) => m.HeatmapMap),
  { ssr: false }
);

const DEFAULT_BBOX = {
  minLat: 35.35,
  minLng: 139.55,
  maxLat: 35.55,
  maxLng: 139.75,
};

function minutesToISO(minutes: number): string {
  const h = Math.floor(minutes / 60) % 24;
  const m = minutes % 60;
  const today = new Date().toISOString().slice(0, 10);
  return `${today}T${String(h).padStart(2, "0")}:${String(m).padStart(2, "0")}:00Z`;
}

interface HeatmapCell {
  lat: number;
  lng: number;
  delayScore: number;
  sampleCount: number;
}

interface HeatmapData {
  delayHeatmap: HeatmapCell[];
}

export default function HeatmapPage() {
  const [timeMinutes, setTimeMinutes] = useState(480); // 08:00 default
  const [bbox, setBbox] = useState(DEFAULT_BBOX);

  const from = minutesToISO(timeMinutes);
  const to = minutesToISO(timeMinutes + 30);

  const { data, loading } = useQuery<HeatmapData>(GET_DELAY_HEATMAP, {
    variables: { from, to, bbox },
  });

  const cells = data?.delayHeatmap ?? [];

  return (
    <div className="flex flex-col h-screen w-screen">
      {/* Header bar */}
      <header className="flex items-center gap-4 bg-gray-900 border-b border-gray-800 px-4 py-2 z-10">
        <Link href="/routes" className="text-xs text-blue-400 hover:text-blue-300">
          ← 路線マップ
        </Link>
        <h1 className="font-bold text-white text-sm flex-1">
          時間帯別遅延ヒートマップ
        </h1>
        {loading && (
          <span className="text-xs text-gray-400 animate-pulse">更新中...</span>
        )}
        <span className="text-xs text-gray-400">
          データ数: {cells.length}セル
        </span>
      </header>

      {/* Time slider */}
      <div className="px-4 py-2 bg-gray-900 border-b border-gray-800">
        <TimeSlider value={timeMinutes} onChange={setTimeMinutes} />
      </div>

      {/* Map */}
      <main className="flex-1 relative">
        <HeatmapMap cells={cells} onViewStateChange={setBbox} />

        {/* Legend */}
        <div className="absolute bottom-6 left-4 bg-gray-900/80 rounded p-3 text-xs">
          <p className="text-gray-300 mb-2 font-medium">遅延スコア</p>
          <div className="flex gap-1 items-center">
            <div className="w-16 h-3 rounded" style={{
              background: "linear-gradient(to right, #0198BD, #49E3CE, #D8FEB5, #FEEDD1, #FEAD54, #D1374E)"
            }} />
          </div>
          <div className="flex justify-between text-gray-400 mt-1">
            <span>低</span>
            <span>高</span>
          </div>
        </div>
      </main>
    </div>
  );
}
