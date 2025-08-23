# make fresh   # clean slate + rebuild + run
# # or
# make dev     # just rebuild + run
# make logs    # tail everything


.PHONY: fresh clear-screen dev up down logs ui-logs api-logs build-ui-prod build-api-prod nuke verify-imports verify-ui-mods fix-imports list-ui-imports ui-build ui-type ui-lint ui-dev

clear-screen:
	@{ tput reset || tput clear || clear || printf '\033[3J\033[H\033[2J'; } 2>/dev/null

# ADHD: one-button fresh start (safe)
fresh: | clear-screen
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

fresh-nonstrict: clear-screen
	@echo "🚀 Up with rebuild (non-strict)…"
	- docker compose --env-file .env up --build

# Dev up (rebuild if Dockerfiles changed)
dev: | clear-screen
	docker compose --env-file .env up --build

up: | clear-screen
	docker compose --env-file .env up

down: | clear-screen
	docker compose down -v --remove-orphans

logs: | clear-screen
	docker compose logs -f --tail=100

ui-logs: | clear-screen
	docker compose logs -f --tail=100 frontend

api-logs: | clear-screen
	docker compose logs -f --tail=100 backend

# CI-style local production builds (no run)
build-ui-prod: | clear-screen
	docker build -f apps/ui/Dockerfile -t ui-prod apps/ui

build-api-prod: | clear-screen
	docker build -f apps/backend/Dockerfile -t api-prod apps/backend

# Nuclear option (use rarely)
nuke: | clear-screen
	- docker compose down -v --remove-orphans
	- docker system prune -af --volumes
	docker compose --env-file .env up --build

verify-imports: | clear-screen
	@echo "🔎 Checking for bad '@/src/' imports…"
	@! rg -n "@/src/" apps/ui/src || (echo "❌ Found bad '@/src/' imports. Run: rg -l \"@/src/\" apps/ui/src | xargs -r sed -i 's#@/src/#@/#g'"; exit 1)
	@echo "✅ No '@/src/' issues."

# Lists every "@/components/ui/<mod>" import so you see what's required
list-ui-imports: | clear-screen
	@rg -no "from ['\"]@/components/ui/([^'\"\)]+)['\"]" apps/ui/src | sort -u || true

# Fails if an "@/components/ui/<mod>" import doesn't have a matching file under src/components/ui
verify-ui-mods: | clear-screen
	@echo "🔎 verifying ui/* imports exist..."
	@missing=0; \
	for m in $$(rg -no "from ['\"]@/components/ui/([^'\"\)]+)['\"]" apps/ui/src | sed -E 's#.*ui/([^'\''"]+).*#\1#' | sort -u); do \
		test -f "apps/ui/src/components/ui/$${m}.tsx" || test -f "apps/ui/src/components/ui/$${m}.ts" || { \
			echo "❌ Missing: apps/ui/src/components/ui/$${m}.tsx"; missing=1; }; \
	done; \
	exit $$missing

# (handy) Fixes stray '@/src/' imports -> '@/'
fix-imports: | clear-screen
	@rg -l "@/src/" apps/ui/src | xargs -r sed -i 's#@/src/#@/#g' || true

ui-type: | clear-screen
	cd apps/ui && npm run typecheck

ui-lint: | clear-screen
	cd apps/ui && npm run lint

ui-build: | clear-screen
	cd apps/ui && rm -rf node_modules .next && npm ci && npm run typecheck && npm run build


ui-dev: | clear-screen
	cd apps/ui && npm run dev

# Put a short description after each target like: target: ## your description
.DEFAULT_GOAL := help

help: ## Show all commands
	@printf "\n\033[1mAvailable make commands\033[0m\n\n"
	@awk 'BEGIN {FS = ":.*##"} /^[a-zA-Z0-9_.-]+:.*##/ {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)
	@printf "\n"

fresh: ## Clean slate: down -v, rebuild, up
dev: ## Rebuild + up (dev)
up: ## docker compose up -d
down: ## docker compose down
logs: ## Tail all logs
ui-logs: ## Tail UI logs
api-logs: ## Tail API logs
build-ui-prod: ## Build UI for production
build-api-prod: ## Build API for production
nuke: ## Remove containers, volumes, (careful)
verify-imports: ## Check TS import paths
list-ui-imports: ## List UI imports referencing aliases
verify-ui-mods: ## Verify UI modified modules
fix-imports: ## Auto-fix TS import aliases
ui-type: ## Type-check UI (tsc)
ui-lint: ## Lint UI (eslint)
ui-build: ## Clean & build UI (Next)
ui-dev: ## Run UI dev server
