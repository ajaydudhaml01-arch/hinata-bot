const { SlashCommandBuilder, EmbedBuilder, ActionRowBuilder, ButtonBuilder, ButtonStyle, PermissionFlagsBits } = require('discord.js');

module.exports = {
  data: new SlashCommandBuilder()
    .setName('ticket')
    .setDescription('Configure and setup the support ticket desk.')
    .setDefaultMemberPermissions(PermissionFlagsBits.Administrator)
    .setDMPermission(false)
    .addSubcommand(subcommand => 
      subcommand
        .setName('setup')
        .setDescription('Spawns a support ticket panel with buttons in the current channel.')
    ),
  async execute(interaction, client) {
    const subcommand = interaction.options.getSubcommand();

    if (subcommand === 'setup') {
      const ticketEmbed = new EmbedBuilder()
        .setColor(client.config.colors.primary)
        .setTitle('🎫 Professional Support Desk')
        .setDescription('Welcome to the Support Center! If you require assistance, have questions regarding services, or need to discuss a private server matter with moderation staff, open a private channel below.')
        .addFields(
          { name: '⚡ Speed', value: 'Tickets are generated instantly. Staff is notified automatically.', inline: true },
          { name: '🔒 Privacy', value: 'Each ticket creates a confidential channel viewable only by you and our Support Staff.', inline: true },
          { name: '📝 Instructions', value: 'Click the button below. A popup will ask you for the ticket topic/reason. Please describe your inquiry.', inline: false }
        )
        .setFooter({ text: "Editor's Hideout Support Desk • Secure & Encrypted" })
        .setTimestamp();

      const actionRow = new ActionRowBuilder().addComponents(
        new ButtonBuilder()
          .setCustomId('open_ticket')
          .setLabel('Open Support Ticket')
          .setEmoji('🎫')
          .setStyle(ButtonStyle.Success)
      );

      await interaction.reply({ 
        content: '✅ Support ticket panel successfully created in this channel!', 
        ephemeral: true 
      });

      await interaction.channel.send({ 
        embeds: [ticketEmbed], 
        components: [actionRow] 
      });
    }
  },
};
