# Running GitHub Actions Locally with Act

This repository is configured to run GitHub Actions workflows locally using [act](https://github.com/nektos/act).

## Installation

### macOS
```bash
brew install act
```

### Linux
```bash
curl https://raw.githubusercontent.com/nektos/act/master/install.sh | sudo bash
```

### Windows
```bash
choco install act-cli
```

Or download binaries from the [releases page](https://github.com/nektos/act/releases).

## Prerequisites

- Docker must be installed and running
- Sufficient disk space for Docker images (~1-2GB for medium image)

## Configuration

The repository includes a `.actrc` file that configures act to use the medium-sized Docker image (`catthehacker/ubuntu:act-latest`), which provides better compatibility with the CI workflow requirements.

## Running Workflows

### Run all jobs in the CI workflow
```bash
act
```

### Run a specific job
```bash
act -j compile-grammar
act -j typecheck
act -j test
act -j e2e-test
```

### Run on push event
```bash
act push
```

### Run on pull request event
```bash
act pull_request
```

### List available workflows and jobs
```bash
act -l
```

### Dry run (show what would be executed)
```bash
act -n
```

### Run with verbose output
```bash
act -v
```

## Common Issues

### Java setup
The workflow requires Java 11 for compiling ANTLR4 grammar. The medium image includes Java, but if you encounter issues, you can use the full image:
```bash
act -P ubuntu-latest=catthehacker/ubuntu:full-latest
```

### Artifact upload/download
Act has limited support for artifact actions. Jobs that depend on artifacts from previous jobs may need to be run with the `--artifact-server-path` flag:
```bash
act --artifact-server-path /tmp/artifacts
```

### Cache actions
Cache actions may not work perfectly in local environments. If you encounter cache-related issues, the workflow will fall back to downloading and compiling resources.

## Workflow Overview

The CI workflow includes four jobs:

1. **compile-grammar**: Compiles ANTLR4 grammar and uploads artifacts
2. **typecheck**: Downloads compiled grammar and runs mypy type checking
3. **test**: Downloads compiled grammar and runs pytest
4. **e2e-test**: Downloads compiled grammar and runs end-to-end tests with sample data

Due to artifact dependencies, you may need to run jobs sequentially or use the artifact server path flag.

## Tips

- First run will download the Docker image (~1GB), subsequent runs will be faster
- Use `-j <job-name>` to test individual jobs during development
- Use `--secret-file .secrets` if your workflow needs secrets (not required for this repo)
- Act uses your local filesystem, so changes to code are immediately reflected
