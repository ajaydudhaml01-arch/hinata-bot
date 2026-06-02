const { 
  SlashCommandBuilder, 
  EmbedBuilder, 
  ActionRowBuilder, 
  StringSelectMenuBuilder, 
  ComponentType 
} = require('discord.js');

module.exports = {
  data: new SlashCommandBuilder()
    .setName('help')
    .setDescription('Displays a list of all available commands by category.'),
  async execute(interaction, client) {
    const primaryColor = client.config.colors.primary;

    // Home Embed
    const mainEmbed = new EmbedBuilder()
      .setColor(primaryColor)
      .setTitle("📚 Editor's Hideout Bot - Directory")
      .setDescription("Welcome! This multi-purpose bot handles server management, moderation, tickets, and fun tools. Choose a category from the dropdown menu below to view specific commands.")
      .addFields(
        { name: '🛠️ Utility', value: 'System info, user lookups, latency tests.', inline: true },
        { name: '🛡️ Moderation', value: 'Server protection: bans, kicks, timeouts, warnings.', inline: true },
        { name: '🎉 Fun', value: 'Aesthetic polls, random memes, and engagement.', inline: true },
        { name: '🎫 Support Desk', value: 'High-performance private ticketing workflows.', inline: true }
      )
      .setFooter({ text: "Select a category below • Interactive Menu" })
      .setTimestamp();

    // Select Menu setup
    const selectMenu = new StringSelectMenuBuilder()
      .setCustomId('help_category_select')
      .setPlaceholder('Select a Command Category')
      .addOptions([
        {
          label: 'Utility Commands',
          description: 'Access ping, serverinfo, userinfo, and general help.',
          value: 'utility',
          emoji: '🛠️'
        },
        {
          label: 'Moderation Tools',
          description: 'Access warning logs, kicks, bans, purge, and mute actions.',
          value: 'moderation',
          emoji: '🛡️'
        },
        {
          label: 'Fun & Engagement',
          description: 'Access polls and random web memes.',
          value: 'fun',
          emoji: '🎉'
        },
        {
          label: 'Support Tickets',
          description: 'Access ticket portal creations.',
          value: 'tickets',
          emoji: '🎫'
        }
      ]);

    const row = new ActionRowBuilder().addComponents(selectMenu);

    const message = await interaction.reply({ 
      embeds: [mainEmbed], 
      components: [row],
      fetchReply: true 
    });

    // Create a component collector for the menu
    const collector = message.createMessageComponentCollector({
      componentType: ComponentType.StringSelect,
      time: 60000 // 1 minute timeout
    });

    collector.on('collect', async (menuInteraction) => {
      // Validate that only the command issuer can interact with the menu
      if (menuInteraction.user.id !== interaction.user.id) {
        return menuInteraction.reply({ 
          content: "❌ You cannot use this menu. Run `/help` to spawn your own interactive helper.", 
          ephemeral: true 
        });
      }

      await menuInteraction.deferUpdate();
      
      const selectedValue = menuInteraction.values[0];
      const categoryEmbed = new EmbedBuilder().setColor(primaryColor).setTimestamp();

      if (selectedValue === 'utility') {
        categoryEmbed
          .setTitle('🛠️ Utility & System Commands')
          .setDescription('General server utility and testing commands.')
          .addFields(
            { name: '`/help`', value: 'Displays this directory.', inline: false },
            { name: '`/ping`', value: 'Checks bot latency and API speeds.', inline: false },
            { name: '`/serverinfo`', value: 'Displays advanced statistics for the current server.', inline: false },
            { name: '`/userinfo [target]`', value: 'Displays membership info and roles for a target user.', inline: false }
          );
      } else if (selectedValue === 'moderation') {
        categoryEmbed
          .setTitle('🛡️ Moderation & Server Security')
          .setDescription('Commands designed for moderation and security staff.')
          .addFields(
            { name: '`/kick <member> [reason]`', value: 'Removes a member from the server.', inline: false },
            { name: '`/ban <member> [reason]`', value: 'Permanently bans a member from the server.', inline: false },
            { name: '`/timeout <member> <duration> [reason]`', value: 'Temporarily silences a member (duration up to 28 days).', inline: false },
            { name: '`/purge <amount>`', value: 'Deletes up to 100 recent messages from the channel.', inline: false },
            { name: '`/warn <action> <member> [details]`', value: 'Manage warnings. Actions: `add` (issue warning), `list` (view user warnings), `clear` (delete user warnings).', inline: false }
          );
      } else if (selectedValue === 'fun') {
        categoryEmbed
          .setTitle('🎉 Fun & Server Engagement')
          .setDescription('Interactive tools to drive community engagement.')
          .addFields(
            { name: '`/poll <question> <option1> <option2> [opt3]...`', value: 'Launch a beautifully styled, interactive poll where users can vote using buttons. Supports up to 5 options.', inline: false },
            { name: '`/meme`', value: 'Fetches a random safe-for-work meme from web databases.', inline: false }
          );
      } else if (selectedValue === 'tickets') {
        categoryEmbed
          .setTitle('🎫 Professional Support Desk')
          .setDescription('A system to setup dedicated channels for private support.')
          .addFields(
            { name: '`/ticket setup`', value: 'Creates a custom ticket banner panel with a button in the channel. Clicking it opens a private ticket channel for the user and server support staff.', inline: false }
          );
      }

      categoryEmbed.setFooter({ text: `Category: ${selectedValue.toUpperCase()} • Issued by ${interaction.user.tag}` });
      await interaction.editReply({ embeds: [categoryEmbed] });
    });

    // Disable the menu when collector expires
    collector.on('end', async () => {
      const disabledRow = new ActionRowBuilder().addComponents(
        selectMenu.setDisabled(true).setPlaceholder('Help Menu expired. Run /help again.')
      );
      await interaction.editReply({ components: [disabledRow] }).catch(() => {});
    });
  },
};
