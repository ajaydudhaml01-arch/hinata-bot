const { SlashCommandBuilder, EmbedBuilder, PermissionFlagsBits } = require('discord.js');

module.exports = {
  data: new SlashCommandBuilder()
    .setName('timeout')
    .setDescription('Temporarily silences (mutes) a server member.')
    .setDefaultMemberPermissions(PermissionFlagsBits.ModerateMembers)
    .setDMPermission(false)
    .addUserOption(option => 
      option.setName('target')
        .setDescription('The member you want to mute.')
        .setRequired(true)
    )
    .addIntegerOption(option => 
      option.setName('duration')
        .setDescription('Duration of the mute.')
        .setRequired(true)
        .addChoices(
          { name: '60 Seconds', value: 60 },
          { name: '5 Minutes', value: 300 },
          { name: '10 Minutes', value: 600 },
          { name: '1 Hour', value: 3600 },
          { name: '1 Day', value: 86400 },
          { name: '1 Week', value: 604800 }
        )
    )
    .addStringOption(option => 
      option.setName('reason')
        .setDescription('Reason for the mute (Optional).')
        .setRequired(false)
    ),
  async execute(interaction, client) {
    const target = interaction.options.getMember('target');
    const durationSeconds = interaction.options.getInteger('duration');
    const reason = interaction.options.getString('reason') || 'No reason provided';

    if (!target) {
      return interaction.reply({ 
        content: '❌ That user does not appear to be in this server.', 
        ephemeral: true 
      });
    }

    if (target.id === interaction.user.id) {
      return interaction.reply({ content: "❌ You cannot mute yourself.", ephemeral: true });
    }

    if (target.id === client.user.id) {
      return interaction.reply({ content: "❌ I cannot mute myself.", ephemeral: true });
    }

    if (target.roles.highest.position >= interaction.member.roles.highest.position) {
      return interaction.reply({ 
        content: "❌ You cannot mute this user because they have a higher or equal role hierarchy than you.", 
        ephemeral: true 
      });
    }

    if (!target.moderatable) {
      return interaction.reply({ 
        content: "❌ I cannot mute this user. Make sure my role position is higher than theirs and I have `Timeout Members` permissions.", 
        ephemeral: true 
      });
    }

    const durationMs = durationSeconds * 1000;

    // Send DM to target
    const dmEmbed = new EmbedBuilder()
      .setColor(client.config.colors.warning)
      .setTitle(`🛡️ Timed Out in ${interaction.guild.name}`)
      .setDescription(`You have been temporarily muted in **${interaction.guild.name}**.\n\n**Duration:** ${durationSeconds / 60 >= 1 ? `${durationSeconds / 60} minute(s)` : `${durationSeconds} second(s)`}\n**Reason:** ${reason}`)
      .setTimestamp();

    await target.send({ embeds: [dmEmbed] }).catch(() => {
      console.log(`[Timeout Command] Could not send direct message to ${target.user.tag}.`);
    });

    // Execute Timeout
    await target.timeout(durationMs, reason);

    const timeoutEmbed = new EmbedBuilder()
      .setColor(client.config.colors.warning)
      .setTitle('🤫 Member Muted')
      .setDescription(`Successfully applied timeout to **${target.user.tag}**.`)
      .addFields(
        { name: 'Target Member', value: `${target} (\`${target.id}\`)`, inline: true },
        { name: 'Muted By', value: `${interaction.user}`, inline: true },
        { name: 'Duration', value: `\`${durationSeconds / 60 >= 1 ? `${durationSeconds / 60} minute(s)` : `${durationSeconds} second(s)`}\``, inline: true },
        { name: 'Reason', value: `\`\`\`${reason}\`\`\`` }
      )
      .setTimestamp();

    await interaction.reply({ embeds: [timeoutEmbed] });

    // Send Mod Log if channel exists
    const logChannelId = client.config.defaultSettings.logChannelId;
    if (logChannelId) {
      const logChannel = interaction.guild.channels.cache.get(logChannelId);
      if (logChannel) {
        await logChannel.send({ embeds: [timeoutEmbed] });
      }
    }
  },
};
