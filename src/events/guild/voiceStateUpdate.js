const { ChannelType, PermissionFlagsBits } = require('discord.js');

module.exports = {
  name: 'voiceStateUpdate',
  once: false,
  async execute(oldState, newState, client) {
    const { guild, member } = newState;

    const joinToCreateId = client.config.defaultSettings.joinToCreateChannelId;
    if (!joinToCreateId) return;

    // Ensure memory tracker exists on client
    if (!client.dynamicChannels) {
      client.dynamicChannels = new Set();
    }

    // ----------------------------------------------------
    // CASE A: User joined the dedicated "Join-to-Create" VC
    // ----------------------------------------------------
    if (newState.channelId === joinToCreateId) {
      try {
        const triggerChannel = guild.channels.cache.get(joinToCreateId);
        const categoryId = triggerChannel ? triggerChannel.parentId : null;

        // Create new temporary channel under the same category with customized rights
        const tempChannel = await guild.channels.create({
          name: `🔊 ${member.user.username}'s Room`,
          type: ChannelType.GuildVoice,
          parent: categoryId || null,
          userLimit: 99, // limit to 99 members
          permissionOverwrites: [
            {
              id: member.id, // Grant room creator full room ownership & moderation rights
              allow: [
                PermissionFlagsBits.ViewChannel,
                PermissionFlagsBits.Connect,
                PermissionFlagsBits.Speak,
                PermissionFlagsBits.ManageChannels,
                PermissionFlagsBits.MuteMembers,
                PermissionFlagsBits.DeafenMembers,
                PermissionFlagsBits.MoveMembers
              ]
            },
            {
              id: guild.members.me.id, // Guarantee bot management permissions
              allow: [
                PermissionFlagsBits.ViewChannel,
                PermissionFlagsBits.Connect,
                PermissionFlagsBits.ManageChannels,
                PermissionFlagsBits.MoveMembers
              ]
            }
          ]
        });

        // Add to active set
        client.dynamicChannels.add(tempChannel.id);

        // Move user into the new temporary room
        await member.voice.setChannel(tempChannel);
        console.log(`[Dynamic VC] Created room "${tempChannel.name}" for ${member.user.tag}`);

      } catch (err) {
        console.error('[Dynamic VC Error] Failed to configure voice channel:', err);
      }
    }

    // ----------------------------------------------------
    // CASE B: User left or switched channels (clean up empty rooms)
    // ----------------------------------------------------
    if (oldState.channelId && oldState.channelId !== newState.channelId) {
      const oldChannelId = oldState.channelId;

      if (client.dynamicChannels.has(oldChannelId)) {
        const oldChannel = guild.channels.cache.get(oldChannelId);
        
        if (oldChannel) {
          // If the channel is empty, delete it
          if (oldChannel.members.size === 0) {
            try {
              await oldChannel.delete();
              client.dynamicChannels.delete(oldChannelId);
              console.log(`[Dynamic VC] Deleted empty voice channel: ${oldChannel.name}`);
            } catch (err) {
              console.error('[Dynamic VC Error] Failed to delete empty channel:', err);
            }
          }
        } else {
          // Clean up if it was deleted manually or missing from cache
          client.dynamicChannels.delete(oldChannelId);
        }
      }
    }
  },
};
