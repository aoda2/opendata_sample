"use client";

interface Route {
  id: string;
  shortName: string;
  longName: string;
  avgDelaySec: number;
}

interface Props {
  routes: Route[];
  selectedId: string | null;
  onSelect: (id: string) => void;
}

function delayColor(sec: number): string {
  if (sec < 60) return "bg-green-500";
  if (sec < 120) return "bg-yellow-400";
  return "bg-red-500";
}

export function RouteList({ routes, selectedId, onSelect }: Props) {
  return (
    <ul className="space-y-1 overflow-y-auto h-full">
      {routes.map((r) => (
        <li key={r.id}>
          <button
            onClick={() => onSelect(r.id)}
            className={`w-full text-left px-3 py-2 rounded transition-colors ${
              selectedId === r.id
                ? "bg-blue-700 text-white"
                : "hover:bg-gray-800 text-gray-200"
            }`}
          >
            <div className="flex items-center gap-2">
              <span className="font-bold text-sm min-w-[2.5rem]">{r.shortName}</span>
              <span className="truncate text-xs text-gray-400 flex-1">{r.longName}</span>
              <span
                className={`ml-auto text-xs text-white px-2 py-0.5 rounded-full ${delayColor(r.avgDelaySec)}`}
              >
                {Math.round(r.avgDelaySec)}s
              </span>
            </div>
          </button>
        </li>
      ))}
    </ul>
  );
}
