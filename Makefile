.PHONY: proto install import serve dev codegen

# ── Backend ──────────────────────────────────────────────────────────────────

# Re-generate Python gRPC code from proto
proto:
	cd backend && bash scripts/gen_proto.sh

# Install Python dependencies into a virtualenv
install-backend:
	cd backend && python3 -m venv .venv && .venv/bin/pip install -e ".[dev]"

# Import GTFS CSV files into SQLite  (requires GTFS files in backend/data/gtfs/)
import:
	cd backend && .venv/bin/python -m cmd.importer --data data/gtfs --db data/transit.db

# Start gRPC + GraphQL gateway (port 50051 / 8080)
serve:
	cd backend && .venv/bin/python -m cmd.server --db data/transit.db

# ── Frontend ─────────────────────────────────────────────────────────────────

# Install npm dependencies
install-frontend:
	cd frontend && npm install

# Run Next.js dev server (port 3000)
dev:
	cd frontend && npm run dev

# Generate typed GraphQL hooks from running backend
codegen:
	cd frontend && npx graphql-codegen

# ── All ───────────────────────────────────────────────────────────────────────

install: install-backend install-frontend
