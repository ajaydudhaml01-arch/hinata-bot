# 📚 Editor's Hideout Bot - Comprehensive User Guide

Welcome to the **Editor's Hideout** multi-purpose Discord bot! This bot handles moderation, support ticket systems, server analytics, user lookups, welcome/leave logs, and interactive community polls.

---

## 🛠️ Step 1: Getting a Discord Bot Token
To run this bot, you must create a Discord Application in the Discord Developer Portal:

1. Visit the [Discord Developer Portal](https://discord.com/developers/applications).
2. Click **New Application** in the top right, name your bot (e.g., "Editor's Hideout Assistant"), and save.
3. On the left sidebar, navigate to the **Bot** tab.
4. Click **Reset Token** to generate a new Bot Token. **Copy this token immediately** and paste it into your `.env` file under `DISCORD_TOKEN`.
5. Scroll down to the **Privileged Gateway Intents** section:
   - **Enable** `Presence Intent`
   - **Enable** `Server Members Intent` *(Required for the Welcome/Farewell system)*
   - **Enable** `Message Content Intent` *(Required for warning systems and message filters)*
6. Click **Save Changes**.

---

## 🔗 Step 2: Inviting the Bot to Your Server
To invite the bot, generate a secure invite URL:

1. In the Developer Portal, go to the **OAuth2** tab, then select the **URL Generator** sub-tab.
2. In the **Scopes** checklist, check `bot` and `applications.commands` (needed for Slash Commands).
3. In the **Bot Permissions** checklist that appears below, select the following permissions:
   - `Administrator` (Recommended for full do-everything features) OR select the following specific ones:
     - `Manage Channels` *(Needed for support ticket creations)*
     - `Manage Roles` *(Needed for auto-member role assignment)*
     - `Kick Members` & `Ban Members` & `Moderate Members` *(Needed for moderation)*
     - `Send Messages`, `Embed Links`, `Attach Files`, `Read Message History`, `Add Reactions`
4. Copy the generated URL at the bottom of the page, paste it into a web browser, and authorize it for your server.

---

## ⚙️ Step 3: Local Configuration (.env & config.json)

### 1. Configure the Environment Variables (`.env`)
Open your `.env` file in your editor and enter the details:
```env
DISCORD_TOKEN=your_bot_token_here
CLIENT_ID=your_bot_client_id_here
GUILD_ID=your_development_server_id_here
```
> **Tip:** You can find the **Client ID** under the **General Information** tab of your bot's Developer Portal.
> You can find the **Guild ID** (Server ID) by turning on Developer Mode in your Discord client settings, right-clicking your server icon on the left, and clicking **Copy Server ID**. Providing `GUILD_ID` ensures that commands load instantly during development!

### 2. Tailor Bot Settings (`config.json`)
Open `config.json` and configure channels to activate automation:
```json
{
  "colors": {
    "primary": "#5865F2",
    "success": "#57F287",
    "warning": "#FEE75C",
    "danger": "#ED4245",
    "info": "#3498DB",
    "neutral": "#2B2D31"
  },
  "defaultSettings": {
    "welcomeChannelId": "YOUR_WELCOME_CHANNEL_ID",
    "farewellChannelId": "YOUR_FAREWELL_CHANNEL_ID",
    "welcomeRoleName": "Member",
    "ticketCategoryId": "YOUR_TICKET_CATEGORY_ID",
    "ticketStaffRoleId": "YOUR_STAFF_ROLE_ID",
    "logChannelId": "YOUR_MOD_LOG_CHANNEL_ID"
  }
}
```
*Leave IDs blank (`""`) if you want the bot to use dynamic search fallbacks (like looking for a channel named `welcome`).*

---

## 🚀 Step 4: Running the Bot
Once configured, you can launch the bot!

1. Open your terminal in the project directory.
2. Run the start command:
   ```bash
   node index.js
   ```
3. You should see confirmation logs:
   ```text
   [Bot Online] Logged in as Editor's Hideout Assistant#1234
   [Bot Initialization] Starting to register slash commands...
   Started refreshing 9 application (/) commands.
   Successfully reloaded application (/) commands for development Guild: ...
   [Bot Initialization] Commands registered successfully. Ready to receive commands.
   ```

---

## 📚 Complete Command Reference

| Command | Category | Description |
|:---|:---|:---|
| `/help` | Utility | Opens a dynamic select menu detailing all features. |
| `/ping` | Utility | Checks the bot's WebSocket and API latency. |
| `/serverinfo` | Utility | Displays rich statistics about the server. |
| `/userinfo [target]` | Utility | Displays details and roles for a specified server member. |
| `/kick <target> [reason]` | Moderation | Kicks a member with permission checks and logs. |
| `/ban <target> [reason]` | Moderation | Permanently bans a member from the guild. |
| `/timeout <target> <duration> [reason]` | Moderation | Temporarily silences a member (choice list durations). |
| `/purge <amount>` | Moderation | Bulk deletes up to 100 messages from the channel. |
| `/warn add <target> <details>` | Moderation | Issues a warning to a member (saves to local DB). |
| `/warn list <target>` | Moderation | Lists all warnings logged for a member. |
| `/warn clear <target>` | Moderation | Clears warning history for a member. |
| `/poll <q> <opt1> <opt2> [opts...]` | Fun | Launches an interactive poll with custom vote buttons. |
| `/meme` | Fun | Fetches a random, safe-for-work meme from Reddit. |
| `/ticket setup` | Tickets | Spawns a support panel with a button to open private tickets. |
| `/rank [target]` | Utility | Displays a member's XP progress, level, and leaderboard rank. |
| `/roles setup <roles...>` | Tickets | Spawns a premium self-assignable button-role selection panel. |

---

## 🤖 Advanced Autonomous Automation Systems

Your bot operates fully automatically in the background across four modular systems:

### 1. 🛡️ Auto-Moderation (AutoMod) & Anti-Spam
- **Invite link block**: Automatically deletes messages containing server invite links, sends warning details via DMs, registers an official warning in `warnings.json`, and outputs logs in your mod logs.
- **Word Filter**: Auto-deletes keywords listed in `config.json` -> `blockedWords` and logs warnings.
- **Anti-Spam Shield**: If a user spams more than 5 messages in 4 seconds, the bot deletes their spam and **applies a 5-minute timeout (mute)** automatically.
*(Bypasses administrators and moderators automatically).*

### 2. 🔊 Dynamic Voice Channels ("Join-to-Create")
1. To activate, create a voice channel in your server (e.g. `➕ Create VC`).
2. Copy the Channel ID and paste it into `config.json` -> `joinToCreateChannelId`.
3. When a user joins this channel, the bot immediately creates a voice channel named `🔊 [User]'s Room` under the same category, moves the user into it, and **deletes the channel automatically** when the last member leaves!

### 3. 🎭 Button-Roles Setup
1. Run `/roles setup` and specify up to 5 roles.
2. The bot deploys a card showing the options.
3. Users click the corresponding buttons to self-assign or remove the roles on-demand ephemerally.

### 4. 📈 Activity Leveling System (XP & Leaderboards)
- Members earn 15-25 XP once per minute for chatting (anti-spam cooldown prevents spam leveling).
- Saves levels securely inside `data/levels.json`.
- Automatically posts a level-up embed in chat when thresholds are met.
- **Automatic Milestone Roles**: You can define role grants in `config.json` -> `levelRoles` (e.g., `"5": "ROLE_ID"` grants that role when a user reaches level 5).

