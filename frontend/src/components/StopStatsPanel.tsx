"use client";

import { useQuery } from "@apollo/client/react";
import { GET_STOP_STATS } from "@/gql/queries";

interface Props {
  stopId: string;
  stopName: string;
  onClose: () => void;
}

interface StopStatsData {
  stopStats: {
    stopId: string;
    stopName: string;
    avgDelaySec: number;
    delayRate: number;
    tripCount: number;
    nextDeparture: string | null;
  };
}

export function StopStatsPanel({ stopId, stopName, onClose }: Props) {
  const now = new Date();
  const from = now.toISOString();
  const to = new Date(now.getTime() + 3600_000).toISOString();

  const { data, loading } = useQuery<StopStatsData>(GET_STOP_STATS, {
    variables: { stopId, from, to },
  });

  const stats = data?.stopStats;

  return (
    <div className="bg-gray-900 border border-gray-700 rounded-lg p-4 w-72">
      <div className="flex justify-between items-start mb-3">
        <h3 className="font-semibold text-white text-sm">{stopName}</h3>
        <button onClick={onClose} className="text-gray-400 hover:text-white ml-2">✕</button>
      </div>

      {loading && <p className="text-gray-400 text-xs">読み込み中...</p>}

      {stats && (
        <dl className="grid grid-cols-2 gap-y-2 text-xs">
          <dt className="text-gray-400">平均遅延</dt>
          <dd className="text-white font-mono">{Math.round(stats.avgDelaySec)}秒</dd>

          <dt className="text-gray-400">遅延率</dt>
          <dd className="text-white font-mono">{Math.round(stats.delayRate * 100)}%</dd>

          <dt className="text-gray-400">便数</dt>
          <dd className="text-white font-mono">{stats.tripCount}便</dd>

          {stats.nextDeparture && (
            <>
              <dt className="text-gray-400">次の出発</dt>
              <dd className="text-white font-mono">{stats.nextDeparture}</dd>
            </>
          )}
        </dl>
      )}
    </div>
  );
}
