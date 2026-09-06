# Hinata

[![CI](https://github.com/ajaydudhaml01-arch/hinata-bot/actions/workflows/ci.yml/badge.svg)](https://github.com/ajaydudhaml01-arch/hinata-bot/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
![Node.js](https://img.shields.io/badge/Node.js-18.18%2B-brightgreen)

**Hinata** is a modular, open-source Discord bot built with Discord.js. It combines moderation, tickets, leveling, dynamic voice channels, self-roles, welcome/farewell automation, polls, server utilities, and a lightweight health endpoint for cloud hosting.

The goal is to provide a clean base that community owners and developers can configure, extend, and self-host.

## Features

- **Moderation** — kick, ban, timeout, purge, warnings, logging
- **Auto-moderation** — invite filtering, blocked-word filtering, anti-spam protection
- **Support tickets** — private ticket channel creation and staff access
- **Leveling** — XP, levels, leaderboard support, milestone roles
- **Dynamic voice channels** — join-to-create voice rooms that clean themselves up
- **Self roles** — button-based role assignment
- **Community tools** — polls, memes, user info, server info, latency checks
- **Member automation** — welcome/farewell messages and optional member role
- **Cloud-friendly** — lightweight HTTP health page for Render/Koyeb-style hosting
- **Modular structure** — commands, events, and handlers are separated under `src/`

## Requirements

- Node.js **18.18 or newer**
- npm
- A Discord application and bot token
- A Discord server where you can manage the bot

## Quick start

```bash
git clone https://github.com/ajaydudhaml01-arch/hinata-bot.git
cd hinata-bot
npm install
```

Create your local environment file:

```powershell
Copy-Item .env.example .env
```

On macOS/Linux:

```bash
cp .env.example .env
```

Fill in:

```env
DISCORD_TOKEN=your_bot_token_here
CLIENT_ID=your_discord_application_client_id
GUILD_ID=your_development_server_id
```

Create your local bot configuration:

```powershell
Copy-Item config.example.json config.json
```

Then edit `config.json` for your server and start Hinata:

```bash
npm start
```

> `config.json`, `.env`, and runtime JSON data are intentionally ignored by Git so your server-specific configuration and generated data do not become part of the public repository.

## Discord setup

In the Discord Developer Portal:

1. Create an application and bot.
2. Enable the intents required by the features you use:
   - Server Members Intent
   - Message Content Intent
   - Presence Intent if needed by your deployment/features
3. Invite the bot with the `bot` and `applications.commands` scopes.
4. Grant only the permissions required by the features you enable.

Avoid granting `Administrator` unless you understand and explicitly need the additional access.

## Commands

Hinata currently includes commands across these groups:

| Group | Examples |
| --- | --- |
| Utility | `/help`, `/ping`, `/serverinfo`, `/userinfo`, `/rank` |
| Moderation | `/kick`, `/ban`, `/timeout`, `/purge`, `/warn` |
| Community | `/poll`, `/meme` |
| Tickets | `/ticket setup` |
| Roles | `/roles setup` |

Command availability can evolve as the project is updated. See `src/commands/` for the source of truth.

## Configuration

`config.example.json` contains the reusable configuration template.

Important settings include:

- `welcomeChannelId`
- `farewellChannelId`
- `welcomeRoleName`
- `ticketCategoryId`
- `ticketStaffRoleId`
- `logChannelId`
- `joinToCreateChannelId`
- `blockedWords`
- `levelRoles`
- `memberCountChannelId`

Leave optional IDs as empty strings when a feature is not configured.

## Project structure

```text
hinata-bot/
├── index.js
├── src/
│   ├── commands/
│   ├── events/
│   └── handlers/
├── data/                 # local runtime data; contents are ignored
├── tests/
├── config.example.json
├── .env.example
└── .github/
```

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for a contributor-oriented overview.

## Development

Check syntax:

```bash
npm run check
```

Run tests:

```bash
npm test
```

The repository includes GitHub Actions CI for supported Node.js versions.

## Hosting

Hinata starts a lightweight HTTP server on `PORT` (default `8080`) in addition to the Discord client. This helps platforms that require an HTTP listener for service health checks.

For production:

- store secrets in the host's environment-variable/secret manager
- never commit `.env`
- use persistent storage if you need local JSON data to survive restarts
- consider a database for larger or multi-instance deployments

## Data and privacy

The current leveling/warning systems may store Discord identifiers and bot-generated state in local JSON files. Runtime data under `data/` is intentionally excluded from Git.

Server owners are responsible for informing their users about any data they collect and for complying with applicable Discord policies and privacy requirements.

## Security

Never post your Discord bot token, `.env` file, private credentials, or sensitive server data in an issue.

For vulnerability reporting, read [SECURITY.md](SECURITY.md).

## Contributing

Contributions are welcome. Please read [CONTRIBUTING.md](CONTRIBUTING.md) before opening a pull request.

Useful places to start:

- bug fixes
- tests
- documentation
- per-guild configuration improvements
- persistence/database adapters
- accessibility and UX improvements for interactions

## Roadmap

See [ROADMAP.md](ROADMAP.md).

## License

Hinata is released under the [MIT License](LICENSE).

## Maintainer

Maintained by [Ajay Dudhmal](https://github.com/ajaydudhaml01-arch).
