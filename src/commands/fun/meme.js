const { SlashCommandBuilder, EmbedBuilder } = require('discord.js');
const axios = require('axios');

module.exports = {
  data: new SlashCommandBuilder()
    .setName('meme')
    .setDescription('Fetches a random safe-for-work meme from Reddit.'),
  async execute(interaction, client) {
    await interaction.deferReply();

    try {
      // Fetch a random meme from the open-source meme API
      const response = await axios.get('https://meme-api.com/gimme');
      const data = response.data;

      // Ensure that NSFW memes are filtered out to keep the server family-friendly
      if (data.nsfw) {
        return interaction.editReply('🔞 A mature meme was retrieved, but filtered out to keep this server safe. Please try again!');
      }

      const memeEmbed = new EmbedBuilder()
        .setColor(client.config.colors.primary)
        .setTitle(data.title || 'Meme')
        .setURL(data.postLink)
        .setImage(data.url)
        .setFooter({ text: `r/${data.subreddit} • Author: ${data.author} • 👍 ${data.ups}` })
        .setTimestamp();

      await interaction.editReply({ embeds: [memeEmbed] });

    } catch (error) {
      console.error('[Meme Command Error]', error);
      await interaction.editReply('❌ Failed to fetch a meme. Please try again later.');
    }
  },
};
