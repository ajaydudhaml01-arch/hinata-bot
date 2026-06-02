const { ActivityType } = require('discord.js');

module.exports = {
  name: 'ready',
  once: true,
  async execute(client) {
    console.log(`[Bot Online] Logged in as ${client.user.tag}`);

    // Set custom status
    client.user.setPresence({
      activities: [{ name: "Editor's Hideout | /help", type: ActivityType.Watching }],
      status: 'online',
    });

    // Deploy / refresh slash commands
    console.log('[Bot Initialization] Starting to register slash commands...');
    await client.handleCommands();
    console.log('[Bot Initialization] Commands registered successfully. Ready to receive commands.');
  },
};
