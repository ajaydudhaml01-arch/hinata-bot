require('dotenv').config();
const { Client, Collection, GatewayIntentBits, Partials } = require('discord.js');
const fs = require('fs');
const path = require('path');
const config = require('./config.json');

// Initialize the client with standard and privileged gateway intents
const client = new Client({
  intents: [
    GatewayIntentBits.Guilds,
    GatewayIntentBits.GuildMembers,
    GatewayIntentBits.GuildMessages,
    GatewayIntentBits.MessageContent,
    GatewayIntentBits.GuildMessageReactions,
    GatewayIntentBits.GuildVoiceStates
  ],
  partials: [
    Partials.Channel,
    Partials.Message,
    Partials.User,
    Partials.GuildMember,
    Partials.Reaction
  ]
});

// Attach collection for slash commands and support configurations
client.commands = new Collection();
client.config = config;

// Ensure local folder for warning data exists
const dataDir = path.join(__dirname, 'data');
if (!fs.existsSync(dataDir)) {
  fs.mkdirSync(dataDir);
}

// Load dynamic handlers
const handlersPath = path.join(__dirname, 'src', 'handlers');
const handlerFiles = fs.readdirSync(handlersPath).filter(file => file.endsWith('.js'));

(async () => {
  for (const file of handlerFiles) {
    require(path.join(handlersPath, file))(client);
  }

  // Bind events and deploy commands
  await client.handleEvents();
  
  // We will call handleCommands inside the 'ready' event once we are logged in,
  // or we can run it here. Running it inside the ready event ensures we have the client.user.id
  // when registering commands. Let's trigger client.handleCommands in ready.js event.

  // Lightweight HTTP Web Server for Koyeb/Render port-binding requirement
  const http = require('http');
  const server = http.createServer((req, res) => {
    res.writeHead(200, { 'Content-Type': 'text/html' });
    res.end('<html><head><title>Hinata Status</title></head><body style="font-family:sans-serif;text-align:center;padding:50px;background:#2B2D31;color:white;"><h1>🟢 Hinata Bot is online and running 24/7!</h1><p>Status page for Koyeb/Render cloud hosting.</p></body></html>');
  });
  const PORT = process.env.PORT || 8080;
  server.listen(PORT, () => {
    console.log(`[Web Server] Listening on port ${PORT}`);
  });

  // Log in to Discord
  if (!process.env.DISCORD_TOKEN) {
    console.error('ERROR: DISCORD_TOKEN is missing in your environment! Please configure the .env file.');
    process.exit(1);
  }

  client.login(process.env.DISCORD_TOKEN);
})();
