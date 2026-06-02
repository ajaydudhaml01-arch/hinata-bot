const { SlashCommandBuilder, PermissionFlagsBits } = require('discord.js');

module.exports = {
  data: new SlashCommandBuilder()
    .setName('purge')
    .setDescription('Deletes a specified number of messages from this channel.')
    .setDefaultMemberPermissions(PermissionFlagsBits.ManageMessages)
    .setDMPermission(false)
    .addIntegerOption(option => 
      option.setName('amount')
        .setDescription('Number of messages to delete (1-100).')
        .setMinValue(1)
        .setMaxValue(100)
        .setRequired(true)
    ),
  async execute(interaction, client) {
    const amount = interaction.options.getInteger('amount');

    await interaction.deferReply({ ephemeral: true });

    try {
      // Fetch messages and filter out those older than 14 days (Discord restriction)
      const deleted = await interaction.channel.bulkDelete(amount, true);

      await interaction.editReply({ 
        content: `✅ Successfully purged \`${deleted.size}\` messages from this channel.` 
      });

      // Send a temporary public confirmation that deletes itself
      const publicMsg = await interaction.channel.send({ 
        content: `🧹 **Purged \`${deleted.size}\` messages** by ${interaction.user}` 
      });

      setTimeout(async () => {
        await publicMsg.delete().catch(() => {});
      }, 4000);

    } catch (error) {
      console.error('[Purge Command Error]', error);
      await interaction.editReply({ 
        content: '❌ Failed to purge messages. Messages older than 14 days cannot be deleted in bulk due to Discord API limitations.' 
      });
    }
  },
};
