if [ -f .venv/bin/activate ]; then
    source .venv/bin/activate
fi

java >/dev/null 2>&1
if [[ ! $? -eq 0 ]]; then
  echo "Java not found / not working. Overriding java"
  export PATH="/opt/homebrew/opt/openjdk@11/bin:$PATH"
fi

if ! command uv ; then
  echo "uv not found or not working. Overriding uv"
  export PATH="$PATH:$HOME/.local/bin"
fi

if [[ -f Makefile ]]; then
	make test
fi
