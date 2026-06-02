const { 
  EmbedBuilder, 
  ActionRowBuilder, 
  ButtonBuilder, 
  ButtonStyle, 
  ChannelType, 
  PermissionFlagsBits,
  TextInputBuilder,
  TextInputStyle,
  ModalBuilder
} = require('discord.js');
const fs = require('fs');
const path = require('path');

module.exports = {
  name: 'interactionCreate',
  async execute(interaction, client) {
    // ----------------------------------------------------
    // 1. SLASH COMMANDS HANDLER
    // ----------------------------------------------------
    if (interaction.isChatInputCommand()) {
      const command = client.commands.get(interaction.commandName);

      if (!command) {
        console.warn(`[Command Warning] Command "${interaction.commandName}" was triggered but not found in client.commands.`);
        return;
      }

      try {
        await command.execute(interaction, client);
      } catch (error) {
        console.error(`[Command Error] Error executing command "${interaction.commandName}":`, error);
        
        const errorEmbed = new EmbedBuilder()
          .setColor(client.config.colors.danger)
          .setTitle('⚠️ Execution Error')
          .setDescription('An error occurred while executing this command. Please contact server administration.')
          .setTimestamp();

        if (interaction.replied || interaction.deferred) {
          await interaction.followUp({ embeds: [errorEmbed], ephemeral: true }).catch(() => {});
        } else {
          await interaction.reply({ embeds: [errorEmbed], ephemeral: true }).catch(() => {});
        }
      }
    }

    // ----------------------------------------------------
    // 2. BUTTON INTERACTIONS HANDLER (Tickets & Polls)
    // ----------------------------------------------------
    else if (interaction.isButton()) {
      const customId = interaction.customId;

      // --- OPEN TICKET BUTTON ---
      if (customId === 'open_ticket') {
        // Create modal to ask for the ticket reason
        const modal = new ModalBuilder()
          .setCustomId('ticket_creation_modal')
          .setTitle('Open Support Ticket');

        const reasonInput = new TextInputBuilder()
          .setCustomId('ticket_reason')
          .setLabel("What is the reason for this ticket?")
          .setStyle(TextInputStyle.Paragraph)
          .setPlaceholder("Please describe your question or issue in detail...")
          .setRequired(true)
          .setMinLength(5)
          .setMaxLength(500);

        const actionRow = new ActionRowBuilder().addComponents(reasonInput);
        modal.addComponents(actionRow);

        await interaction.showModal(modal);
      }

      // --- CLOSE TICKET BUTTON ---
      else if (customId === 'close_ticket') {
        // We will defer reply to prevent timeouts
        await interaction.deferReply();

        const channel = interaction.channel;
        
        // Double check this is indeed a ticket channel
        if (!channel.name.startsWith('ticket-')) {
          return interaction.editReply({ 
            content: '❌ This command can only be used inside a ticket channel.', 
            ephemeral: true 
          });
        }

        const closingEmbed = new EmbedBuilder()
          .setColor(client.config.colors.warning)
          .setTitle('🔒 Ticket Closing')
          .setDescription('This support ticket is closing in 5 seconds. Log data is being saved.')
          .setTimestamp();

        await interaction.editReply({ embeds: [closingEmbed] });

        // Generate simple ticket history transcript/logs
        try {
          const messages = await channel.messages.fetch({ limit: 100 });
          const transcript = messages.reverse().map(m => `[${m.createdAt.toISOString()}] ${m.author.tag}: ${m.content}`).join('\n');
          
          // Send transcript log to log channel if defined
          const logChannelId = client.config.defaultSettings.logChannelId;
          if (logChannelId) {
            const logChannel = client.channels.cache.get(logChannelId);
            if (logChannel) {
              const logEmbed = new EmbedBuilder()
                .setColor(client.config.colors.neutral)
                .setTitle('🎫 Ticket Closed')
                .addFields(
                  { name: 'Ticket Name', value: channel.name, inline: true },
                  { name: 'Closed By', value: interaction.user.tag, inline: true }
                )
                .setTimestamp();
              
              // Attachment
              const buffer = Buffer.from(transcript, 'utf-8');
              await logChannel.send({ 
                embeds: [logEmbed], 
                files: [{ attachment: buffer, name: `${channel.name}-transcript.txt` }] 
              });
            }
          }
        } catch (logErr) {
          console.error('[Ticket Logs] Failed to create or send ticket transcript:', logErr);
        }

        // Delete the channel after 5 seconds
        setTimeout(async () => {
          await channel.delete().catch(err => console.error('[Ticket Delete] Failed to delete ticket channel:', err));
        }, 5000);
      }

      // --- POLL VOTE BUTTONS ---
      else if (customId.startsWith('poll_vote_')) {
        // Defer reply to prevent timeouts
        await interaction.deferUpdate();

        const optionIndex = parseInt(customId.split('_')[2]);
        const message = interaction.message;
        
        if (!message.embeds || message.embeds.length === 0) return;

        const embed = message.embeds[0];
        const fields = [...embed.fields];
        
        // Simple client-side vote checking using local in-memory store 
        // to prevent double votes per message (ideal for standard premium setups)
        if (!client.pollVotes) client.pollVotes = new Map();
        const pollId = message.id;
        if (!client.pollVotes.has(pollId)) {
          client.pollVotes.set(pollId, new Map()); // UserID -> OptionIndex
        }

        const votesMap = client.pollVotes.get(pollId);
        const userId = interaction.user.id;

        if (votesMap.has(userId)) {
          const previousVote = votesMap.get(userId);
          if (previousVote === optionIndex) {
            // Clicking the same option again removes the vote
            votesMap.delete(userId);
          } else {
            // Clicking another option changes the vote
            votesMap.set(userId, optionIndex);
          }
        } else {
          // New vote
          votesMap.set(userId, optionIndex);
        }

        // Re-calculate percentages
        const totalVotes = votesMap.size;
        const voteCounts = Array(fields.length).fill(0);
        
        votesMap.forEach((voteIndex) => {
          if (voteCounts[voteIndex] !== undefined) {
            voteCounts[voteIndex]++;
          }
        });

        // Generate beautiful percentage progress bars
        const updatedFields = fields.map((field, idx) => {
          const count = voteCounts[idx];
          const pct = totalVotes > 0 ? Math.round((count / totalVotes) * 100) : 0;
          
          // Progress bar drawing
          const barLength = 10;
          const filledLength = Math.round((pct / 100) * barLength);
          const bar = '🟩'.repeat(filledLength) + '⬜'.repeat(barLength - filledLength);
          
          // Original option text (extract from the current title)
          const optionText = field.name.replace(/^[0-9]+\.\s+/, '');
          
          return {
            name: `${idx + 1}. ${optionText}`,
            value: `${bar} **${pct}%** (${count} votes)`,
            inline: false
          };
        });

        const newEmbed = EmbedBuilder.from(embed)
          .setFields(updatedFields)
          .setFooter({ text: `Total Votes: ${totalVotes} • Interactive Poll` });

        await message.edit({ embeds: [newEmbed] });
      }

      // --- SELF ASSIGN ROLE BUTTONS ---
      else if (customId.startsWith('role_toggle_')) {
        await interaction.deferReply({ ephemeral: true });

        const roleId = customId.split('_')[2];
        const guild = interaction.guild;
        const member = interaction.member;
        const role = guild.roles.cache.get(roleId);

        if (!role) {
          return interaction.editReply({ content: '❌ Could not find that role in this server.' });
        }

        // Check hierarchy
        if (role.position >= guild.members.me.roles.highest.position) {
          return interaction.editReply({ 
            content: '❌ I cannot assign this role because it is positioned higher than or equal to my highest role in the server settings hierarchy.' 
          });
        }

        try {
          if (member.roles.cache.has(roleId)) {
            await member.roles.remove(role);
            await interaction.editReply({ content: `✅ Role **${role.name}** has been removed from your profile.` });
          } else {
            await member.roles.add(role);
            await interaction.editReply({ content: `✅ Role **${role.name}** has been successfully added to your profile!` });
          }
        } catch (err) {
          console.error('[Role Toggle Error] Failed to change user role:', err);
          await interaction.editReply({ content: '❌ Failed to update your roles. Please contact an administrator.' });
        }
      }

      // --- CLAIM REQUEST BUTTON ---
      else if (customId.startsWith('request_claim_')) {
        const hasStaffPermission = interaction.member.permissions.has(PermissionFlagsBits.ManageMessages);
        if (!hasStaffPermission) {
          return interaction.reply({ content: '❌ Only staff members can claim rendering requests!', ephemeral: true });
        }

        await interaction.deferUpdate();

        const requestId = customId.split('_')[2];
        const message = interaction.message;
        const embed = message.embeds[0];

        // Clone current fields and update status field (field index 4)
        const fields = [...embed.fields];
        fields[4] = { name: '⚡ Status', value: `🛠️ **Claimed by ${interaction.user}**`, inline: true };

        const updatedEmbed = EmbedBuilder.from(embed)
          .setColor(client.config.colors.warning)
          .setFields(fields);

        // Buttons row
        const row = new ActionRowBuilder().addComponents(
          new ButtonBuilder()
            .setCustomId(`request_complete_${requestId}`)
            .setLabel('Complete Request')
            .setEmoji('✅')
            .setStyle(ButtonStyle.Primary),
          new ButtonBuilder()
            .setCustomId(`request_cancel_${requestId}`)
            .setLabel('Cancel Claim')
            .setStyle(ButtonStyle.Secondary)
        );

        await message.edit({ embeds: [updatedEmbed], components: [row] });
      }

      // --- CANCEL CLAIM BUTTON ---
      else if (customId.startsWith('request_cancel_')) {
        const hasStaffPermission = interaction.member.permissions.has(PermissionFlagsBits.ManageMessages);
        if (!hasStaffPermission) {
          return interaction.reply({ content: '❌ Only staff members can manage rendering requests!', ephemeral: true });
        }

        await interaction.deferUpdate();

        const requestId = customId.split('_')[2];
        const message = interaction.message;
        const embed = message.embeds[0];

        const fields = [...embed.fields];
        fields[4] = { name: '⚡ Status', value: '⏳ **Pending Staff Claim**', inline: true };

        const updatedEmbed = EmbedBuilder.from(embed)
          .setColor(client.config.colors.primary)
          .setFields(fields);

        const row = new ActionRowBuilder().addComponents(
          new ButtonBuilder()
            .setCustomId(`request_claim_${requestId}`)
            .setLabel('Claim Request')
            .setEmoji('🛠️')
            .setStyle(ButtonStyle.Success),
          new ButtonBuilder()
            .setCustomId(`request_deny_${requestId}`)
            .setLabel('Deny')
            .setEmoji('❌')
            .setStyle(ButtonStyle.Danger)
        );

        await message.edit({ embeds: [updatedEmbed], components: [row] });
      }

      // --- DENY REQUEST BUTTON ---
      else if (customId.startsWith('request_deny_')) {
        const hasStaffPermission = interaction.member.permissions.has(PermissionFlagsBits.ManageMessages);
        if (!hasStaffPermission) {
          return interaction.reply({ content: '❌ Only staff members can deny rendering requests!', ephemeral: true });
        }

        await interaction.deferUpdate();

        const requestId = customId.split('_')[2];
        const message = interaction.message;
        const embed = message.embeds[0];

        const fields = [...embed.fields];
        fields[4] = { name: '⚡ Status', value: `❌ **Denied by ${interaction.user}**`, inline: true };

        const updatedEmbed = EmbedBuilder.from(embed)
          .setColor(client.config.colors.danger)
          .setFields(fields);

        // Notify user via DM
        try {
          const requesterIdMatch = fields[3].value.match(/\((\d+)\)/);
          if (requesterIdMatch) {
            const requesterId = requesterIdMatch[1];
            const requester = await interaction.guild.members.fetch(requesterId);
            if (requester) {
              const dmEmbed = new EmbedBuilder()
                .setColor(client.config.colors.danger)
                .setDescription(`❌ **Request Denied** in **${interaction.guild.name}**\nYour flow frame request for clip \`${fields[0].value}\` has been declined by staff.`);
              await requester.send({ embeds: [dmEmbed] }).catch(() => {});
            }
          }
        } catch (e) {
          console.error('[Request DM Error]', e);
        }

        await message.edit({ embeds: [updatedEmbed], components: [] }); // Remove buttons
      }

      // --- COMPLETE REQUEST BUTTON (SHOWS MODAL) ---
      else if (customId.startsWith('request_complete_')) {
        const hasStaffPermission = interaction.member.permissions.has(PermissionFlagsBits.ManageMessages);
        if (!hasStaffPermission) {
          return interaction.reply({ content: '❌ Only staff members can complete rendering requests!', ephemeral: true });
        }

        const requestId = customId.split('_')[2];

        // Launch Completion Modal
        const modal = new ModalBuilder()
          .setCustomId(`request_completion_modal_${requestId}`)
          .setTitle('Complete Rendering Request');

        const linkInput = new TextInputBuilder()
          .setCustomId('request_download_link')
          .setLabel("What is the completed clip download link?")
          .setStyle(TextInputStyle.Short)
          .setPlaceholder("Paste Mega, GDrive, Pixeldrain or Mediafire link...")
          .setRequired(true);

        const actionRow = new ActionRowBuilder().addComponents(linkInput);
        modal.addComponents(actionRow);

        await interaction.showModal(modal);
      }
    }

    // ----------------------------------------------------
    // 3. MODAL SUBMISSIONS HANDLER (Ticket Creation)
    // ----------------------------------------------------
    else if (interaction.isModalSubmit()) {
      if (interaction.customId === 'ticket_creation_modal') {
        await interaction.deferReply({ ephemeral: true });

        const reason = interaction.fields.getTextInputValue('ticket_reason');
        const guild = interaction.guild;
        const member = interaction.member;

        // Configuration fallbacks
        const staffRoleId = client.config.defaultSettings.ticketStaffRoleId;
        const categoryId = client.config.defaultSettings.ticketCategoryId;

        // Resolve staff role or find default 'Staff' / 'Moderator' roles
        let staffRole = staffRoleId ? guild.roles.cache.get(staffRoleId) : null;
        if (!staffRole) {
          staffRole = guild.roles.cache.find(r => r.name.toLowerCase() === 'staff' || r.name.toLowerCase() === 'moderator');
        }

        // Build permissions for the ticket channel
        const permissionOverwrites = [
          {
            id: guild.roles.everyone.id,
            deny: [PermissionFlagsBits.ViewChannel] // Block channel visibility to public
          },
          {
            id: member.id,
            allow: [
              PermissionFlagsBits.ViewChannel,
              PermissionFlagsBits.SendMessages,
              PermissionFlagsBits.ReadMessageHistory,
              PermissionFlagsBits.AttachFiles,
              PermissionFlagsBits.EmbedLinks
            ]
          },
          {
            id: guild.members.me.id, // Explicitly guarantee bot access to avoid lockouts
            allow: [
              PermissionFlagsBits.ViewChannel,
              PermissionFlagsBits.SendMessages,
              PermissionFlagsBits.ReadMessageHistory,
              PermissionFlagsBits.ManageChannels,
              PermissionFlagsBits.EmbedLinks,
              PermissionFlagsBits.AttachFiles
            ]
          }
        ];

        // Give access to the staff role if found
        if (staffRole) {
          permissionOverwrites.push({
            id: staffRole.id,
            allow: [
              PermissionFlagsBits.ViewChannel,
              PermissionFlagsBits.SendMessages,
              PermissionFlagsBits.ReadMessageHistory,
              PermissionFlagsBits.ManageMessages,
              PermissionFlagsBits.EmbedLinks,
              PermissionFlagsBits.AttachFiles
            ]
          });
        }

        // Try to create the channel under the category if provided
        try {
          const ticketChannel = await guild.channels.create({
            name: `ticket-${member.user.username.toLowerCase().substring(0, 15)}`,
            type: ChannelType.GuildText,
            parent: categoryId || null,
            permissionOverwrites: permissionOverwrites
          });

          // Send welcome instructions embed in the ticket channel
          const ticketWelcomeEmbed = new EmbedBuilder()
            .setColor(client.config.colors.primary)
            .setTitle(`🎫 Ticket Opened - Support Desk`)
            .setDescription(`Hello ${member.user}, thank you for reaching out. Support staff has been notified.\n\n**Reason for ticket:**\n\`\`\`${reason}\`\`\``)
            .addFields(
              { name: 'Staff Support', value: staffRole ? `${staffRole}` : 'Staff role not configured, administrators will assist shortly.', inline: true },
              { name: 'Instructions', value: 'Explain your concern thoroughly. Click the lock button below when this inquiry is fully resolved.', inline: true }
            )
            .setTimestamp();

          const ticketCloseRow = new ActionRowBuilder().addComponents(
            new ButtonBuilder()
              .setCustomId('close_ticket')
              .setLabel('Close Ticket')
              .setEmoji('🔒')
              .setStyle(ButtonStyle.Danger)
          );

          await ticketChannel.send({ 
            content: `${member.user} ${staffRole ? staffRole : ''}`, 
            embeds: [ticketWelcomeEmbed], 
            components: [ticketCloseRow] 
          });

          // Acknowledge ticket opened to the user
          const successEmbed = new EmbedBuilder()
            .setColor(client.config.colors.success)
            .setDescription(`✅ Support ticket successfully created: ${ticketChannel}`);

          await interaction.editReply({ embeds: [successEmbed] });

        } catch (err) {
          console.error('[Ticket Creation Error] Failed to generate ticket channel:', err);
          await interaction.editReply({ 
            content: '❌ Failed to create ticket channel. Make sure the bot has `Manage Channels` permission.', 
            ephemeral: true 
          });
        }
      }

      // --- REQUEST COMPLETION MODAL SUBMIT ---
      else if (interaction.customId.startsWith('request_completion_modal_')) {
        await interaction.deferReply({ ephemeral: true });

        const requestId = interaction.customId.split('_')[3];
        const downloadLink = interaction.fields.getTextInputValue('request_download_link');
        const message = interaction.message;
        const embed = message.embeds[0];

        const fields = [...embed.fields];
        fields[4] = { name: '⚡ Status', value: `✅ **Completed by ${interaction.user}**`, inline: true };

        const updatedEmbed = EmbedBuilder.from(embed)
          .setColor(client.config.colors.success)
          .setFields(fields);

        // Redirect Link Button for completed download
        const row = new ActionRowBuilder().addComponents(
          new ButtonBuilder()
            .setLabel('Download Completed Clip')
            .setEmoji('💾')
            .setStyle(ButtonStyle.Link)
            .setURL(downloadLink)
        );

        // Edit request board
        await message.edit({ embeds: [updatedEmbed], components: [row] });

        // DM the original requester
        try {
          const requesterIdMatch = fields[3].value.match(/\((\d+)\)/);
          if (requesterIdMatch) {
            const requesterId = requesterIdMatch[1];
            const requester = await interaction.guild.members.fetch(requesterId);
            if (requester) {
              const dmEmbed = new EmbedBuilder()
                .setColor(client.config.colors.success)
                .setTitle('🎉 Request Completed!')
                .setDescription(`Your flow frame rendering request for **${fields[0].value}** has been successfully completed by **${interaction.user.tag}**!\n\nClick the download link below to fetch your rendered clip.`);
              
              const dmRow = new ActionRowBuilder().addComponents(
                new ButtonBuilder()
                  .setLabel('Download Clip')
                  .setEmoji('💾')
                  .setStyle(ButtonStyle.Link)
                  .setURL(downloadLink)
              );

              await requester.send({ embeds: [dmEmbed], components: [dmRow] }).catch(() => {});
            }
          }
        } catch (e) {
          console.error('[Request DM Complete Error]', e);
        }

        await interaction.editReply({ content: '✅ Request successfully marked as completed. The requester has been notified via DM!' });
      }
    }
  },
};
