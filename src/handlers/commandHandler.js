const fs = require('fs');
const path = require('path');
const { REST, Routes } = require('discord.js');

module.exports = (client) => {
  client.handleCommands = async () => {
    const commandsPath = path.join(__dirname, '..', 'commands');
    const commandFolders = fs.readdirSync(commandsPath);

    const commandsArray = [];

    for (const folder of commandFolders) {
      const folderPath = path.join(commandsPath, folder);
      const commandFiles = fs.readdirSync(folderPath).filter(file => file.endsWith('.js'));

      for (const file of commandFiles) {
        const filePath = path.join(folderPath, file);
        const command = require(filePath);

        if ('data' in command && 'execute' in command) {
          // Set command in Collection
          client.commands.set(command.data.name, command);
          // Format for REST API registration
          commandsArray.push(command.data.toJSON());
          console.log(`[CommandHandler] Loaded command: ${command.data.name}`);
        } else {
          console.warn(`[CommandHandler] The command at ${filePath} is missing a required "data" or "execute" property.`);
        }
      }
    }

    const rest = new REST({ version: '10' }).setToken(process.env.DISCORD_TOKEN);

    try {
      console.log(`Started refreshing ${commandsArray.length} application (/) commands.`);

      if (process.env.GUILD_ID) {
        // Registering to specific development guild (Instant update)
        await rest.put(
          Routes.applicationGuildCommands(process.env.CLIENT_ID, process.env.GUILD_ID),
          { body: commandsArray }
        );
        console.log(`Successfully reloaded application (/) commands for development Guild: ${process.env.GUILD_ID}`);
      } else {
        // Registering globally (May take up to an hour, but usually fast in modern Discord API)
        await rest.put(
          Routes.applicationCommands(process.env.CLIENT_ID),
          { body: commandsArray }
        );
        console.log('Successfully reloaded application (/) commands globally.');
      }
    } catch (error) {
      console.error('Error occurred while registering slash commands:', error);
    }
  };
};
