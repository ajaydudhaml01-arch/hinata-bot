const { SlashCommandBuilder, EmbedBuilder } = require('discord.js');

module.exports = {
  data: new SlashCommandBuilder()
    .setName('ping')
    .setDescription('Check the bot latency and API response times.'),
  async execute(interaction, client) {
    const sent = await interaction.deferReply({ fetchReply: true });
    const roundtrip = sent.createdTimestamp - interaction.createdTimestamp;
    const websocket = client.ws.ping;

    const pingEmbed = new EmbedBuilder()
      .setColor(client.config.colors.primary)
      .setTitle('🏓 Pong!')
      .addFields(
        { name: 'API Latency', value: `\`${roundtrip}ms\``, inline: true },
        { name: 'WebSocket Heartbeat', value: `\`${websocket}ms\``, inline: true }
      )
      .setTimestamp();

    await interaction.editReply({ embeds: [pingEmbed] });
  },
};
