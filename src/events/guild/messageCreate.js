const { EmbedBuilder, PermissionFlagsBits } = require('discord.js');
const fs = require('fs');
const path = require('path');

const levelsFilePath = path.join(__dirname, '..', '..', '..', 'data', 'levels.json');
const warningsFilePath = path.join(__dirname, '..', '..', '..', 'data', 'warnings.json');

// --- DATABASE HANDLERS ---
function readJSON(filePath) {
  try {
    if (!fs.existsSync(filePath)) return {};
    const data = fs.readFileSync(filePath, 'utf8');
    return JSON.parse(data || '{}');
  } catch (err) {
    console.error(`[DB Error] Failed to read ${filePath}:`, err);
    return {};
  }
}

function writeJSON(filePath, data) {
  try {
    fs.writeFileSync(filePath, JSON.stringify(data, null, 2), 'utf8');
  } catch (err) {
    console.error(`[DB Error] Failed to write ${filePath}:`, err);
  }
}

module.exports = {
  name: 'messageCreate',
  once: false,
  async execute(message, client) {
    // 1. Safeguard checks
    if (message.author.bot || !message.guild) return;

    const { guild, author, member, channel } = message;

    // Bypass staff for AutoMod checks
    const isStaff = member.permissions.has(PermissionFlagsBits.ManageMessages) || 
                    member.permissions.has(PermissionFlagsBits.Administrator);

    // ----------------------------------------------------
    // 2. AUTOMATED MODERATION (AutoMod & Anti-Spam)
    // ----------------------------------------------------
    if (!isStaff) {
      const contentLower = message.content.toLowerCase();

      // --- A. INVITE LINK FILTER ---
      const hasInvite = /(discord\.gg\/|discord\.com\/invite\/)/i.test(message.content);
      if (hasInvite) {
        await message.delete().catch(() => {});

        // Issue warning automatically in Warnings DB
        const warnDb = readJSON(warningsFilePath);
        if (!warnDb[guild.id]) warnDb[guild.id] = {};
        if (!warnDb[guild.id][author.id]) warnDb[guild.id][author.id] = [];

        const newWarning = {
          id: Date.now().toString(),
          reason: "AutoMod: Advertising discord invite links.",
          moderatorId: client.user.id,
          timestamp: Date.now()
        };
        warnDb[guild.id][author.id].push(newWarning);
        writeJSON(warningsFilePath, warnDb);

        const warnCount = warnDb[guild.id][author.id].length;

        // DM user
        const dmEmbed = new EmbedBuilder()
          .setColor(client.config.colors.danger)
          .setDescription(`⚠️ **Warning Issued** in **${guild.name}**\n\nInvite advertising is strictly forbidden.\n**Total Warnings:** ${warnCount}`)
          .setTimestamp();
        await author.send({ embeds: [dmEmbed] }).catch(() => {});

        // Warning Alert in Channel
        const channelAlert = await channel.send({
          content: `❌ ${author}, invite links are not permitted here! Warning registered. (\`${warnCount}\` total)`
        });
        setTimeout(() => channelAlert.delete().catch(() => {}), 5000);

        // Log to Mod Logs
        const logChannelId = client.config.defaultSettings.logChannelId;
        if (logChannelId) {
          const logChannel = guild.channels.cache.get(logChannelId);
          if (logChannel) {
            const logEmbed = new EmbedBuilder()
              .setColor(client.config.colors.danger)
              .setTitle('🛡️ AutoMod: Invite Deleted')
              .addFields(
                { name: 'Offender', value: `${author} (\`${author.id}\`)`, inline: true },
                { name: 'Channel', value: `${channel}`, inline: true },
                { name: 'Warn Count', value: `\`${warnCount}\``, inline: true }
              )
              .setTimestamp();
            await logChannel.send({ embeds: [logEmbed] });
          }
        }
        return; // Stop event execution
      }

      // --- B. BLOCKED KEYWORDS FILTER ---
      const blockedWords = client.config.defaultSettings.blockedWords || [];
      const hasBlockedWord = blockedWords.some(word => contentLower.includes(word));
      if (hasBlockedWord) {
        await message.delete().catch(() => {});

        // Issue warning automatically
        const warnDb = readJSON(warningsFilePath);
        if (!warnDb[guild.id]) warnDb[guild.id] = {};
        if (!warnDb[guild.id][author.id]) warnDb[guild.id][author.id] = [];

        const newWarning = {
          id: Date.now().toString(),
          reason: "AutoMod: Sending blacklisted words/scams.",
          moderatorId: client.user.id,
          timestamp: Date.now()
        };
        warnDb[guild.id][author.id].push(newWarning);
        writeJSON(warningsFilePath, warnDb);

        const warnCount = warnDb[guild.id][author.id].length;

        // DM user
        const dmEmbed = new EmbedBuilder()
          .setColor(client.config.colors.danger)
          .setDescription(`⚠️ **Warning Issued** in **${guild.name}**\n\nYour message contained blacklisted words or phrases.\n**Total Warnings:** ${warnCount}`)
          .setTimestamp();
        await author.send({ embeds: [dmEmbed] }).catch(() => {});

        // Warning Alert in Channel
        const channelAlert = await channel.send({
          content: `❌ ${author}, your message was deleted as it contained prohibited text! Warning registered.`
        });
        setTimeout(() => channelAlert.delete().catch(() => {}), 5000);

        // Log to Mod Logs
        const logChannelId = client.config.defaultSettings.logChannelId;
        if (logChannelId) {
          const logChannel = guild.channels.cache.get(logChannelId);
          if (logChannel) {
            const logEmbed = new EmbedBuilder()
              .setColor(client.config.colors.danger)
              .setTitle('🛡️ AutoMod: Prohibited Word Filtered')
              .addFields(
                { name: 'Offender', value: `${author} (\`${author.id}\`)`, inline: true },
                { name: 'Channel', value: `${channel}`, inline: true },
                { name: 'Message Content snippet', value: `\`\`\`${message.content.substring(0, 100)}\`\`\`` }
              )
              .setTimestamp();
            await logChannel.send({ embeds: [logEmbed] });
          }
        }
        return; // Stop event execution
      }

      // --- C. ANTI-SPAM SYSTEM ---
      if (!client.spamTracker) client.spamTracker = new Map();
      const now = Date.now();
      
      if (!client.spamTracker.has(author.id)) {
        client.spamTracker.set(author.id, []);
      }

      const userTimestamps = client.spamTracker.get(author.id);
      userTimestamps.push(now);

      // Keep only timestamps from the last 4 seconds
      const recentTimestamps = userTimestamps.filter(t => now - t < 4000);
      client.spamTracker.set(author.id, recentTimestamps);

      if (recentTimestamps.length >= 5) {
        await message.delete().catch(() => {});

        // Timeout user for 5 minutes
        if (member.moderatable) {
          await member.timeout(300000, "AutoMod: Message Spamming").catch(() => {});
          
          const channelAlert = await channel.send({
            content: `🤫 ${author} has been temporarily muted for 5 minutes due to message spamming.`
          });
          setTimeout(() => channelAlert.delete().catch(() => {}), 8000);

          // Log to Mod Logs
          const logChannelId = client.config.defaultSettings.logChannelId;
          if (logChannelId) {
            const logChannel = guild.channels.cache.get(logChannelId);
            if (logChannel) {
              const logEmbed = new EmbedBuilder()
                .setColor(client.config.colors.warning)
                .setTitle('🤫 AutoMod: Spammer Muted')
                .addFields(
                  { name: 'User Muted', value: `${author} (\`${author.id}\`)`, inline: true },
                  { name: 'Channel', value: `${channel}`, inline: true },
                  { name: 'Duration', value: '5 Minutes', inline: true }
                )
                .setTimestamp();
              await logChannel.send({ embeds: [logEmbed] });
            }
          }
        }
        return; // Stop event execution
      }

      // --- D. MALWARE & EXECUTABLE LINK SCANNER ---
      const dangerousLinkRegex = /(mega\.nz|mediafire\.com|drive\.google\.com|dropbox\.com|anonfiles\.com|pixeldrain\.com).*(?:\.exe|\.scr|\.bat|\.vbs|\.msi|\.cmd|\.pif)/i;
      const hasDangerousLink = dangerousLinkRegex.test(message.content);
      const hasDangerousAttachment = message.attachments.some(att => /(?:\.exe|\.scr|\.bat|\.vbs|\.msi|\.cmd|\.pif)$/i.test(att.name));

      if (hasDangerousLink || hasDangerousAttachment) {
        await message.delete().catch(() => {});

        // Issue warning automatically
        const warnDb = readJSON(warningsFilePath);
        if (!warnDb[guild.id]) warnDb[guild.id] = {};
        if (!warnDb[guild.id][author.id]) warnDb[guild.id][author.id] = [];

        const newWarning = {
          id: Date.now().toString(),
          reason: "AutoMod: Sharing prohibited executable files/scripts.",
          moderatorId: client.user.id,
          timestamp: Date.now()
        };
        warnDb[guild.id][author.id].push(newWarning);
        writeJSON(warningsFilePath, warnDb);

        const warnCount = warnDb[guild.id][author.id].length;

        // DM user
        const dmEmbed = new EmbedBuilder()
          .setColor(client.config.colors.danger)
          .setDescription(`⚠️ **Security Warning** in **${guild.name}**\n\nSharing executables, installers, or scripts (\`.exe\`, \`.scr\`, \`.bat\`, etc.) is strictly prohibited to keep our editing community safe from malware.\n**Total Warnings:** ${warnCount}`)
          .setTimestamp();
        await author.send({ embeds: [dmEmbed] }).catch(() => {});

        // Channel Alert
        const channelAlert = await channel.send({
          content: `❌ ${author}, download links for software installers, scripts, or executables (\`.exe\`, \`.scr\`, \`.bat\`) are restricted to verified staff to prevent malware! Warning registered.`
        });
        setTimeout(() => channelAlert.delete().catch(() => {}), 8000);

        // Log to Mod Logs
        const logChannelId = client.config.defaultSettings.logChannelId;
        if (logChannelId) {
          const logChannel = guild.channels.cache.get(logChannelId);
          if (logChannel) {
            const logEmbed = new EmbedBuilder()
              .setColor(client.config.colors.danger)
              .setTitle('🚨 Security Alert: Prohibited Executable Blocked')
              .addFields(
                { name: 'Offender', value: `${author} (\`${author.id}\`)`, inline: true },
                { name: 'Channel', value: `${channel}`, inline: true },
                { name: 'Details', value: hasDangerousLink ? 'Dangerous link found in message content.' : 'Prohibited file extension attached.', inline: true },
                { name: 'Message Content snippet', value: `\`\`\`${message.content.substring(0, 200)}\`\`\`` }
              )
              .setTimestamp();
            await logChannel.send({ embeds: [logEmbed] });
          }
        }
        return; // Stop event execution
      }
    }

    // ----------------------------------------------------
    // 3. XP LEVELING SYSTEM
    // ----------------------------------------------------
    if (!client.xpCooldown) client.xpCooldown = new Map();
    const lastXp = client.xpCooldown.get(author.id) || 0;
    const nowTime = Date.now();

    // 60-second cooldown per user to prevent leveling via spamming
    if (nowTime - lastXp >= 60000) {
      client.xpCooldown.set(author.id, nowTime);

      const levelDb = readJSON(levelsFilePath);
      if (!levelDb[guild.id]) levelDb[guild.id] = {};
      if (!levelDb[guild.id][author.id]) {
        levelDb[guild.id][author.id] = { xp: 0, level: 0 };
      }

      const userData = levelDb[guild.id][author.id];
      const xpGained = Math.floor(Math.random() * 11) + 15; // 15 to 25 XP
      userData.xp += xpGained;

      // XP formula: 5 * (level^2) + (50 * level) + 100
      const currentLevel = userData.level;
      const xpNeeded = 5 * Math.pow(currentLevel, 2) + 50 * currentLevel + 100;

      if (userData.xp >= xpNeeded) {
        userData.level++;
        userData.xp = userData.xp - xpNeeded; // Carry over excess XP

        // Send aesthetic level-up card in chat
        const levelUpEmbed = new EmbedBuilder()
          .setColor(client.config.colors.success)
          .setTitle('🎉 Level Up!')
          .setDescription(`Congratulations ${author}! You have advanced to **Level ${userData.level}**!`)
          .setThumbnail(author.displayAvatarURL())
          .setFooter({ text: `Keep active to unlock future milestone roles!` })
          .setTimestamp();

        const levelUpMsg = await channel.send({ embeds: [levelUpEmbed] });
        // Automatically delete level-up notification after 8 seconds to prevent channel clutter
        setTimeout(() => levelUpMsg.delete().catch(() => {}), 10000);

        // --- ONE PIECE MILESTONE ROLES AUTO-CREATION & GRANT SYSTEM ---
        const onePieceTiers = {
          "5": { name: "Super Rookie", color: "#3498DB" },
          "15": { name: "Warlord of the Sea", color: "#F1C40F" },
          "30": { name: "Marine Admiral", color: "#E67E22" },
          "45": { name: "Emperor of the Sea", color: "#9B59B6" },
          "60": { name: "Pirate King", color: "#E74C3C" }
        };

        const milestone = onePieceTiers[userData.level.toString()];
        if (milestone) {
          try {
            // 1. Search if a role with that exact name exists in the server
            let role = guild.roles.cache.find(r => r.name.toLowerCase() === milestone.name.toLowerCase());
            
            // 2. If it doesn't exist, create it automatically!
            if (!role) {
              console.log(`[Level System] Role "${milestone.name}" not found. Auto-creating...`);
              role = await guild.roles.create({
                name: milestone.name,
                color: milestone.color,
                reason: `XP Level Milestone Role Unlocked: Level ${userData.level}`
              });
            }

            // 3. Assign role to the member (checking role hierarchy)
            if (role && guild.members.me.roles.highest.position > role.position) {
              await member.roles.add(role);
              console.log(`[Level System] Assigned One Piece Role "${role.name}" to ${author.tag}`);
              
              // Post unlock embed in chat
              const unlockEmbed = new EmbedBuilder()
                .setColor(milestone.color)
                .setTitle('🏆 One Piece Tier Unlocked!')
                .setDescription(`🎉 ${author} has risen to the rank of **${role.name}** after reaching **Level ${userData.level}**!`)
                .setThumbnail(author.displayAvatarURL())
                .setFooter({ text: "Pirate King quest continues! • Chat to gain power" })
                .setTimestamp();
              
              const unlockMsg = await channel.send({ embeds: [unlockEmbed] });
              setTimeout(() => unlockMsg.delete().catch(() => {}), 15000); // self deletes after 15s to keep chat tidy
            } else {
              console.warn(`[Level System Warning] Cannot assign role "${milestone.name}" due to role hierarchy limitation.`);
            }

          } catch (err) {
            console.error(`[Level System Error] Failed to handle milestone role "${milestone.name}":`, err);
          }
        }
      }

      writeJSON(levelsFilePath, levelDb);
    }
  },
};
