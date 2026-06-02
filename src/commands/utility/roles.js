const { SlashCommandBuilder, EmbedBuilder, ActionRowBuilder, ButtonBuilder, ButtonStyle, PermissionFlagsBits } = require('discord.js');

module.exports = {
  data: new SlashCommandBuilder()
    .setName('roles')
    .setDescription('Configure self-assignable role panels.')
    .setDefaultMemberPermissions(PermissionFlagsBits.Administrator)
    .setDMPermission(false)
    .addSubcommand(subcommand =>
      subcommand
        .setName('setup')
        .setDescription('Deploys a button-based self-role card in the current channel.')
        .addRoleOption(option => option.setName('role1').setDescription('First selectable role.').setRequired(true))
        .addRoleOption(option => option.setName('role2').setDescription('Second selectable role.').setRequired(true))
        .addRoleOption(option => option.setName('role3').setDescription('Third selectable role (Optional).').setRequired(false))
        .addRoleOption(option => option.setName('role4').setDescription('Fourth selectable role (Optional).').setRequired(false))
        .addRoleOption(option => option.setName('role5').setDescription('Fifth selectable role (Optional).').setRequired(false))
    ),
  async execute(interaction, client) {
    const subcommand = interaction.options.getSubcommand();

    if (subcommand === 'setup') {
      const r1 = interaction.options.getRole('role1');
      const r2 = interaction.options.getRole('role2');
      const r3 = interaction.options.getRole('role3');
      const r4 = interaction.options.getRole('role4');
      const r5 = interaction.options.getRole('role5');

      const roles = [r1, r2];
      if (r3) roles.push(r3);
      if (r4) roles.push(r4);
      if (r5) roles.push(r5);

      const boardEmbed = new EmbedBuilder()
        .setColor(client.config.colors.primary)
        .setTitle('🎭 Self-Assign Interest Roles')
        .setDescription('Personalize your experience! Click the corresponding buttons below to toggle interest roles on or off. A popup will let you know when the role has been successfully modified.')
        .addFields({
          name: 'Selected Roles Available',
          value: roles.map((role, idx) => `🔹 **Option ${idx + 1}**: ${role}`).join('\n')
        })
        .setFooter({ text: "Editor's Hideout Role Portal • Direct Assignment" })
        .setTimestamp();

      const row = new ActionRowBuilder();

      roles.forEach((role, idx) => {
        row.addComponents(
          new ButtonBuilder()
            .setCustomId(`role_toggle_${role.id}`)
            .setLabel(role.name)
            .setStyle(ButtonStyle.Secondary)
        );
      });

      await interaction.reply({ content: '✅ Self-role board successfully deployed!', ephemeral: true });
      await interaction.channel.send({ embeds: [boardEmbed], components: [row] });
    }
  },
};
