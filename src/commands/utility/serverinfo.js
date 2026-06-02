const { SlashCommandBuilder, EmbedBuilder } = require('discord.js');

module.exports = {
  data: new SlashCommandBuilder()
    .setName('serverinfo')
    .setDescription('Displays detailed information about this server.'),
  async execute(interaction, client) {
    const { guild } = interaction;
    const { name, memberCount, ownerId, createdTimestamp, id, description } = guild;

    const owner = await guild.members.fetch(ownerId).catch(() => null);
    const textChannels = guild.channels.cache.filter(c => c.type === 0).size;
    const voiceChannels = guild.channels.cache.filter(c => c.type === 2).size;
    const categories = guild.channels.cache.filter(c => c.type === 4).size;
    const rolesCount = guild.roles.cache.size;
    const emojiCount = guild.emojis.cache.size;

    const serverEmbed = new EmbedBuilder()
      .setColor(client.config.colors.primary)
      .setTitle(name)
      .setDescription(description || 'No server description set.')
      .setThumbnail(guild.iconURL({ dynamic: true, size: 256 }))
      .addFields(
        { name: 'Server Owner', value: owner ? `${owner.user.tag} (${owner.id})` : `ID: ${ownerId}`, inline: false },
        { name: 'Server ID', value: `\`${id}\``, inline: true },
        { name: 'Created On', value: `<t:${Math.floor(createdTimestamp / 1000)}:R>`, inline: true },
        { name: 'Total Members', value: `\`${memberCount}\``, inline: true },
        { name: 'Channels', value: `📁 **${categories}** Categories\n💬 **${textChannels}** Text\n🔊 **${voiceChannels}** Voice`, inline: true },
        { name: 'Custom Assets', value: `🎭 **${rolesCount}** Roles\n😀 **${emojiCount}** Emojis`, inline: true },
        { name: 'Boost Level', value: `📈 Level **${guild.premiumTier}** (${guild.premiumSubscriptionCount} boosts)`, inline: true }
      )
      .setImage(guild.bannerURL({ size: 1024 }))
      .setFooter({ text: `Requested by ${interaction.user.tag}` })
      .setTimestamp();

    await interaction.reply({ embeds: [serverEmbed] });
  },
};
