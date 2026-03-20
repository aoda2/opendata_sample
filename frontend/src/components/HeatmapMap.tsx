"use client";

import { useState } from "react";
import Map from "react-map-gl/mapbox";
import { DeckGL } from "@deck.gl/react";
import { HexagonLayer } from "@deck.gl/aggregation-layers";
import type { MapViewState } from "@deck.gl/core";
import { webgl2Adapter } from "@luma.gl/webgl";
import "mapbox-gl/dist/mapbox-gl.css";

const INITIAL_VIEW_STATE: MapViewState = {
  longitude: 139.638,
  latitude: 35.443,
  zoom: 11,
  pitch: 30,
  bearing: 0,
};

const COLOR_RANGE: [number, number, number, number][] = [
  [1, 152, 189, 200],
  [73, 227, 206, 200],
  [216, 254, 181, 200],
  [254, 237, 177, 200],
  [254, 173, 84, 200],
  [209, 55, 78, 200],
];

interface HeatmapCell {
  lat: number;
  lng: number;
  delayScore: number;
  sampleCount: number;
}

interface Props {
  cells: HeatmapCell[];
  onViewStateChange?: (bbox: { minLat: number; minLng: number; maxLat: number; maxLng: number }) => void;
}

export function HeatmapMap({ cells, onViewStateChange }: Props) {
  const mapToken = process.env.NEXT_PUBLIC_MAPBOX_TOKEN ?? "";
  const [viewState, setViewState] = useState<MapViewState>(INITIAL_VIEW_STATE);

  const layers = [
    new HexagonLayer({
      id: "delay-heatmap",
      data: cells,
      getPosition: (d: HeatmapCell) => [d.lng, d.lat],
      getColorWeight: (d: HeatmapCell) => d.delayScore,
      getElevationWeight: (d: HeatmapCell) => d.delayScore,
      elevationScale: 1,
      radius: 300,
      colorRange: COLOR_RANGE,
      pickable: true,
      extruded: true,
      coverage: 0.9,
    }),
  ];

  return (
    <DeckGL
      viewState={viewState}
      onViewStateChange={({ viewState: vs }) => {
        const mvs = vs as MapViewState;
        setViewState(mvs);

        // Approximate bbox from center + zoom
        if (onViewStateChange) {
          const span = 0.5 / Math.pow(2, (mvs.zoom ?? 11) - 10);
          onViewStateChange({
            minLat: (mvs.latitude ?? 35.443) - span,
            minLng: (mvs.longitude ?? 139.638) - span,
            maxLat: (mvs.latitude ?? 35.443) + span,
            maxLng: (mvs.longitude ?? 139.638) + span,
          });
        }
      }}
      controller={true}
      layers={layers}
      deviceProps={{ type: "webgl", adapters: [webgl2Adapter] }}
    >
      <Map
        mapboxAccessToken={mapToken}
        mapStyle="mapbox://styles/mapbox/dark-v11"
      />
    </DeckGL>
  );
}
