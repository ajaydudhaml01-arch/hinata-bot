const { SlashCommandBuilder, EmbedBuilder, PermissionFlagsBits } = require('discord.js');
const fs = require('fs');
const path = require('path');

const warningsFilePath = path.join(__dirname, '..', '..', '..', 'data', 'warnings.json');

// Helper function to read warnings from file
function readWarnings() {
  try {
    if (!fs.existsSync(warningsFilePath)) {
      return {};
    }
    const data = fs.readFileSync(warningsFilePath, 'utf8');
    return JSON.parse(data || '{}');
  } catch (err) {
    console.error('[Warn DB] Failed to read warnings database:', err);
    return {};
  }
}

// Helper function to write warnings to file
function writeWarnings(data) {
  try {
    fs.writeFileSync(warningsFilePath, JSON.stringify(data, null, 2), 'utf8');
  } catch (err) {
    console.error('[Warn DB] Failed to write warnings database:', err);
  }
}

module.exports = {
  data: new SlashCommandBuilder()
    .setName('warn')
    .setDescription('Manage user warnings.')
    .setDefaultMemberPermissions(PermissionFlagsBits.ModerateMembers)
    .setDMPermission(false)
    .addSubcommand(subcommand =>
      subcommand
        .setName('add')
        .setDescription('Issues a warning to a member.')
        .addUserOption(option => option.setName('target').setDescription('The member to warn.').setRequired(true))
        .addStringOption(option => option.setName('details').setDescription('Detailed reason for the warning.').setRequired(true))
    )
    .addSubcommand(subcommand =>
      subcommand
        .setName('list')
        .setDescription('Displays warning history for a member.')
        .addUserOption(option => option.setName('target').setDescription('The member whose warnings you want to view.').setRequired(true))
    )
    .addSubcommand(subcommand =>
      subcommand
        .setName('clear')
        .setDescription('Clears all warnings from a member.')
        .addUserOption(option => option.setName('target').setDescription('The member whose warnings you want to wipe.').setRequired(true))
    ),
  async execute(interaction, client) {
    const subcommand = interaction.options.getSubcommand();
    const targetUser = interaction.options.getUser('target');
    const guildId = interaction.guild.id;

    const db = readWarnings();
    if (!db[guildId]) db[guildId] = {};
    if (!db[guildId][targetUser.id]) db[guildId][targetUser.id] = [];

    // --- ADD SUBCOMMAND ---
    if (subcommand === 'add') {
      const details = interaction.options.getString('details');
      const moderator = interaction.user;

      const newWarning = {
        id: Date.now().toString(),
        reason: details,
        moderatorId: moderator.id,
        timestamp: Date.now()
      };

      db[guildId][targetUser.id].push(newWarning);
      writeWarnings(db);

      const warningCount = db[guildId][targetUser.id].length;

      // DM warning details to user
      const dmEmbed = new EmbedBuilder()
        .setColor(client.config.colors.danger)
        .setTitle(`🛡️ Warning issued in ${interaction.guild.name}`)
        .setDescription(`You have received an official warning in **${interaction.guild.name}**.\n\n**Reason:** ${details}\n**Total Warnings:** ${warningCount}`)
        .setTimestamp();

      const member = await interaction.guild.members.fetch(targetUser.id).catch(() => null);
      if (member) {
        await member.send({ embeds: [dmEmbed] }).catch(() => {
          console.log(`[Warn Command] Could not send direct message to ${targetUser.tag}.`);
        });
      }

      const successEmbed = new EmbedBuilder()
        .setColor(client.config.colors.success)
        .setTitle('🛡️ Warning Logged')
        .setDescription(`Successfully warned **${targetUser.tag}**.`)
        .addFields(
          { name: 'Target User', value: `${targetUser} (\`${targetUser.id}\`)`, inline: true },
          { name: 'Warned By', value: `${moderator}`, inline: true },
          { name: 'Total Active Warnings', value: `\`${warningCount}\``, inline: true },
          { name: 'Reason', value: `\`\`\`${details}\`\`\`` }
        )
        .setTimestamp();

      await interaction.reply({ embeds: [successEmbed] });

      // Send Mod Log if channel exists
      const logChannelId = client.config.defaultSettings.logChannelId;
      if (logChannelId) {
        const logChannel = interaction.guild.channels.cache.get(logChannelId);
        if (logChannel) {
          await logChannel.send({ embeds: [successEmbed] });
        }
      }
    }

    // --- LIST SUBCOMMAND ---
    else if (subcommand === 'list') {
      const userWarnings = db[guildId][targetUser.id];

      if (!userWarnings || userWarnings.length === 0) {
        return interaction.reply({ 
          embeds: [
            new EmbedBuilder()
              .setColor(client.config.colors.success)
              .setDescription(`✅ **${targetUser.tag}** has clean history! 0 active warnings.`)
          ] 
        });
      }

      const listEmbed = new EmbedBuilder()
        .setColor(client.config.colors.warning)
        .setTitle(`🛡️ Warning Logs - ${targetUser.tag}`)
        .setDescription(`Displaying active warnings issued to ${targetUser} in this guild.`)
        .setThumbnail(targetUser.displayAvatarURL())
        .setTimestamp();

      userWarnings.forEach((warn, index) => {
        listEmbed.addFields({
          name: `Warning #${index + 1} (ID: ${warn.id})`,
          value: `**Reason:** ${warn.reason}\n**Issued By:** <@${warn.moderatorId}>\n**Date:** <t:${Math.floor(warn.timestamp / 1000)}:f>`,
          inline: false
        });
      });

      await interaction.reply({ embeds: [listEmbed] });
    }

    // --- CLEAR SUBCOMMAND ---
    else if (subcommand === 'clear') {
      const warningsCount = db[guildId][targetUser.id]?.length || 0;

      if (warningsCount === 0) {
        return interaction.reply({ 
          content: `❌ **${targetUser.tag}** already has 0 active warnings.`, 
          ephemeral: true 
        });
      }

      db[guildId][targetUser.id] = [];
      writeWarnings(db);

      const clearEmbed = new EmbedBuilder()
        .setColor(client.config.colors.success)
        .setTitle('🧼 Warnings Cleared')
        .setDescription(`Successfully wiped **${warningsCount}** warning records from ${targetUser}.`)
        .setTimestamp();

      await interaction.reply({ embeds: [clearEmbed] });

      // Send Mod Log if channel exists
      const logChannelId = client.config.defaultSettings.logChannelId;
      if (logChannelId) {
        const logChannel = interaction.guild.channels.cache.get(logChannelId);
        if (logChannel) {
          await logChannel.send({ embeds: [clearEmbed] });
        }
      }
    }
  },
};
