# Security Policy

## Supported versions

Security fixes are targeted at the latest code on `main` and the latest published release.

## Reporting a vulnerability

Please **do not open a public issue containing exploit details, tokens, credentials, private server information, or other sensitive data**.

Preferred reporting path:

1. Use GitHub's private vulnerability reporting / Security Advisory flow for this repository when available.
2. If private reporting is unavailable, open a minimal public issue stating that you found a security problem **without including sensitive technical details**, so the maintainer can arrange a safer channel.

Include, when safe:

- affected feature/file
- impact
- reproduction conditions
- suggested mitigation, if known

## Discord bot secrets

A Discord bot token gives control of the bot account. If a token is ever exposed:

1. Reset it immediately in the Discord Developer Portal.
2. Update the secret in your deployment environment.
3. Remove it from source control and consider cleaning Git history.
4. Review recent bot activity.

Never commit `.env` files or production credentials.
