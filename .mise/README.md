# mise Configuration for CineMatch

This directory contains mise-specific configuration and documentation.

## What is mise?

[mise](https://mise.jdx.dev/) is a polyglot tool version manager that automatically installs and manages project-specific tool versions. Think of it as a modern alternative to nvm, pyenv, rbenv, etc., but for all languages.

## First Time Setup

```bash
# 1. Install mise (if not already installed)
curl https://mise.run | sh

# 2. Activate mise in your shell (add to ~/.zshrc or ~/.bashrc)
echo 'eval "$(mise activate zsh)"' >> ~/.zshrc  # for zsh
# or
echo 'eval "$(mise activate bash)"' >> ~/.bashrc  # for bash

# 3. Restart your shell or run:
source ~/.zshrc  # or source ~/.bashrc

# 4. Navigate to the project directory
cd /path/to/cinematch

# 5. Trust the configuration (first time only)
mise trust

# 6. Install all tools
mise install
```

## Verifying Installation

```bash
# Check mise status
mise doctor

# List installed tools
mise list

# Verify tool versions
python --version  # Should show 3.11.x
node --version    # Should show 20.x.x
pnpm --version    # Latest version
just --version    # Latest version
terraform version # Should show 1.7.0
uv --version      # Latest version
```

## How It Works

When you `cd` into the project directory, mise automatically:
1. Reads `.mise.toml` in the project root
2. Installs any missing tools
3. Adds them to your PATH

When you leave the directory, your global tools are restored.

## Tools Managed by mise

| Tool | Version | Purpose |
|------|---------|---------|
| python | 3.11 | Backend runtime |
| uv | latest | Python package manager |
| node | 20 | Frontend runtime |
| pnpm | latest | JavaScript package manager |
| just | latest | Task runner |
| terraform | 1.7.0 | Infrastructure as code |

## Without Shell Activation

If you can't or don't want to activate mise in your shell, you can still use it:

```bash
# Run a command with mise tools
mise exec -- python --version

# Start a subshell with tools available
mise shell

# Use mise to run just commands
mise exec -- just check
```

## CI/CD

The GitHub Actions workflow doesn't use mise directly. Instead, it installs tools using GitHub Actions (setup-python, setup-node, etc.). The versions in `.mise.toml` are kept in sync with `.github/workflows/ci-cd.yml` manually.

## Troubleshooting

**Tools not found after installation:**
- Make sure you've activated mise in your shell
- Try `mise doctor` to check the setup
- Restart your shell after activation

**"Config files are not trusted" error:**
- Run `mise trust` in the project directory

**Want to update a tool version:**
- Edit `.mise.toml`
- Run `mise install` to install the new version
- Commit the change

**Check which version is active:**
```bash
mise current
```

**Update mise itself:**
```bash
mise self-update
```

## Documentation

- [mise Documentation](https://mise.jdx.dev/)
- [Configuration Reference](https://mise.jdx.dev/configuration.html)
- [CLI Reference](https://mise.jdx.dev/cli/)
