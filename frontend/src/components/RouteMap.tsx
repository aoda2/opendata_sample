"use client";

import { useState } from "react";
import Map from "react-map-gl/mapbox";
import { DeckGL } from "@deck.gl/react";
import { PathLayer, ScatterplotLayer } from "@deck.gl/layers";
import type { PickingInfo } from "@deck.gl/core";
import { webgl2Adapter } from "@luma.gl/webgl";
import "mapbox-gl/dist/mapbox-gl.css";

const INITIAL_VIEW_STATE = {
  longitude: 139.638,
  latitude: 35.443,
  zoom: 12,
  pitch: 0,
  bearing: 0,
};

interface LatLng {
  lat: number;
  lng: number;
}

interface Stop {
  id: string;
  name: string;
  lat: number;
  lng: number;
  sequence: number;
}

interface StopTooltipData {
  name: string;
  x: number;
  y: number;
}

interface Props {
  shape: LatLng[] | null;
  stops: Stop[];
  onStopClick?: (stop: Stop) => void;
}

export function RouteMap({ shape, stops, onStopClick }: Props) {
  const mapToken = process.env.NEXT_PUBLIC_MAPBOX_TOKEN ?? "";
  const [tooltip, setTooltip] = useState<StopTooltipData | null>(null);

  const layers = [
    new PathLayer({
      id: "route-shape",
      data: shape ? [{ path: shape.map((p) => [p.lng, p.lat] as [number, number]) }] : [],
      getPath: (d) => d.path,
      getColor: [0, 140, 255],
      getWidth: 4,
      widthMinPixels: 2,
    }),
    new ScatterplotLayer({
      id: "stops",
      data: stops,
      getPosition: (d: Stop) => [d.lng, d.lat],
      getRadius: 40,
      radiusMinPixels: 5,
      getFillColor: [255, 165, 0],
      pickable: true,
      onHover: (info: PickingInfo) => {
        if (info.object) {
          setTooltip({ name: (info.object as Stop).name, x: info.x, y: info.y });
        } else {
          setTooltip(null);
        }
      },
      onClick: (info: PickingInfo) => {
        if (info.object && onStopClick) onStopClick(info.object as Stop);
      },
    }),
  ];

  return (
    <div className="relative w-full h-full">
      <DeckGL
        initialViewState={INITIAL_VIEW_STATE}
        controller={true}
        layers={layers}
        deviceProps={{ type: "webgl", adapters: [webgl2Adapter] }}
      >
        <Map
          mapboxAccessToken={mapToken}
          mapStyle="mapbox://styles/mapbox/dark-v11"
        />
      </DeckGL>

      {tooltip && (
        <div
          className="absolute z-10 bg-gray-800 text-white text-sm px-3 py-2 rounded shadow-lg pointer-events-none"
          style={{ left: tooltip.x + 12, top: tooltip.y - 10 }}
        >
          {tooltip.name}
        </div>
      )}
    </div>
  );
}
