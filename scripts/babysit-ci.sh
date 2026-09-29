#!/bin/bash
# Babysit CI Pipeline
# Monitors GitHub Actions workflow until completion

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Get repo info from git
REPO=$(git config --get remote.origin.url | sed 's/.*github.com.\([^/]*\/[^/]*\).*/\1/')
BRANCH=$(git rev-parse --abbrev-ref HEAD)
COMMIT=$(git rev-parse --short HEAD)

echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}CI Pipeline Babysitter${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}"
echo ""
echo "Repo:   $REPO"
echo "Branch: $BRANCH"
echo "Commit: $COMMIT"
echo ""

# Check if gh CLI is available
if ! command -v gh &> /dev/null; then
    echo -e "${RED}Error: GitHub CLI (gh) not found${NC}"
    echo "Install with: brew install gh (macOS) or see https://cli.github.com"
    exit 1
fi

# Authenticate
echo -e "${YELLOW}Authenticating with GitHub...${NC}"
if ! gh auth status > /dev/null 2>&1; then
    echo "Please authenticate with GitHub:"
    gh auth login
fi

echo ""

# Get pull request info
echo -e "${YELLOW}Finding pull request...${NC}"
PR_DATA=$(gh pr view --json number,state,statusCheckRollup 2>/dev/null || echo "")

if [ -z "$PR_DATA" ]; then
    echo -e "${YELLOW}No pull request found for this branch${NC}"
    echo "You need to create a PR for CI to run"
    exit 1
fi

PR_NUMBER=$(echo "$PR_DATA" | jq -r '.number')
echo -e "${GREEN}✓ Found PR #${PR_NUMBER}${NC}"
echo ""

# Monitor workflow
echo -e "${YELLOW}Monitoring CI workflow...${NC}"
echo "(Press Ctrl+C to stop monitoring)"
echo ""

ATTEMPT=0
MAX_ATTEMPTS=$((60 * 60 / 10))  # 1 hour with 10-second checks
LAST_STATUS=""

while [ $ATTEMPT -lt $MAX_ATTEMPTS ]; do
    # Get status
    STATUS_DATA=$(gh pr view $PR_NUMBER --json statusCheckRollup 2>/dev/null || echo "")

    if [ -z "$STATUS_DATA" ]; then
        ATTEMPT=$((ATTEMPT + 1))
        sleep 10
        continue
    fi

    # Extract checks
    STATE=$(echo "$STATUS_DATA" | jq -r '.statusCheckRollup[0].state // "PENDING"' 2>/dev/null || echo "PENDING")

    # Get all checks
    CHECKS=$(echo "$STATUS_DATA" | jq -r '.statusCheckRollup[] | "\(.name): \(.state // "PENDING")"' 2>/dev/null)

    # Print status if changed
    if [ "$STATE" != "$LAST_STATUS" ]; then
        TIMESTAMP=$(date '+%H:%M:%S')
        LAST_STATUS="$STATE"

        case "$STATE" in
            "SUCCESS")
                echo -e "${GREEN}[${TIMESTAMP}] ✓ All checks passed!${NC}"
                echo ""
                echo -e "${GREEN}═══════════════════════════════════════════════════════${NC}"
                echo -e "${GREEN}CI Pipeline: SUCCESS${NC}"
                echo -e "${GREEN}═══════════════════════════════════════════════════════${NC}"
                exit 0
                ;;
            "FAILURE")
                echo -e "${RED}[${TIMESTAMP}] ✗ One or more checks failed${NC}"
                echo ""
                echo "Failed checks:"
                echo "$CHECKS" | grep -v ": SUCCESS" | grep -v ": PENDING" | sed 's/^/  /'
                echo ""
                echo -e "${RED}═══════════════════════════════════════════════════════${NC}"
                echo -e "${RED}CI Pipeline: FAILED${NC}"
                echo -e "${RED}═══════════════════════════════════════════════════════${NC}"
                echo ""
                echo "View details:"
                echo "  gh pr view $PR_NUMBER --web"
                exit 1
                ;;
            "PENDING"|"IN_PROGRESS")
                echo -e "${BLUE}[${TIMESTAMP}] ⏳ Running checks...${NC}"
                echo "$CHECKS" | sed 's/^/  /'
                ;;
            *)
                echo -e "${YELLOW}[${TIMESTAMP}] ? Unknown status: $STATE${NC}"
                ;;
        esac
        echo ""
    fi

    ATTEMPT=$((ATTEMPT + 1))
    sleep 10
done

echo -e "${RED}Timeout: CI pipeline did not complete within 1 hour${NC}"
exit 1
