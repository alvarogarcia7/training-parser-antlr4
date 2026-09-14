# PWA Deployment Targets
# Progressive Web App packaging, local network serving, and GitHub Pages deployment

pwa-build: check-virtual-env
	@echo "Packaging PWA for deployment..."
	@mkdir -p dist/pwa
	@cp -r mobile-app/* dist/pwa/
	@echo "PWA packaged to dist/pwa/"
	@echo "To test locally: python3 -m http.server -d dist/pwa 8080"
	@echo "Open: http://localhost:8080/"
.PHONY: pwa-build

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
