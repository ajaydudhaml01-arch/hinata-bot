const { SlashCommandBuilder, EmbedBuilder } = require('discord.js');

module.exports = {
  data: new SlashCommandBuilder()
    .setName('userinfo')
    .setDescription('Displays information about a server member.')
    .addUserOption(option => 
      option.setName('target')
        .setDescription('The member you want to view info about (Optional).')
        .setRequired(false)
    ),
  async execute(interaction, client) {
    const user = interaction.options.getUser('target') || interaction.user;
    const member = await interaction.guild.members.fetch(user.id).catch(() => null);

    if (!member) {
      return interaction.reply({ 
        content: '❌ Could not find that member in this server.', 
        ephemeral: true 
      });
    }

    const roles = member.roles.cache
      .filter(r => r.id !== interaction.guild.id) // Exclude @everyone
      .map(r => r.toString())
      .join(', ') || 'No roles assigned';

    const userEmbed = new EmbedBuilder()
      .setColor(client.config.colors.primary)
      .setTitle(`User Info - ${user.tag}`)
      .setThumbnail(user.displayAvatarURL({ dynamic: true, size: 256 }))
      .addFields(
        { name: 'Display Name', value: member.displayName, inline: true },
        { name: 'User ID', value: `\`${user.id}\``, inline: true },
        { name: 'Is Bot?', value: user.bot ? '🤖 Yes' : '👤 No', inline: true },
        { name: 'Joined Discord', value: `<t:${Math.floor(user.createdTimestamp / 1000)}:R>`, inline: true },
        { name: 'Joined Server', value: `<t:${Math.floor(member.joinedTimestamp / 1000)}:R>`, inline: true },
        { name: 'Highest Role', value: `${member.roles.highest}`, inline: true },
        { name: `Roles [${member.roles.cache.size - 1}]`, value: roles.length > 1024 ? `${roles.substring(0, 1000)}...` : roles, inline: false }
      )
      .setFooter({ text: `Requested by ${interaction.user.tag}` })
      .setTimestamp();

    await interaction.reply({ embeds: [userEmbed] });
  },
};
