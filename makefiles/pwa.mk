# PWA Deployment Targets
# Progressive Web App packaging, local network serving, and GitHub Pages deployment

pwa-build: check-virtual-env
	@echo "Packaging PWA for deployment..."
	@mkdir -p dist/pwa
	@cp -r mobile-app/* dist/pwa/
	@echo "Copying Python modules into PWA..."
	@cp -r parser dist/pwa/
	@cp -r src dist/pwa/
	@cp -r dist dist/pwa/
	@cp -r data dist/pwa/
	@if [ -d mobile-app/pyodide ]; then \
		echo "Copying Pyodide to PWA..."; \
		cp -r mobile-app/pyodide dist/pwa/; \
	fi
	@echo "PWA packaged to dist/pwa/"
	@echo "To test locally: python3 -m http.server -d dist/pwa 8080"
	@echo "Open: http://localhost:8080/"
.PHONY: pwa-build

download-pyodide:
	@echo "Downloading Pyodide for offline support..."
	@chmod +x scripts/download-pyodide.sh
	@./scripts/download-pyodide.sh
.PHONY: download-pyodide

pwa-build-offline: download-pyodide pwa-build
	@echo "✓ PWA ready for offline deployment (includes local Pyodide)"
.PHONY: pwa-build-offline

pwa-publish: pwa-build
	@echo "Publishing PWA to github-pages branch..."
	@if ! git rev-parse --verify gh-pages >/dev/null 2>&1; then \
		echo "Creating github-pages branch..."; \
		git checkout --orphan gh-pages; \
		git rm -rf . 2>/dev/null || true; \
		git commit --allow-empty -m "Initial commit for GitHub Pages"; \
		git checkout $(shell git rev-parse --abbrev-ref HEAD); \
	fi
	@git worktree add -B gh-pages /tmp/pwa-deploy origin/gh-pages 2>/dev/null || git worktree add -B gh-pages /tmp/pwa-deploy HEAD
	@rm -rf /tmp/pwa-deploy/*
	@cp -r dist/pwa/* /tmp/pwa-deploy/
	@echo ".gitkeep" > /tmp/pwa-deploy/.gitkeep
	@cd /tmp/pwa-deploy && git add -A && git commit -m "Deploy PWA from $(shell git rev-parse --short HEAD)" && git push origin gh-pages || echo "No changes to commit"
	@git worktree remove /tmp/pwa-deploy || true
	@echo "PWA published to github-pages branch"
	@echo "GitHub Pages URL: https://$(shell git remote get-url origin | sed 's/.*github.com.\([^/]*\)\/\(.*\)\.git/\1.github.io\/\2/')"
.PHONY: pwa-publish

pwa-serve-local: check-virtual-env
	@echo "Starting local HTTPS server for PWA..."
	@if [ ! -f certs/cert.pem ] || [ ! -f certs/key.pem ]; then \
		echo "SSL certificates not found. Generating..."; \
		chmod +x scripts/create-ssl-certs.sh; \
		./scripts/create-ssl-certs.sh; \
	fi
	python3 scripts/serve-local.py --host 0.0.0.0 --port 8444
.PHONY: pwa-serve-local

pwa-certs:
	@echo "Generating SSL certificates for local HTTPS..."
	@chmod +x scripts/create-ssl-certs.sh
	@./scripts/create-ssl-certs.sh
.PHONY: pwa-certs

pwa-clean:
	@echo "Cleaning PWA build artifacts..."
	@rm -rf dist/pwa
	@echo "✓ PWA build artifacts removed"
.PHONY: pwa-clean

# CORS Proxy for development
# Used to handle CORS restrictions when testing git sync with cross-origin servers

CORS_PORT?=8081
CORS_PROXY_PID?=.cors-proxy.pid

pwa-cors-proxy:
	@if [ -f $(CORS_PROXY_PID) ] && kill -0 $$(cat $(CORS_PROXY_PID)) 2>/dev/null; then \
		echo "✓ CORS proxy already running (PID: $$(cat $(CORS_PROXY_PID)))"; \
	else \
		echo "Starting CORS proxy on http://localhost:$(CORS_PORT)"; \
		node /tmp/cors-proxy.js > /tmp/cors-proxy.log 2>&1 & \
		echo $$! > $(CORS_PROXY_PID); \
		sleep 2; \
		if curl -s http://localhost:$(CORS_PORT) > /dev/null 2>&1; then \
			echo "✅ CORS proxy running"; \
		else \
			echo "❌ Failed to start CORS proxy"; \
			exit 1; \
		fi; \
	fi
.PHONY: pwa-cors-proxy

pwa-cors-proxy-stop:
	@if [ -f $(CORS_PROXY_PID) ]; then \
		if kill -0 $$(cat $(CORS_PROXY_PID)) 2>/dev/null; then \
			kill $$(cat $(CORS_PROXY_PID)); \
			echo "✓ CORS proxy stopped"; \
		fi; \
		rm $(CORS_PROXY_PID); \
	else \
		echo "CORS proxy not running"; \
	fi
.PHONY: pwa-cors-proxy-stop

pwa-serve: pwa-serve-http
	@echo "💡 Tip: Run 'make pwa-cors-proxy' in another terminal for CORS proxy support"
	@echo "💡 For local git testing, also run: make local-git-server"
.PHONY: pwa-serve

pwa-serve-http:
	@echo "Starting PWA on http://localhost:8080/mobile-app/"
	uv run python3 serve.py
.PHONY: pwa-serve-http

# Local Git Server for Testing
# Serves git repositories over HTTP with CORS headers for PWA testing

local-git-server:
	@if [ ! -f /tmp/git-server/git-http-server.js ]; then \
		echo "❌ Git server script not found at /tmp/git-server/git-http-server.js"; \
		echo "Run: setup-local-git-server"; \
		exit 1; \
	fi
	@echo "Starting local git server on http://localhost:8888/"
	@echo "Repository: http://localhost:8888/test-repo.git"
	cd /tmp/git-server && nohup node git-http-server.js > /tmp/git-server.log 2>&1 &
	@echo "✅ Git server started (logs: /tmp/git-server.log)"
.PHONY: local-git-server

setup-local-git-server:
	@echo "Setting up local git server..."
	@mkdir -p /tmp/git-server
	@if [ ! -f /tmp/git-server/git-http-server.js ]; then \
		cp scripts/git-http-server.js /tmp/git-server/; \
		echo "✓ Copied git HTTP server"; \
	fi
	@if [ ! -f /tmp/cors-proxy.js ]; then \
		cp scripts/cors-proxy.js /tmp/cors-proxy.js; \
		echo "✓ Copied CORS proxy"; \
	fi
	@if [ ! -d /tmp/git-server/test-repo.git ]; then \
		cd /tmp/git-server && git init --bare test-repo.git; \
		mkdir temp-setup && cd temp-setup && \
		git clone ../test-repo.git . && \
		echo "# Test Training Workout" > README.md && \
		git config user.email "test@local" && \
		git config user.name "Test User" && \
		git add README.md && \
		git commit -m "Initial workout data" && \
		git push -u origin main && \
		cd /tmp/git-server && rm -rf temp-setup; \
		echo "✓ Created test repository"; \
	fi
	@echo "✅ Local git server setup complete"
	@echo "   Run: make local-git-server"
.PHONY: setup-local-git-server

# E2E Testing
# Starts the dev server, waits for it to be ready, runs tests, then cleans up

PWA_SERVER_PID?=.pwa-server.pid
PWA_PORT?=8080

test-e2e: check-virtual-env
	@echo "Checking dependencies..."
	@if [ ! -d node_modules ]; then \
		echo "Installing npm dependencies..."; \
		npm install; \
	fi
	@echo "Installing Playwright browsers (chromium)..."
	@npx playwright install --with-deps chromium > /dev/null 2>&1
	@echo "Starting PWA server for E2E tests..."
	@if [ -f $(PWA_SERVER_PID) ] && kill -0 $$(cat $(PWA_SERVER_PID)) 2>/dev/null; then \
		echo "✓ PWA server already running (PID: $$(cat $(PWA_SERVER_PID)))"; \
	else \
		echo "Starting new PWA server on http://localhost:$(PWA_PORT)"; \
		uv run python3 serve.py > /tmp/pwa-server.log 2>&1 & \
		echo $$! > $(PWA_SERVER_PID); \
		\
		echo "Waiting for server to be ready (max 30 seconds)..."; \
		MAX_ATTEMPTS=30; \
		ATTEMPT=0; \
		while [ $$ATTEMPT -lt $$MAX_ATTEMPTS ]; do \
			if curl -s http://localhost:$(PWA_PORT) > /dev/null 2>&1; then \
				echo "✅ PWA server is ready"; \
				break; \
			fi; \
			ATTEMPT=$$((ATTEMPT + 1)); \
			echo "  Attempt $$ATTEMPT/$$MAX_ATTEMPTS..."; \
			sleep 1; \
		done; \
		\
		if [ $$ATTEMPT -eq $$MAX_ATTEMPTS ]; then \
			echo "❌ PWA server failed to start"; \
			kill $$(cat $(PWA_SERVER_PID)) 2>/dev/null || true; \
			rm $(PWA_SERVER_PID); \
			tail -20 /tmp/pwa-server.log; \
			exit 1; \
		fi; \
	fi
	@echo "Running E2E tests..."; \
	TEST_RESULT=0; \
	npm run test:e2e || TEST_RESULT=$$?; \
	echo "Stopping PWA server..."; \
	if [ -f $(PWA_SERVER_PID) ] && kill -0 $$(cat $(PWA_SERVER_PID)) 2>/dev/null; then \
		kill $$(cat $(PWA_SERVER_PID)); \
		sleep 1; \
		echo "✓ PWA server stopped"; \
	fi; \
	rm -f $(PWA_SERVER_PID); \
	if [ $$TEST_RESULT -ne 0 ]; then exit $$TEST_RESULT; fi; \
	echo "✅ E2E tests completed"
.PHONY: test-e2e

test-e2e-debug: check-virtual-env
	@echo "Checking dependencies..."
	@if [ ! -d node_modules ]; then \
		echo "Installing npm dependencies..."; \
		npm install; \
	fi
	@echo "Installing Playwright browsers (chromium)..."
	@npx playwright install --with-deps chromium > /dev/null 2>&1
	@echo "Starting PWA server for E2E debug..."
	@if [ -f $(PWA_SERVER_PID) ] && kill -0 $$(cat $(PWA_SERVER_PID)) 2>/dev/null; then \
		echo "✓ PWA server already running"; \
	else \
		uv run python3 serve.py > /tmp/pwa-server.log 2>&1 & \
		echo $$! > $(PWA_SERVER_PID); \
		sleep 3; \
	fi
	@echo "Starting E2E tests in debug mode..."
	@npm run test:e2e:debug
.PHONY: test-e2e-debug
