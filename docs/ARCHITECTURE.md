# Architecture

Hinata uses a modular CommonJS structure built on Discord.js.

## Entry point

`index.js`:

- loads environment variables with `dotenv`
- creates the Discord client with required gateway intents
- attaches the command collection and configuration
- loads handler modules from `src/handlers`
- starts the lightweight HTTP health endpoint
- logs in using `DISCORD_TOKEN`

## Handlers

`src/handlers/` is responsible for discovering and registering application behavior such as commands and events.

This keeps startup logic in `index.js` relatively small and allows features to remain modular.

## Commands

`src/commands/` is grouped by feature category:

- `fun/`
- `moderation/`
- `tickets/`
- `utility/`

New commands should follow the same export contract used by existing commands and should be placed in the most appropriate category.

## Events

`src/events/` contains Discord event listeners and background automation.

Examples of behavior implemented through events can include:

- interaction handling
- message-based automation
- member join/leave behavior
- voice state changes
- leveling and moderation automation

## Configuration

Secrets belong in `.env`.

Reusable server settings are documented in `config.example.json`. Each deployment should create its own ignored `config.json`.

## Persistence

The current project uses local JSON files for some runtime state. This is simple for a single instance, but larger deployments should eventually use a database or another shared persistence layer.

Runtime JSON files are excluded from Git.
