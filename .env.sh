if [ -f .venv/bin/activate ]; then
    source .venv/bin/activate
fi

if ! command java; then
  echo "Java not found / not working. Overriding java"
  export PATH="/opt/homebrew/opt/openjdk@11/bin:$PATH"
fi

if [[ -f Makefile ]]; then
	make test
fi
