const { SlashCommandBuilder, EmbedBuilder } = require('discord.js');
const fs = require('fs');
const path = require('path');

const levelsFilePath = path.join(__dirname, '..', '..', '..', 'data', 'levels.json');

function readLevels() {
  try {
    if (!fs.existsSync(levelsFilePath)) return {};
    const data = fs.readFileSync(levelsFilePath, 'utf8');
    return JSON.parse(data || '{}');
  } catch (err) {
    console.error('[Rank Command] Failed to read levels DB:', err);
    return {};
  }
}

module.exports = {
  data: new SlashCommandBuilder()
    .setName('rank')
    .setDescription("View your or another member's level and server experience ranking.")
    .addUserOption(option =>
      option.setName('target')
        .setDescription('The user whose level details you want to view (Optional).')
        .setRequired(false)
    ),
  async execute(interaction, client) {
    const targetUser = interaction.options.getUser('target') || interaction.user;

    if (targetUser.bot) {
      return interaction.reply({ content: '❌ Bots do not earn experience points.', ephemeral: true });
    }

    const guildId = interaction.guild.id;
    const db = readLevels();

    if (!db[guildId] || !db[guildId][targetUser.id]) {
      return interaction.reply({
        content: targetUser.id === interaction.user.id 
          ? "❌ You haven't earned any experience points yet. Send a few messages in chat to start earning!"
          : `❌ **${targetUser.tag}** hasn't earned any experience points yet.`,
        ephemeral: true
      });
    }

    const userData = db[guildId][targetUser.id];
    const level = userData.level;
    const xp = userData.xp;

    // Calculate XP needed for next level
    // Formula: 5 * (level^2) + (50 * level) + 100
    const xpNeeded = 5 * Math.pow(level, 2) + 50 * level + 100;

    // Calculate Server Rank
    const guildMembersData = db[guildId];
    const sortedMembers = Object.keys(guildMembersData)
      .map(id => ({
        id: id,
        level: guildMembersData[id].level,
        xp: guildMembersData[id].xp
      }))
      .sort((a, b) => {
        if (b.level !== a.level) {
          return b.level - a.level;
        }
        return b.xp - a.xp;
      });

    const rank = sortedMembers.findIndex(m => m.id === targetUser.id) + 1;

    // Generate sleek progress bar
    const barLength = 10;
    const progress = Math.min(xp / xpNeeded, 1);
    const filledBlocks = Math.round(progress * barLength);
    const emptyBlocks = barLength - filledBlocks;
    const progressBar = '🟩'.repeat(filledBlocks) + '⬜'.repeat(emptyBlocks);
    const percentage = Math.round(progress * 100);

    const rankEmbed = new EmbedBuilder()
      .setColor(client.config.colors.primary)
      .setTitle(`⭐ Experience Card - ${targetUser.username}`)
      .setThumbnail(targetUser.displayAvatarURL({ dynamic: true, size: 256 }))
      .addFields(
        { name: 'Server Rank', value: `🏆 **#${rank}** of \`${sortedMembers.length}\``, inline: true },
        { name: 'Current Level', value: `✨ Level **${level}**`, inline: true },
        { name: 'XP Progress', value: `📊 \`${xp}\` / \`${xpNeeded}\` XP (${percentage}%)`, inline: false },
        { name: 'Progress Bar', value: `${progressBar}`, inline: false }
      )
      .setFooter({ text: "Editor's Hideout XP Ledger • Chat more to level up!" })
      .setTimestamp();

    await interaction.reply({ embeds: [rankEmbed] });
  },
};
