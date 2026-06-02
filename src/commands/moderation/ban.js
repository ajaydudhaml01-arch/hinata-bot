const { SlashCommandBuilder, EmbedBuilder, PermissionFlagsBits } = require('discord.js');

module.exports = {
  data: new SlashCommandBuilder()
    .setName('ban')
    .setDescription('Permanently bans a user from the server.')
    .setDefaultMemberPermissions(PermissionFlagsBits.Administrator)
    .setDMPermission(false)
    .addUserOption(option => 
      option.setName('target')
        .setDescription('The user to ban (can be a user ID or server member).')
        .setRequired(true)
    )
    .addStringOption(option => 
      option.setName('reason')
        .setDescription('Reason for banning this member (Optional).')
        .setRequired(false)
    ),
  async execute(interaction, client) {
    // Rigid admin-only access check
    const isOwner = interaction.user.id === interaction.guild.ownerId;
    const isAdmin = interaction.member.permissions.has(PermissionFlagsBits.Administrator);

    if (!isOwner && !isAdmin) {
      return interaction.reply({ 
        content: '❌ Only the Server Owner and Administrators are permitted to execute moderation commands.', 
        ephemeral: true 
      });
    }

    const user = interaction.options.getUser('target');
    const reason = interaction.options.getString('reason') || 'No reason provided';
    const member = await interaction.guild.members.fetch(user.id).catch(() => null);

    if (user.id === interaction.user.id) {
      return interaction.reply({ content: "❌ You cannot ban yourself.", ephemeral: true });
    }

    if (user.id === client.user.id) {
      return interaction.reply({ content: "❌ I cannot ban myself.", ephemeral: true });
    }

    // If the user is inside the server, check role hierarchy
    if (member) {
      if (member.roles.highest.position >= interaction.member.roles.highest.position) {
        return interaction.reply({ 
          content: "❌ You cannot ban this user because they have a higher or equal role hierarchy than you.", 
          ephemeral: true 
        });
      }
      
      if (!member.bannable) {
        return interaction.reply({ 
          content: "❌ I cannot ban this user. Make sure my role position is higher than theirs and I have `Ban Members` permissions.", 
          ephemeral: true 
        });
      }

      // DM the user before banning
      const dmEmbed = new EmbedBuilder()
        .setColor(client.config.colors.danger)
        .setTitle(`🛡️ Banned from ${interaction.guild.name}`)
        .setDescription(`You have been permanently banned from **${interaction.guild.name}**.\n\n**Reason:** ${reason}`)
        .setTimestamp();

      await member.send({ embeds: [dmEmbed] }).catch(() => {
        console.log(`[Ban Command] Could not send direct message to ${user.tag}.`);
      });
    }

    // Execute Ban
    await interaction.guild.members.ban(user.id, { reason });

    const banSuccessEmbed = new EmbedBuilder()
      .setColor(client.config.colors.danger)
      .setTitle('🛡️ Member Banned')
      .setDescription(`Successfully banned **${user.tag}** from the server.`)
      .addFields(
        { name: 'Target User', value: `${user} (\`${user.id}\`)`, inline: true },
        { name: 'Banned By', value: `${interaction.user}`, inline: true },
        { name: 'Reason', value: `\`\`\`${reason}\`\`\`` }
      )
      .setTimestamp();

    await interaction.reply({ embeds: [banSuccessEmbed] });

    // Send Mod Log if channel exists
    const logChannelId = client.config.defaultSettings.logChannelId;
    if (logChannelId) {
      const logChannel = interaction.guild.channels.cache.get(logChannelId);
      if (logChannel) {
        await logChannel.send({ embeds: [banSuccessEmbed] });
      }
    }
  },
};
