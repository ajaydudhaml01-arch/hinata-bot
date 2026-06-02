const { EmbedBuilder } = require('discord.js');

module.exports = {
  name: 'guildMemberRemove',
  once: false,
  async execute(member, client) {
    const { guild, user } = member;

    console.log(`[Member Left] ${user.tag} left ${guild.name}`);

    // --- AUTOMATED STATISTICS SYSTEM ---
    const statsChannelId = client.config.defaultSettings.memberCountChannelId;
    if (statsChannelId) {
      const statsChannel = guild.channels.cache.get(statsChannelId);
      if (statsChannel) {
        await statsChannel.setName(`🌍┃ Members: ${guild.memberCount}`)
          .then(() => console.log(`[Statistics] Updated member count to: ${guild.memberCount}`))
          .catch(err => console.error('[Statistics Error] Failed to update member count voice channel name:', err));
      }
    }

    const channelId = client.config.defaultSettings.farewellChannelId;
    let farewellChannel = channelId ? guild.channels.cache.get(channelId) : null;

    // Fallback: search for channels with matching names
    if (!farewellChannel) {
      farewellChannel = guild.channels.cache.find(
        c => c.type === 0 && (c.name.includes('leave') || c.name.includes('goodbye') || c.name.includes('welcome'))
      );
    }

    if (farewellChannel) {
      const farewellEmbed = new EmbedBuilder()
        .setColor(client.config.colors.danger)
        .setTitle(`😢 Goodbye, ${user.username}`)
        .setDescription(`**${user.tag}** has left **${guild.name}**. We hope you had a good time!`)
        .setThumbnail(user.displayAvatarURL({ dynamic: true, size: 256 }))
        .addFields(
          { name: '👤 Username', value: `\`${user.tag}\``, inline: true },
          { name: '🆔 User ID', value: `\`${user.id}\``, inline: true },
          { name: '📉 Updated Count', value: `We now have **${guild.memberCount}** members.`, inline: false }
        )
        .setTimestamp();

      await farewellChannel.send({ embeds: [farewellEmbed] })
        .catch(err => console.error('[Farewell System] Failed to send goodbye message:', err));
    }
  },
};
