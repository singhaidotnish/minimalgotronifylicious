# ==== Core ====
DC := docker compose
BACK_SERVICE := backend
FRONT_DIR := apps/ui
BACK_DIR := apps/backend

.PHONY: help fresh dev up down rebuild logs be-logs ui-logs exec health \
        paper live ui-dev ui-build ui-type ui-lint fix-imports

help:
	@echo ""
	@echo "Targets:"
	@echo "  fresh      - down + prune + build --no-cache + up"
	@echo "  dev        - build (with cache) + up"
	@echo "  up/down    - start/stop stack"
	@echo "  rebuild    - rebuild images (no cache)"
	@echo "  logs       - tail all services"
	@echo "  be-logs    - tail backend logs"
	@echo "  exec       - run a command in a service (S=<service> C='<cmd>')"
	@echo "  health     - curl backend /api/health"
	@echo "  paper      - up using .env.paper"
	@echo "  live       - up using .env.live"
	@echo "  ui-*       - frontend helpers (dev/build/type/lint)"
	@echo "  fix-imports- fix '@/src/' -> '@/' in UI src"
	@echo ""

# ==== Orchestrations ====
fresh:
	- $(DC) down -v --remove-orphans
	- docker builder prune -f
	$(DC) build --no-cache
	$(DC) up --force-recreate

dev:
	$(DC) build
	$(DC) up

up:
	$(DC) up

down:
	$(DC) down -v

rebuild:
	$(DC) build --no-cache

logs:
	$(DC) logs -f

be-logs:
	$(DC) logs -f $(BACK_SERVICE)

ui-logs:
	$(DC) logs -f ui

# run an arbitrary command in a service:
#   make exec S=backend C='bash'
exec:
	@if [ -z "$(S)" ] || [ -z "$(C)" ]; then \
		echo "Usage: make exec S=<service> C='<command>'"; exit 2; fi
	$(DC) exec $(S) sh -lc "$(C)"

health:
	@curl -fsS "http://localhost:$${BACKEND_HOST_PORT:-5000}/api/health" && echo "  ✅" || (echo "  ❌" && exit 1)

# ==== Profiles ====
paper:
	$(DC) --env-file $(BACK_DIR)/.env.paper up --build

live:
	$(DC) --env-file $(BACK_DIR)/.env.live up --build

# ==== Frontend ====
ui-dev:
	cd $(FRONT_DIR) && npm run dev

ui-build:
	cd $(FRONT_DIR) && rm -rf node_modules .next && npm ci && npm run typecheck && npm run build

ui-type:
	cd $(FRONT_DIR) && npm run typecheck

ui-lint:
	cd $(FRONT_DIR) && npm run lint

# Fix stray '@/src/' imports -> '@/' (optional)
fix-imports:
	@rg -l "@/src/" $(FRONT_DIR)/src | xargs -r sed -i 's#@/src/#@/#g' || true
