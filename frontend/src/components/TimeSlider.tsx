"use client";

interface Props {
  value: number;           // minutes since midnight (0 = 00:00, 1439 = 23:59)
  onChange: (minutes: number) => void;
}

function formatMinutes(minutes: number): string {
  const h = Math.floor(minutes / 60) % 24;
  const m = minutes % 60;
  return `${String(h).padStart(2, "0")}:${String(m).padStart(2, "0")}`;
}

export function TimeSlider({ value, onChange }: Props) {
  // Range: 5:00 (300) to 24:00 (1440), step 30 min
  const MIN = 300;
  const MAX = 1440;
  const STEP = 30;

  return (
    <div className="flex items-center gap-3 bg-gray-900 border border-gray-700 rounded-lg px-4 py-3">
      <span className="text-xs text-gray-400 w-12">時間帯</span>
      <input
        type="range"
        min={MIN}
        max={MAX}
        step={STEP}
        value={value}
        onChange={(e) => onChange(Number(e.target.value))}
        className="flex-1 accent-blue-500"
      />
      <span className="text-white font-mono text-sm w-12 text-right">
        {formatMinutes(value)}
      </span>
    </div>
  );
}
