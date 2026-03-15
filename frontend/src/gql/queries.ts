import { gql } from "@apollo/client";

export const GET_ROUTES = gql`
  query GetRoutes {
    routes {
      id
      shortName
      longName
      avgDelaySec
    }
  }
`;

export const GET_ROUTE_DETAIL = gql`
  query GetRouteDetail($routeId: ID!) {
    routeShape(routeId: $routeId) {
      points {
        lat
        lng
      }
    }
    stopsByRoute(routeId: $routeId) {
      id
      name
      lat
      lng
      sequence
    }
  }
`;

export const GET_STOP_STATS = gql`
  query GetStopStats($stopId: ID!, $from: String!, $to: String!) {
    stopStats(stopId: $stopId, from_: $from, to: $to) {
      stopId
      stopName
      avgDelaySec
      delayRate
      tripCount
      nextDeparture
    }
  }
`;

export const GET_DELAY_HEATMAP = gql`
  query GetDelayHeatmap($from: String!, $to: String!, $bbox: BBoxInput!) {
    delayHeatmap(from_: $from, to: $to, bbox: $bbox) {
      lat
      lng
      delayScore
      sampleCount
    }
  }
`;
