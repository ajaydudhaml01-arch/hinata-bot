const { SlashCommandBuilder, EmbedBuilder, ActionRowBuilder, ButtonBuilder, ButtonStyle } = require('discord.js');

module.exports = {
  data: new SlashCommandBuilder()
    .setName('request')
    .setDescription('Submit an anime clip or flow frame rendering request.')
    .addStringOption(option => 
      option.setName('anime')
        .setDescription('The name of the anime.')
        .setRequired(true)
    )
    .addStringOption(option => 
      option.setName('timestamp')
        .setDescription('The episode and timestamp (e.g. Episode 3, 14:20).')
        .setRequired(true)
    )
    .addStringOption(option => 
      option.setName('details')
        .setDescription('Any specific instructions (e.g., interpolate to 60fps, logoless).')
        .setRequired(true)
    ),
  async execute(interaction, client) {
    const anime = interaction.options.getString('anime');
    const timestamp = interaction.options.getString('timestamp');
    const details = interaction.options.getString('details');

    const requestChannelId = '1468444989263450227'; // 🧐┃flow-frames-request channel ID
    const requestChannel = interaction.guild.channels.cache.get(requestChannelId);

    if (!requestChannel) {
      return interaction.reply({
        content: '❌ The request channel `🧐┃flow-frames-request` is not found or configured in this server. Please contact an administrator.',
        ephemeral: true
      });
    }

    const requestId = interaction.id; // Unique interaction ID to track this specific request

    const requestEmbed = new EmbedBuilder()
      .setColor(client.config.colors.primary)
      .setTitle('🧐 New Flow-Frame Request')
      .setDescription(`A new rendering request has been submitted. Staff can claim or deny below.`)
      .addFields(
        { name: '🎬 Anime / Media', value: `\`${anime}\``, inline: true },
        { name: '⏱️ Timestamp', value: `\`${timestamp}\``, inline: true },
        { name: '📝 Details / Instructions', value: `\`\`\`${details}\`\`\`` },
        { name: '👤 Requester', value: `${interaction.user} (\`${interaction.user.id}\`)`, inline: true },
        { name: '⚡ Status', value: '⏳ **Pending Staff Claim**', inline: true }
      )
      .setFooter({ text: `Request ID: ${requestId} • Editor's Hideout Queue` })
      .setTimestamp();

    const row = new ActionRowBuilder().addComponents(
      new ButtonBuilder()
        .setCustomId(`request_claim_${requestId}`)
        .setLabel('Claim Request')
        .setEmoji('🛠️')
        .setStyle(ButtonStyle.Success),
      new ButtonBuilder()
        .setCustomId(`request_deny_${requestId}`)
        .setLabel('Deny')
        .setEmoji('❌')
        .setStyle(ButtonStyle.Danger)
    );

    // Save in-memory or log metadata if needed
    if (!client.activeRequests) client.activeRequests = new Map();
    client.activeRequests.set(requestId, {
      userId: interaction.user.id,
      anime: anime,
      timestamp: timestamp,
      details: details,
      status: 'pending'
    });

    try {
      await requestChannel.send({ embeds: [requestEmbed], components: [row] });
      
      await interaction.reply({
        content: `✅ Your request for **${anime}** has been posted successfully in ${requestChannel}!`,
        ephemeral: true
      });
    } catch (err) {
      console.error('[Request Command Error] Failed to post request:', err);
      await interaction.reply({
        content: '❌ Failed to submit request. Make sure the bot has permission to write in the request channel.',
        ephemeral: true
      });
    }
  },
};
