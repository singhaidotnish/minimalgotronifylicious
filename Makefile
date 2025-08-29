# ==== Core ====
DC := docker compose
BACK_SERVICE := backend
FRONT_DIR := apps/ui
BACK_DIR := apps/backend

.PHONY: fresh dev up down rebuild logs be-logs ui-logs exec health \
				paper live ui-dev ui-build ui-type ui-lint fix-imports \
				test lint

# ==== Orchestrations ====
## down + prune + build --no-cache + up
fresh:
	@docker compose down -v --remove-orphans || true
	@docker system prune -f || true
	@docker compose build --no-cache
	@docker compose up

dev: ## build (with cache) + up
	@docker compose up --build

up: ## start stack
	@docker compose up -d

down: ## stop stack
	@docker compose down

logs: ## tail all services
	@docker compose logs -f

be-logs: ## tail backend logs
	@docker compose logs -f backend

exec: ## run a command in a service (S=<service> C='<cmd>')
	@docker compose exec $(S) sh -lc "$(C)"

## curl backend /api/health
health:
	@curl -fsS "$(BACKEND_URL)/api/health" || true

## up using .env.paper
paper:
	@env $$(cat .env.paper | xargs) docker compose up --build

## up using .env.live
live:
	@env $$(cat .env.live | xargs) docker compose up --build

## start frontend dev server
ui-dev:
	@docker compose run --rm -p $(FRONTEND_PORT):$(FRONTEND_PORT) frontend npm run dev

ui-build: ## build frontend
	@docker compose run --rm frontend npm ci
	@docker compose run --rm frontend npm run build

ui-type: ## typecheck frontend
	@docker compose run --rm frontend npm run typecheck

ui-lint: ## lint frontend
	@docker compose run --rm frontend npm run lint

## build symbol caches (Binance+NSE)
symbols: symbols-binance symbols-nse

symbols-binance: ## cache Binance spot symbols
	mkdir -p data/symbols
	python3 apps/backend/src/minimalgotronifylicious/bin/save_binance_exchangeinfo.py -o data/symbols/binance_exchangeInfo.json
	@echo "Set BINANCE_SYMBOLS_PATH=data/symbols/binance_exchangeInfo.json in your .env"

symbols-binance-fut: ## cache Binance futures symbols
	mkdir -p data/symbols
	python3 apps/backend/src/minimalgotronifylicious/bin/save_binance_exchangeinfo.py --futures -o data/symbols/binance_futures_exchangeInfo.json

symbols-nse: ## convert NSE scrip-master CSV -> JSON
	mkdir -p data/symbols
	python3 apps/backend/src/minimalgotronifylicious/bin/convert_nse_scrip_master.py -i data/symbols/nse_scrip_master.csv -o data/symbols/nse_scrip_master.json
	@echo "Set NSE_SYMBOLS_PATH=data/symbols/nse_scrip_master.json in your .env"

# Default target
.DEFAULT_GOAL := help

##@ General
.PHONY: help
help: ## Show this help (auto-generated)
	@awk 'BEGIN{ \
		FS=":"; \
		section="General"; \
		printf "\033[1m%s\033[0m\n", section \
	} \
	/^##@/ { \
		section=substr($$0,5); \
		printf "\n\033[1m%s\033[0m\n", section; \
		next \
	} \
	/^[[:space:]]*$$/ { next } \
	/^[a-zA-Z0-9_./%-]+:[^=]*##/ { \
		split($$0,a,"##"); \
		split(a[1],t,":"); \
		printf "  \033[36m%-24s\033[0m %s\n", t[1], a[2]; \
		next \
	} \
	/^##[^@]/ { \
		desc=substr($$0,4); \
		getline; \
		if ($$0 ~ /^[a-zA-Z0-9_./%-]+:/) { \
			split($$0,t,":"); \
			printf "  \033[36m%-24s\033[0m %s\n", t[1], desc \
		} \
	}' $(MAKEFILE_LIST)
