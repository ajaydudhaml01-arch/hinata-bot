const { EmbedBuilder } = require('discord.js');

module.exports = {
  name: 'guildMemberAdd',
  once: false,
  async execute(member, client) {
    const { guild, user } = member;

    console.log(`[Member Joined] ${user.tag} joined ${guild.name}`);

    // --- AUTO-ROLE SYSTEM ---
    const roleName = client.config.defaultSettings.welcomeRoleName;
    if (roleName) {
      const role = guild.roles.cache.find(r => r.name.toLowerCase() === roleName.toLowerCase());
      if (role) {
        await member.roles.add(role)
          .then(() => console.log(`[AutoRole] Assigned role "${roleName}" to ${user.tag}`))
          .catch(err => console.error(`[AutoRole] Failed to assign role to ${user.tag}:`, err));
      }
    }

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

    // --- WELCOME EMBED ---
    const channelId = client.config.defaultSettings.welcomeChannelId;
    let welcomeChannel = channelId ? guild.channels.cache.get(channelId) : null;

    // Fallback: search for channels with matching names
    if (!welcomeChannel) {
      welcomeChannel = guild.channels.cache.find(
        c => c.type === 0 && (c.name.includes('welcome') || c.name.includes('joins') || c.name.includes('door'))
      );
    }

    if (welcomeChannel) {
      const welcomeEmbed = new EmbedBuilder()
        .setColor(client.config.colors.primary)
        .setTitle(`✨ Welcome to ${guild.name}!`)
        .setDescription(`Hello ${member}, we are thrilled to have you here at **${guild.name}**!\n\nTake a moment to introduce yourself, grab some roles, and check out our text channels.`)
        .setThumbnail(user.displayAvatarURL({ dynamic: true, size: 256 }))
        .addFields(
          { name: '👤 Username', value: `\`${user.tag}\``, inline: true },
          { name: '🆔 User ID', value: `\`${user.id}\``, inline: true },
          { name: '📈 Server Count', value: `You are our **#${guild.memberCount}** member!`, inline: false }
        )
        .setFooter({ text: `Account Created: ${user.createdAt.toDateString()}` })
        .setTimestamp();

      await welcomeChannel.send({ content: `👋 Welcome ${member}!`, embeds: [welcomeEmbed] })
        .catch(err => console.error('[Welcome System] Failed to send welcome message:', err));
    }
  },
};
