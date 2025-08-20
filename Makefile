# make fresh   # clean slate + rebuild + run
# # or
# make dev     # just rebuild + run
# make logs    # tail everything


.PHONY: fresh dev up down logs ui-logs api-logs build-ui-prod build-api-prod nuke verify-imports verify-ui-mods fix-imports list-ui-imports ui-build ui-type ui-lint ui-dev


# ADHD: one-button fresh start (safe)
fresh:
	@echo "▶️  Stopping & removing stack (containers + volumes)…"
	- docker compose down -v --remove-orphans
	@echo "🧹 Clearing local caches…"
	- rm -rf apps/ui/.next apps/ui/.turbo apps/ui/.vercel apps/ui/.cache
	- find . -type d -name "__pycache__" -prune -exec rm -rf {} +
	- find . -type d -name ".pytest_cache" -prune -exec rm -rf {} +
	@echo "🧽 Pruning builder cache…"
	- docker buildx prune -f || docker builder prune -f
	@echo "🚀 Up with rebuild…"
	docker compose --env-file .env up --build

# Dev up (rebuild if Dockerfiles changed)
dev:
	docker compose --env-file .env up --build

up:
	docker compose --env-file .env up

down:
	docker compose down -v --remove-orphans

logs:
	docker compose logs -f --tail=100

ui-logs:
	docker compose logs -f --tail=100 frontend

api-logs:
	docker compose logs -f --tail=100 backend

# CI-style local production builds (no run)
build-ui-prod:
	docker build -f apps/ui/Dockerfile -t ui-prod apps/ui

build-api-prod:
	docker build -f apps/backend/Dockerfile -t api-prod apps/backend

# Nuclear option (use rarely)
nuke:
	- docker compose down -v --remove-orphans
	- docker system prune -af --volumes
	docker compose --env-file .env up --build

verify-imports:
	@echo "🔎 Checking for bad '@/src/' imports…"
	@! rg -n "@/src/" apps/ui/src || (echo "❌ Found bad '@/src/' imports. Run: rg -l \"@/src/\" apps/ui/src | xargs -r sed -i 's#@/src/#@/#g'"; exit 1)
	@echo "✅ No '@/src/' issues."

# Lists every "@/components/ui/<mod>" import so you see what's required
list-ui-imports:
	@rg -no "from ['\"]@/components/ui/([^'\"\)]+)['\"]" apps/ui/src | sort -u || true

# Fails if an "@/components/ui/<mod>" import doesn't have a matching file under src/components/ui
verify-ui-mods:
	@echo "🔎 verifying ui/* imports exist..."
	@missing=0; \
	for m in $$(rg -no "from ['\"]@/components/ui/([^'\"\)]+)['\"]" apps/ui/src | sed -E 's#.*ui/([^'\''"]+).*#\1#' | sort -u); do \
	  test -f "apps/ui/src/components/ui/$${m}.tsx" || test -f "apps/ui/src/components/ui/$${m}.ts" || { \
	    echo "❌ Missing: apps/ui/src/components/ui/$${m}.tsx"; missing=1; }; \
	done; \
	exit $$missing

# (handy) Fixes stray '@/src/' imports -> '@/'
fix-imports:
	@rg -l "@/src/" apps/ui/src | xargs -r sed -i 's#@/src/#@/#g' || true

ui-type:
	clear && cd apps/ui && npm run typecheck

ui-lint:
	clear && cd apps/ui && npm run lint

ui-build:
	clear && cd apps/ui && rm -rf node_modules .next && npm ci && npm run typecheck && npm run build


ui-dev:
	clear && cd apps/ui && npm run dev
