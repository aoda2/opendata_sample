"use client";

import { useState } from "react";
import dynamic from "next/dynamic";
import Link from "next/link";
import { useQuery } from "@apollo/client/react";
import { RouteList } from "@/components/RouteList";
import { StopStatsPanel } from "@/components/StopStatsPanel";
import { GET_ROUTES, GET_ROUTE_DETAIL } from "@/gql/queries";

const RouteMap = dynamic(
  () => import("@/components/RouteMap").then((m) => m.RouteMap),
  { ssr: false }
);

interface Stop {
  id: string;
  name: string;
  lat: number;
  lng: number;
  sequence: number;
}

interface Route {
  id: string;
  shortName: string;
  longName: string;
  avgDelaySec: number;
}

interface RoutesData {
  routes: Route[];
}

interface RouteDetailData {
  routeShape: { points: { lat: number; lng: number }[] } | null;
  stopsByRoute: Stop[];
}

export default function RoutesPage() {
  const [selectedRouteId, setSelectedRouteId] = useState<string | null>(null);
  const [selectedStop, setSelectedStop] = useState<Stop | null>(null);

  const { data: routesData, loading: routesLoading } = useQuery<RoutesData>(GET_ROUTES);

  const { data: detailData } = useQuery<RouteDetailData>(GET_ROUTE_DETAIL, {
    variables: { routeId: selectedRouteId },
    skip: !selectedRouteId,
  });

  const routes = routesData?.routes ?? [];
  const shape = detailData?.routeShape?.points ?? null;
  const stops: Stop[] = detailData?.stopsByRoute ?? [];

  return (
    <div className="flex h-screen w-screen overflow-hidden">
      {/* Sidebar */}
      <aside className="w-72 flex-shrink-0 bg-gray-900 border-r border-gray-800 flex flex-col">
        <div className="px-4 py-3 border-b border-gray-800 flex items-center justify-between">
          <h1 className="font-bold text-white text-sm">Yokohama Transit Insight</h1>
          <Link
            href="/heatmap"
            className="text-xs text-blue-400 hover:text-blue-300"
          >
            ヒートマップ →
          </Link>
        </div>

        <div className="px-3 py-2 text-xs text-gray-400 border-b border-gray-800">
          路線一覧（遅延スコア付き）
        </div>

        <div className="flex-1 overflow-hidden px-1 py-1">
          {routesLoading ? (
            <p className="text-gray-500 text-xs p-3">読み込み中...</p>
          ) : (
            <RouteList
              routes={routes}
              selectedId={selectedRouteId}
              onSelect={(id) => {
                setSelectedRouteId(id);
                setSelectedStop(null);
              }}
            />
          )}
        </div>
      </aside>

      {/* Map */}
      <main className="flex-1 relative">
        <RouteMap
          shape={shape}
          stops={stops}
          onStopClick={(stop) => setSelectedStop(stop)}
        />

        {/* Stop stats overlay */}
        {selectedStop && (
          <div className="absolute top-4 right-4 z-20">
            <StopStatsPanel
              stopId={selectedStop.id}
              stopName={selectedStop.name}
              onClose={() => setSelectedStop(null)}
            />
          </div>
        )}

        {!selectedRouteId && (
          <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
            <p className="bg-black/60 text-gray-300 text-sm px-4 py-2 rounded">
              左の路線リストから路線を選択してください
            </p>
          </div>
        )}
      </main>
    </div>
  );
}
