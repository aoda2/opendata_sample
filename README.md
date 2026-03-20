# Yokohama Transit Insight

横浜市営バスの GTFS データを使った **遅延・到着予測ビューア** のサンプル実装です。

停留所・経路の地図可視化と、時間帯別の遅延ヒートマップを deck.gl で表現します。

---

## スクリーンショット

| 画面1: 路線マップ | 画面2: 遅延ヒートマップ |
|---|---|
| 路線リスト + Mapbox + PathLayer / ScatterplotLayer | 時刻スライダー + HexagonLayer |

---

## アーキテクチャ

```
frontend (Next.js)
    │  GraphQL (Apollo Client)
    ▼
backend/gateway (FastAPI + strawberry-graphql)  :8080
    │  gRPC
    ▼
backend/service (grpcio TransitService)         :50051
    │  sqlite3
    ▼
data/transit.db  ←  GTFS CSV (stops / routes / trips / shapes / stop_times)
```

### 技術スタック

| 層 | 技術 |
|---|---|
| フロントエンド | Next.js 15, TypeScript, Tailwind CSS |
| 地図 | Mapbox GL JS, react-map-gl, deck.gl |
| GraphQL クライアント | Apollo Client v4 |
| GraphQL サーバー | strawberry-graphql + FastAPI |
| gRPC | grpcio / grpcio-tools (Python) |
| データベース | SQLite (aiosqlite) |
| データ | GTFS-JP（横浜市営バス） |

---

## ディレクトリ構成

```
opendata_sample/
├── Makefile
├── .gitignore
├── backend/
│   ├── pyproject.toml
│   ├── proto/transit/v1/transit.proto      ← gRPC サービス定義
│   ├── gen/transit/v1/                      ← protoc 生成コード（自動生成）
│   ├── scripts/gen_proto.sh                 ← proto 再生成スクリプト
│   ├── internal/
│   │   ├── db/
│   │   │   ├── schema.sql                   ← テーブル定義
│   │   │   └── queries.py                   ← SQLite クエリヘルパー
│   │   ├── gtfs/
│   │   │   ├── parser.py                    ← GTFS CSV パーサー
│   │   │   └── importer.py                  ← DB インポートロジック
│   │   ├── transit/
│   │   │   └── service.py                   ← gRPC TransitService 実装
│   │   └── gateway/
│   │       ├── schema.py                    ← strawberry GraphQL スキーマ
│   │       └── app.py                       ← FastAPI アプリ
│   └── cmd/
│       ├── importer.py                      ← GTFS インポート CLI
│       └── server.py                        ← サーバー起動エントリーポイント
└── frontend/
    ├── src/
    │   ├── app/
    │   │   ├── routes/page.tsx              ← 画面1: 路線マップ
    │   │   └── heatmap/page.tsx             ← 画面2: 遅延ヒートマップ
    │   ├── components/
    │   │   ├── RouteMap.tsx                 ← PathLayer + ScatterplotLayer
    │   │   ├── HeatmapMap.tsx               ← HexagonLayer
    │   │   ├── RouteList.tsx                ← 路線一覧サイドバー
    │   │   ├── TimeSlider.tsx               ← 時刻スライダー
    │   │   └── StopStatsPanel.tsx           ← 停留所統計パネル
    │   ├── gql/queries.ts                   ← GraphQL クエリ定義
    │   └── lib/apollo.ts                    ← Apollo Client 設定
    └── codegen.ts                           ← graphql-codegen 設定
```

---

## セットアップ

### 前提条件

- Python 3.11+
- Node.js 20+
- [Mapbox アクセストークン](https://account.mapbox.com/)
- [公共交通オープンデータセンター](https://www.odpt.org/) 開発者アカウント（GTFS データ取得に必要）

### 1. GTFS データの取得

[ODPT データカタログ](https://ckan.odpt.org/dataset/yokohama_municipal_bus) から横浜市営バス GTFS-JP をダウンロードし、以下のファイルを `backend/data/gtfs/` に配置します。

```
backend/data/gtfs/
├── routes.txt
├── stops.txt
├── trips.txt
├── stop_times.txt
└── shapes.txt
```

### 2. バックエンドのセットアップ

```bash
# 仮想環境の作成と依存関係のインストール
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -e .

# GTFS データを SQLite にインポート
python -m cmd.importer --data data/gtfs --db data/transit.db

# gRPC + GraphQL サーバーの起動（ポート 50051 / 8080）
python -m cmd.server
```

GraphiQL プレイグラウンドは http://localhost:8080/graphql で利用できます。

### 3. フロントエンドのセットアップ

```bash
cd frontend
npm install

# Mapbox トークンを設定
echo 'NEXT_PUBLIC_MAPBOX_TOKEN=your_token_here' > .env.local
echo 'NEXT_PUBLIC_GRAPHQL_ENDPOINT=http://localhost:8080/graphql' >> .env.local

npm run dev
```

ブラウザで http://localhost:3000 を開きます。

---

## 起動・停止

### 起動

```bash
# バックエンド（gRPC :50051 + GraphQL :8080）
cd backend
source .venv/bin/activate
PYTHONPATH=. python -m cmd.server --db data/transit.db

# フロントエンド（:3000）— 別ターミナルで
cd frontend
npm run dev
```

### 停止

```bash
# ポートを指定して強制終了
lsof -ti :8080 -ti :50051 -ti :3000 | xargs kill -9
```

---

## Makefile コマンド一覧

```bash
make install          # バックエンド + フロントエンドの依存関係を一括インストール
make import           # GTFS CSV を SQLite にインポート
make serve            # バックエンドサーバーを起動
make dev              # フロントエンド開発サーバーを起動
make proto            # proto ファイルから Python コードを再生成
make codegen          # GraphQL スキーマから TypeScript 型を生成
```

---

## GraphQL API

バックエンドは以下のクエリをサポートします。

```graphql
type Query {
  routes: [Route!]!
  route(id: ID!): Route
  routeShape(routeId: ID!): RouteShape
  stopsByRoute(routeId: ID!): [Stop!]!
  stopStats(stopId: ID!, from_: String!, to: String!): StopStats
  delayHeatmap(from_: String!, to: String!, bbox: BBoxInput!): [HeatmapCell!]!
}
```

---

## 今後の拡張予定

- [ ] Firebase Authentication によるログイン機能
- [ ] Firestore によるお気に入り路線の保存
- [ ] GTFS Realtime 対応（リアルタイム位置情報）
- [ ] Vercel + Cloud Run へのデプロイ
- [ ] 路線別遅延ランキングチャート

---

## データについて

本プロジェクトは [公共交通オープンデータセンター (ODPT)](https://www.odpt.org/) が提供する横浜市営バスの GTFS データを使用します。データの利用には開発者登録が必要です。

遅延スコアは実際の運行実績ではなく、デモ用のシミュレーション値（時間帯ルール + 擬似乱数）です。
