const fs = require('fs');
const path = require('path');

module.exports = (client) => {
  client.handleEvents = async () => {
    const eventsPath = path.join(__dirname, '..', 'events');
    const eventFolders = fs.readdirSync(eventsPath);

    for (const folder of eventFolders) {
      const folderPath = path.join(eventsPath, folder);
      const eventFiles = fs.readdirSync(folderPath).filter(file => file.endsWith('.js'));

      for (const file of eventFiles) {
        const filePath = path.join(folderPath, file);
        const event = require(filePath);

        if (event.once) {
          client.once(event.name, (...args) => event.execute(...args, client));
        } else {
          client.on(event.name, (...args) => event.execute(...args, client));
        }
        console.log(`[EventHandler] Loaded event: ${event.name} (${file})`);
      }
    }
  };
};
