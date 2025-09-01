# ==== Core ====
DC := docker compose
# Path base = directory that holds THIS Makefile (works even if `make` is run elsewhere)
MKFILE_DIR := $(abspath $(dir $(lastword $(MAKEFILE_LIST))))

# Monorepo paths (repo-relative)
FRONT_DIR  := apps/ui
BACK_DIR   := apps/backend
BIN_DIR    := $(BACK_DIR)/src/minimalgotronifylicious/bin
DATA_DIR   := $(BACK_DIR)/data/symbols

# NSE cache paths (overridable from CLI/env)
NSE_SCRIP_MASTER_CSV  ?= $(DATA_DIR)/nse_scrip_master.csv
NSE_SCRIP_MASTER_JSON ?= $(DATA_DIR)/nse_scrip_master.json
BINANCE_SYMBOLS_JSON  ?= $(DATA_DIR)/binance_exchangeInfo.json

.PHONY: fresh dev up down rebuild logs be-logs ui-logs exec health \
				paper live ui-dev ui-build ui-type ui-lint fix-imports \
				test lint

# ==== Orchestrations ====
## down + prune + build --no-cache + up
fresh:
	$(DC) down -v --remove-orphans || true
	@docker system prune -f || true
	$(DC) build --no-cache
	$(DC) up

dev: ## build (with cache) + up
	$(DC) up --build

up: ## start stack
	$(DC) up -d

down: ## stop stack
	$(DC) down

logs: ## tail all services
	$(DC) logs -f

be-logs: ## tail backend logs
	$(DC) logs -f backend

exec: ## run a command in a service (S=<service> C='<cmd>')
	$(DC) exec $(S) sh -lc "$(C)"

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
	$(DC) run --rm -p $(FRONTEND_PORT):$(FRONTEND_PORT) frontend npm run dev

ui-build: ## build frontend
	$(DC) run --rm frontend npm ci
	$(DC) run --rm frontend npm run build

ui-type: ## typecheck frontend
	$(DC) run --rm frontend npm run typecheck

ui-lint: ## lint frontend
	$(DC) run --rm frontend npm run lint

## build symbol caches (Binance+NSE)
symbols: symbols-binance symbols-nse

symbols-binance:
	mkdir -p $(DATA_DIR)
	python3 $(BIN_DIR)/save_binance_exchangeinfo.py -o $(BINANCE_SYMBOLS_JSON)
	@echo "Set BINANCE_SYMBOLS_PATH=$(BINANCE_SYMBOLS_JSON) in your .env"

symbols-binance-fut: ## cache Binance futures symbols
	mkdir -p /home/sinhurry/Documents/GitHub/minimalgotronifylicious/apps/backend/data/symbols
	python3 apps/backend/src/minimalgotronifylicious/bin/save_binance_exchangeinfo.py --futures -o /home/sinhurry/Documents/GitHub/minimalgotronifylicious/apps/backend/data/symbols/binance_futures_exchangeInfo.json

## Convert NSE scrip-master CSV → JSON for UI picker
symbols-nse: ## convert NSE scrip-master CSV -> JSON
	@mkdir -p $(DATA_DIR)
	@if [ ! -s "$(NSE_SCRIP_MASTER_CSV)" ]; then \
	  echo "⚠️  Missing: $(NSE_SCRIP_MASTER_CSV)"; \
	  echo "   Put the NSE scrip-master CSV there (or run with NSE_SCRIP_MASTER_CSV=<path>) and re-run:"; \
	  echo "   make symbols-nse"; \
	else \
	  python3 $(BIN_DIR)/convert_nse_scrip_master.py \
	    -i "$(NSE_SCRIP_MASTER_CSV)" \
	    -o "$(NSE_SCRIP_MASTER_JSON)"; \
	  echo "Set NSE_SYMBOLS_PATH=$(NSE_SCRIP_MASTER_JSON) in your .env"; \
	fi


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
