const { SlashCommandBuilder, EmbedBuilder, ActionRowBuilder, ButtonBuilder, ButtonStyle } = require('discord.js');

module.exports = {
  data: new SlashCommandBuilder()
    .setName('poll')
    .setDescription('Creates a beautiful interactive poll with button-based voting.')
    .addStringOption(option => option.setName('question').setDescription('The main poll question.').setRequired(true))
    .addStringOption(option => option.setName('option1').setDescription('First voting choice.').setRequired(true))
    .addStringOption(option => option.setName('option2').setDescription('Second voting choice.').setRequired(true))
    .addStringOption(option => option.setName('option3').setDescription('Third voting choice (Optional).').setRequired(false))
    .addStringOption(option => option.setName('option4').setDescription('Fourth voting choice (Optional).').setRequired(false))
    .addStringOption(option => option.setName('option5').setDescription('Fifth voting choice (Optional).').setRequired(false)),
  async execute(interaction, client) {
    const question = interaction.options.getString('question');
    const opt1 = interaction.options.getString('option1');
    const opt2 = interaction.options.getString('option2');
    const opt3 = interaction.options.getString('option3');
    const opt4 = interaction.options.getString('option4');
    const opt5 = interaction.options.getString('option5');

    const options = [opt1, opt2];
    if (opt3) options.push(opt3);
    if (opt4) options.push(opt4);
    if (opt5) options.push(opt5);

    const pollEmbed = new EmbedBuilder()
      .setColor(client.config.colors.primary)
      .setTitle(`📊 Poll: ${question}`)
      .setDescription('Click one of the buttons below to cast your vote! You can toggle or change your vote at any time.')
      .setAuthor({ name: interaction.user.tag, iconURL: interaction.user.displayAvatarURL() })
      .setTimestamp();

    // Default bar layout before votes are cast
    const defaultBar = '⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜ **0%** (0 votes)';

    options.forEach((opt, idx) => {
      pollEmbed.addFields({
        name: `${idx + 1}. ${opt}`,
        value: defaultBar,
        inline: false
      });
    });

    pollEmbed.setFooter({ text: 'Total Votes: 0 • Interactive Poll' });

    // Buttons creation row
    const row = new ActionRowBuilder();
    const buttonEmojis = ['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣'];

    options.forEach((_, idx) => {
      row.addComponents(
        new ButtonBuilder()
          .setCustomId(`poll_vote_${idx}`)
          .setLabel(`Option ${idx + 1}`)
          .setEmoji(buttonEmojis[idx])
          .setStyle(ButtonStyle.Secondary)
      );
    });

    await interaction.reply({ embeds: [pollEmbed], components: [row] });
  },
};
