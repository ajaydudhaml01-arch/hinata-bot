const { SlashCommandBuilder, EmbedBuilder, PermissionFlagsBits } = require('discord.js');

module.exports = {
  data: new SlashCommandBuilder()
    .setName('kick')
    .setDescription('Removes a user from the server.')
    .setDefaultMemberPermissions(PermissionFlagsBits.Administrator)
    .setDMPermission(false)
    .addUserOption(option => 
      option.setName('target')
        .setDescription('The member you want to kick.')
        .setRequired(true)
    )
    .addStringOption(option => 
      option.setName('reason')
        .setDescription('Reason for kicking this member (Optional).')
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

    const target = interaction.options.getMember('target');
    const reason = interaction.options.getString('reason') || 'No reason provided';

    if (!target) {
      return interaction.reply({ 
        content: '❌ That user does not appear to be in this server.', 
        ephemeral: true 
      });
    }

    // Role Hierarchy & Permission Safeguards
    if (target.id === interaction.user.id) {
      return interaction.reply({ content: "❌ You cannot kick yourself.", ephemeral: true });
    }

    if (target.id === client.user.id) {
      return interaction.reply({ content: "❌ I cannot kick myself.", ephemeral: true });
    }

    if (target.roles.highest.position >= interaction.member.roles.highest.position) {
      return interaction.reply({ 
        content: "❌ You cannot kick this user because they have a higher or equal role hierarchy than you.", 
        ephemeral: true 
      });
    }

    if (!target.kickable) {
      return interaction.reply({ 
        content: "❌ I cannot kick this user. Make sure my role position is higher than theirs and I have `Kick Members` permissions.", 
        ephemeral: true 
      });
    }

    // DM the user before kicking
    const dmEmbed = new EmbedBuilder()
      .setColor(client.config.colors.danger)
      .setTitle(`🛡️ Kicked from ${interaction.guild.name}`)
      .setDescription(`You have been kicked from **${interaction.guild.name}**.\n\n**Reason:** ${reason}`)
      .setTimestamp();

    await target.send({ embeds: [dmEmbed] }).catch(() => {
      console.log(`[Kick Command] Could not send direct message to ${target.user.tag}.`);
    });

    // Execute Kick
    await target.kick(reason);

    const kickSuccessEmbed = new EmbedBuilder()
      .setColor(client.config.colors.success)
      .setTitle('👤 Member Kicked')
      .setDescription(`Successfully kicked **${target.user.tag}** from the server.`)
      .addFields(
        { name: 'Target User', value: `${target.user} (\`${target.id}\`)`, inline: true },
        { name: 'Kicked By', value: `${interaction.user}`, inline: true },
        { name: 'Reason', value: `\`\`\`${reason}\`\`\`` }
      )
      .setTimestamp();

    await interaction.reply({ embeds: [kickSuccessEmbed] });

    // Send Mod Log if channel exists
    const logChannelId = client.config.defaultSettings.logChannelId;
    if (logChannelId) {
      const logChannel = interaction.guild.channels.cache.get(logChannelId);
      if (logChannel) {
        await logChannel.send({ embeds: [kickSuccessEmbed] });
      }
    }
  },
};
