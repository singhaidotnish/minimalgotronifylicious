# ====== paths & tooling ======
ENV_ROOT := .env
ENV_BACK := apps/backend/.env
ENV_FRONT := apps/ui/.env
DC := docker compose

# ====== helpers ======
define ensure_env
	@if [ ! -f "$(1)" ]; then \
		if [ -f "$(1).example" ]; then \
			echo "⛳  $(1) missing — creating from $(1).example"; \
			cp "$(1).example" "$(1)"; \
		else \
			echo "⚠️  $(1) missing — creating empty placeholder"; \
			mkdir -p $(dir $(1)); \
			touch "$(1)"; \
		fi \
	fi
endef

# ====== meta ======
.PHONY: help
help:
	@echo ""
	@echo "Mini Orchestrator — make <target>"
	@echo ""
	@echo "  env-check     Ensure .env files exist (root, backend, frontend)"
	@echo "  dev           Up all services in foreground (build if needed)"
	@echo "  up            Up all services in background (build if needed)"
	@echo "  down          Stop all services"
	@echo "  logs          Tail docker logs"
	@echo "  ps            Show service status"
	@echo "  rebuild       Rebuild images (no cache)"
	@echo "  prune         Stop & remove volumes/orphans + docker prune"
	@echo "  fresh         Clean slate: prune -> rebuild -> up -d"
	@echo "  ui-build      Build frontend production bundle inside container"
	@echo ""

# ====== sanity ======
.PHONY: env-check
env-check:
	@$(call ensure_env,$(ENV_ROOT))
	@$(call ensure_env,$(ENV_BACK))
	@$(call ensure_env,$(ENV_FRONT))
	@echo "✅ env files present:"; ls -lh $(ENV_ROOT) $(ENV_BACK) $(ENV_FRONT) | cat

# ====== day-to-day ======
.PHONY: dev
dev: env-check
	$(DC) up --build

.PHONY: up
up: env-check
	$(DC) up -d --build

.PHONY: down
down:
	$(DC) down

.PHONY: logs
logs:
	$(DC) logs -f --tail=200

.PHONY: ps
ps:
	$(DC) ps

.PHONY: rebuild
rebuild:
	$(DC) build --no-cache

.PHONY: prune
prune:
	$(DC) down -v --remove-orphans
	-docker system prune -f

# ====== your requested targets (kept) ======
# full reset → rebuild → start
.PHONY: fresh
fresh: prune rebuild up
	@echo "🌱 fresh stack is up"

# build the frontend bundle inside its container
# works for Next or Vite as long as package.json has 'build'
.PHONY: ui-build
ui-build: env-check
	# Ensure deps, then build. Use a throwaway container so the image stays clean.
	$(DC) run --rm frontend sh -lc "npm ci || npm install && npm run build"
	@echo "🧱 frontend build finished"

# convenience: pass arbitrary 'service cmd="..."'
# usage: make help    -> see this message
#        make exec S=backend C='bash'
.PHONY: exec
exec:
	@if [ -z "$(S)" ] || [ -z "$(C)" ]; then \
		echo "Usage: make exec S=<service> C='<command>'"; \
		echo "Example: make exec S=backend C='bash'"; \
		exit 2; \
	fi
	$(DC) exec $(S) sh -lc "$(C)"
