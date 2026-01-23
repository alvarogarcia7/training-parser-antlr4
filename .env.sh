if [ -f .venv/bin/activate ]; then
    source .venv/bin/activate
fi

if [[ -f Makefile ]]; then
	make test
fi
