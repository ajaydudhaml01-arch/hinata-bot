# Contributing to Hinata

Thanks for helping improve Hinata.

## Before you start

- Search existing issues before opening a duplicate.
- Never include Discord tokens, `.env` contents, private credentials, or sensitive server data.
- Keep pull requests focused on one change when practical.

## Local setup

```bash
git clone https://github.com/ajaydudhaml01-arch/hinata-bot.git
cd hinata-bot
npm install
cp .env.example .env
cp config.example.json config.json
```

On Windows PowerShell, use `Copy-Item` instead of `cp` if preferred.

## Development workflow

1. Create a branch:
   ```bash
   git checkout -b feat/short-description
   ```
2. Make your changes.
3. Run:
   ```bash
   npm run check
   npm test
   ```
4. Commit with a clear message.
5. Push your branch and open a pull request.

## Commit style

Conventional-style prefixes are encouraged:

- `feat:` new functionality
- `fix:` bug fix
- `docs:` documentation
- `test:` tests
- `refactor:` internal code improvement
- `chore:` maintenance

Examples:

```text
feat: add configurable anti-spam threshold
fix: prevent duplicate dynamic voice channels
docs: clarify Discord intent requirements
```

## Pull requests

A good pull request should explain:

- what changed
- why it changed
- how it was tested
- any behavior or configuration changes

Screenshots are welcome for interaction/UI changes.

## Code expectations

- Keep secrets out of source control.
- Prefer clear names over clever abstractions.
- Handle Discord permission failures gracefully.
- Avoid breaking existing configuration without documenting migration steps.
- Add or update tests when practical.

## Reporting security issues

Please follow [SECURITY.md](SECURITY.md).
