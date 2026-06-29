"""
Discord Integration — connects to Discord to read mentions, channels, DMs and send messages.
"""

import asyncio
import threading
import datetime
from typing import Optional

try:
    import discord
    _discord_available = True
except ImportError:
    discord = None  # type: ignore
    _discord_available = False

_client = None
_loop: Optional[asyncio.AbstractEventLoop] = None
_thread: Optional[threading.Thread] = None


def _check_availability():
    if not _discord_available:
        return False
    return True


if _discord_available:
    class AriaDiscordClient(discord.Client):
        def __init__(self, alert_callback=None, *args, **kwargs):
            intents = discord.Intents.default()
            intents.message_content = True
            intents.guilds = True
            intents.members = True
            super().__init__(intents=intents, *args, **kwargs)
            self.alert_callback = alert_callback
            self.recent_mentions = []
            self.recent_dms = {}  # username -> messages list

        async def on_ready(self):
            pass

        async def on_message(self, message):
            if message.author == self.user:
                return

            is_dm = isinstance(message.channel, discord.DMChannel)
            is_mention = self.user in message.mentions or (message.reference and message.reference.cached_message and message.reference.cached_message.author == self.user)
            
            # Cache DMs
            if is_dm:
                username = message.author.name
                if username not in self.recent_dms:
                    self.recent_dms[username] = []
                self.recent_dms[username].append(message)
                self.recent_dms[username] = self.recent_dms[username][-20:]

            # Cache Mentions
            if is_mention:
                self.recent_mentions.append(message)
                self.recent_mentions = self.recent_mentions[-20:]

            # Trigger proactive alert callback
            if is_mention or is_dm:
                time_str = datetime.datetime.now().strftime("%I:%M %p")
                sender = message.author.name
                server_name = message.guild.name if message.guild else "Direct Message"
                
                if is_dm:
                    msg = f"It's {time_str}, sweetheart~ You got a new DM from {sender}. Want me to read it? ♥"
                else:
                    msg = f"It's {time_str}, sweetheart~ You got mentioned in the {server_name} server by {sender}. Want me to read it? ♥"
                
                if self.alert_callback:
                    self.alert_callback(msg)


def _run_async(coro):
    if not _check_availability():
        return "Discord integration unavailable — discord.py not installed. Run 'pip install discord.py'."
    if _loop is None or _loop.is_closed() or not _loop.is_running():
        return "Error: Discord integration is not running. It may be reconnecting — try again in a moment."
    try:
        future = asyncio.run_coroutine_threadsafe(coro, _loop)
        return future.result(timeout=10)
    except Exception as e:
        return f"Error executing Discord operation: {e}"


# ─── Coroutines ──────────────────────────────────────────────

async def _get_unread_summary():
    if not _client or not _client.is_ready():
        return "Discord client is connecting, sweetheart. Please wait."
    
    summary = []
    # For a bot client, list last 5 active text channels across all guilds
    for guild in _client.guilds:
        channels_active = []
        for channel in guild.text_channels:
            if channel.permissions_for(guild.me).read_messages:
                try:
                    messages = []
                    async for m in channel.history(limit=10):
                        messages.append(m)
                    if messages:
                        channels_active.append((channel, messages))
                except Exception:
                    pass
        
        # Sort by latest message timestamp
        channels_active.sort(key=lambda x: x[1][0].created_at if x[1] else datetime.datetime.min, reverse=True)
        
        for chan, msgs in channels_active[:3]:  # Top 3 active channels per server
            chan_lines = [f"--- #{chan.name} in {guild.name} ---"]
            for m in reversed(msgs):
                time_str = m.created_at.strftime("%H:%M")
                chan_lines.append(f"  [{time_str}] {m.author.name}: {m.content[:50]}")
            summary.append("\n".join(chan_lines))
            
    return "\n\n".join(summary) if summary else "No active channel messages found."


async def _read_channel(server_name: str, channel_name: str, count: int):
    if not _client or not _client.is_ready():
        return "Discord client is not ready."
    
    # Find guild
    guild = discord.utils.get(_client.guilds, name=server_name)
    if not guild:
        # Try case-insensitive search
        guilds = [g for g in _client.guilds if g.name.lower() == server_name.lower()]
        if guilds:
            guild = guilds[0]
        else:
            return f"Error: Server '{server_name}' not found."
            
    # Find channel
    channel = discord.utils.get(guild.text_channels, name=channel_name)
    if not channel:
        channels = [c for c in guild.text_channels if c.name.lower() == channel_name.lower()]
        if channels:
            channel = channels[0]
        else:
            return f"Error: Channel '#{channel_name}' not found in server '{server_name}'."
            
    messages = []
    async for m in channel.history(limit=count):
        messages.append(m)
        
    lines = [f"Last {len(messages)} messages in #{channel.name} ({guild.name}):"]
    for m in reversed(messages):
        time_str = m.created_at.strftime("%I:%M %p")
        lines.append(f"  [{time_str}] {m.author.name}: {m.content}")
    return "\n".join(lines)


async def _send_message(server_name: str, channel_name: str, message: str):
    if not _client or not _client.is_ready():
        return "Discord client is not ready."
    
    guild = discord.utils.get(_client.guilds, name=server_name)
    if not guild:
        guilds = [g for g in _client.guilds if g.name.lower() == server_name.lower()]
        if guilds:
            guild = guilds[0]
        else:
            return f"Error: Server '{server_name}' not found."
            
    channel = discord.utils.get(guild.text_channels, name=channel_name)
    if not channel:
        channels = [c for c in guild.text_channels if c.name.lower() == channel_name.lower()]
        if channels:
            channel = channels[0]
        else:
            return f"Error: Channel '#{channel_name}' not found."
            
    msg = await channel.send(message)
    return f"Success: Message sent to #{channel.name} in server '{guild.name}' (ID: {msg.id})."


async def _check_mentions():
    if not _client or not _client.is_ready():
        return "Discord client is not ready."
    
    # Check client's cached mentions
    lines = ["Recent mentions:"]
    for m in _client.recent_mentions:
        time_str = m.created_at.strftime("%Y-%m-%d %I:%M %p")
        server = m.guild.name if m.guild else "Direct Message"
        lines.append(f"  [{time_str}] {m.author.name} (in #{m.channel.name} on {server}): {m.content}")
        
    return "\n".join(lines) if len(lines) > 1 else "No recent mentions cached."


async def _dm_read(username: str):
    if not _client or not _client.is_ready():
        return "Discord client is not ready."
    
    # Try finding cached DMs
    messages = _client.recent_dms.get(username, [])
    if not messages:
        # Try to find user and fetch
        user = discord.utils.get(_client.users, name=username)
        if not user:
            # Try case-insensitive search
            users = [u for u in _client.users if u.name.lower() == username.lower()]
            if users:
                user = users[0]
        if user:
            try:
                if not user.dm_channel:
                    await user.create_dm()
                async for m in user.dm_channel.history(limit=10):
                    messages.append(m)
                messages.reverse()
            except Exception:
                pass
                
    if not messages:
        return f"No direct messages found with '{username}'."
        
    lines = [f"Direct messages with {username}:"]
    for m in messages:
        time_str = m.created_at.strftime("%I:%M %p")
        lines.append(f"  [{time_str}] {m.author.name}: {m.content}")
    return "\n".join(lines)


async def _dm_send(username: str, message: str):
    if not _client or not _client.is_ready():
        return "Discord client is not ready."
    
    user = discord.utils.get(_client.users, name=username)
    if not user:
        users = [u for u in _client.users if u.name.lower() == username.lower()]
        if users:
            user = users[0]
        else:
            return f"Error: User '{username}' not found."
            
    if not user.dm_channel:
        await user.create_dm()
        
    await user.dm_channel.send(message)
    return f"Success: Direct message sent to '{username}'."


# ─── Synchronous Exporters ───────────────────────────────────

def discord_unread_summary() -> str:
    return _run_async(_get_unread_summary())


def discord_read_channel(server_name: str, channel_name: str, count: int = 10) -> str:
    return _run_async(_read_channel(server_name, channel_name, count))


def discord_send_message(server_name: str, channel_name: str, message: str) -> str:
    return _run_async(_send_message(server_name, channel_name, message))


def discord_check_mentions() -> str:
    return _run_async(_check_mentions())


def discord_dm_read(username: str) -> str:
    return _run_async(_dm_read(username))


def discord_dm_send(username: str, message: str) -> str:
    return _run_async(_dm_send(username, message))


# ─── Server/Channel Browsing ────────────────────────────────

async def _list_servers():
    if not _client or not _client.is_ready():
        return "Discord client is not ready."
    lines = ["Connected servers:"]
    for guild in sorted(_client.guilds, key=lambda g: g.name.lower()):
        lines.append(f"  - {guild.name} ({guild.member_count} members)")
    return "\n".join(lines) if len(lines) > 1 else "No servers found."


async def _list_channels(server_name: str):
    if not _client or not _client.is_ready():
        return "Discord client is not ready."
    guild = discord.utils.get(_client.guilds, name=server_name)
    if not guild:
        guilds = [g for g in _client.guilds if g.name.lower() == server_name.lower()]
        if guilds:
            guild = guilds[0]
        else:
            return f"Server '{server_name}' not found."

    text_channels = sorted(guild.text_channels, key=lambda c: c.position)
    voice_channels = sorted(guild.voice_channels, key=lambda c: c.position)

    lines = [f"Channels in {guild.name}:"]
    if text_channels:
        lines.append("\nText channels:")
        for ch in text_channels:
            topic = f" — {ch.topic[:60]}" if ch.topic else ""
            lines.append(f"  # {ch.name}{topic}")
    if voice_channels:
        lines.append("\nVoice channels:")
        for ch in voice_channels:
            lines.append(f"  🔈 {ch.name}")
    return "\n".join(lines)


async def _server_info(server_name: str):
    if not _client or not _client.is_ready():
        return "Discord client is not ready."
    guild = discord.utils.get(_client.guilds, name=server_name)
    if not guild:
        guilds = [g for g in _client.guilds if g.name.lower() == server_name.lower()]
        if guilds:
            guild = guilds[0]
        else:
            return f"Server '{server_name}' not found."

    total = guild.member_count
    online = sum(1 for m in guild.members if m.status != discord.Status.offline)
    role_count = len(guild.roles) - 1  # subtract @everyone
    channel_count = len(guild.text_channels) + len(guild.voice_channels)
    owner = guild.owner.name if guild.owner else "Unknown"
    created = guild.created_at.strftime("%Y-%m-%d") if guild.created_at else "Unknown"
    boost_level = guild.premium_tier

    return (
        f"Server: {guild.name}\n"
        f"Members: {total} ({online} online)\n"
        f"Channels: {channel_count}\n"
        f"Roles: {role_count}\n"
        f"Owner: {owner}\n"
        f"Created: {created}\n"
        f"Boost Level: {boost_level}"
    )


async def _online_members(server_name: str):
    if not _client or not _client.is_ready():
        return "Discord client is not ready."
    guild = discord.utils.get(_client.guilds, name=server_name)
    if not guild:
        guilds = [g for g in _client.guilds if g.name.lower() == server_name.lower()]
        if guilds:
            guild = guilds[0]
        else:
            return f"Server '{server_name}' not found."

    online = [m for m in guild.members if m.status != discord.Status.offline]
    if not online:
        return f"No one is online in {guild.name}."

    lines = [f"Online members in {guild.name} ({len(online)}):"]
    for m in sorted(online, key=lambda x: x.name.lower()):
        status_emoji = {"online": "🟢", "idle": "🟡", "dnd": "🔴"}.get(str(m.status), "⚪")
        nick = f" ({m.nick})" if m.nick else ""
        lines.append(f"  {status_emoji} {m.name}{nick}")
    return "\n".join(lines)


async def _member_info(server_name: str, username: str):
    if not _client or not _client.is_ready():
        return "Discord client is not ready."
    guild = discord.utils.get(_client.guilds, name=server_name)
    if not guild:
        guilds = [g for g in _client.guilds if g.name.lower() == server_name.lower()]
        if guilds:
            guild = guilds[0]
        else:
            return f"Server '{server_name}' not found."

    member = guild.get_member_named(username)
    if not member:
        return f"Member '{username}' not found in {guild.name}."

    roles = ", ".join(r.name for r in member.roles[1:]) or "None"
    joined = member.joined_at.strftime("%Y-%m-%d") if member.joined_at else "Unknown"
    created = member.created_at.strftime("%Y-%m-%d")
    status_emoji = {"online": "🟢", "idle": "🟡", "dnd": "🔴"}.get(str(member.status), "⚪")

    return (
        f"Member: {member.name}\n"
        f"Nickname: {member.nick or 'None'}\n"
        f"Status: {status_emoji} {member.status}\n"
        f"Roles: {roles}\n"
        f"Joined server: {joined}\n"
        f"Account created: {created}\n"
        f"Bot: {'Yes' if member.bot else 'No'}"
    )


def discord_list_servers() -> str:
    return _run_async(_list_servers())


def discord_list_channels(server_name: str) -> str:
    return _run_async(_list_channels(server_name))


def discord_server_info(server_name: str) -> str:
    return _run_async(_server_info(server_name))


def discord_online_members(server_name: str) -> str:
    return _run_async(_online_members(server_name))


def discord_member_info(server_name: str, username: str) -> str:
    return _run_async(_member_info(server_name, username))


# ─── Background Monitor ───────────────────────────────────────

class DiscordMonitor:
    """Manages the discord.Client connection in a background event loop thread."""

    def __init__(self, token: str, alert_callback=None):
        self.token = token
        self.alert_callback = alert_callback
        self._running = False

    def start(self) -> None:
        if not _discord_available or not self.token:
            return
        if self._running:
            return
        self._running = True
        
        # Start background event loop thread
        global _thread
        _thread = threading.Thread(target=self._start_client, daemon=True)
        _thread.start()

    def stop(self) -> None:
        self._running = False
        global _client, _loop, _thread
        if _client and _loop and not _loop.is_closed() and not _client.is_closed():
            try:
                future = asyncio.run_coroutine_threadsafe(_client.close(), _loop)
                future.result(timeout=10)
            except Exception:
                pass
        if _thread and _thread.is_alive():
            try:
                _thread.join(timeout=10)
            except RuntimeError:
                pass

    def _start_client(self):
        global _loop, _client
        import time
        import logging

        retry_delay = 5       # initial reconnect delay (seconds)
        max_retry_delay = 60   # cap for exponential backoff

        while self._running:
            _loop = asyncio.new_event_loop()
            asyncio.set_event_loop(_loop)
            _client = AriaDiscordClient(alert_callback=self.alert_callback)

            try:
                logging.info("Discord: connecting…")
                _loop.run_until_complete(_client.start(self.token))
            except Exception as e:
                logging.warning(f"Discord connection error: {e}")
            finally:
                try:
                    if _client and not _client.is_closed():
                        _loop.run_until_complete(_client.close())
                except Exception:
                    pass
                try:
                    pending = [task for task in asyncio.all_tasks(_loop) if not task.done()]
                    if pending:
                        for task in pending:
                            task.cancel()
                        _loop.run_until_complete(asyncio.gather(*pending, return_exceptions=True))
                except Exception:
                    pass
                try:
                    _loop.run_until_complete(_loop.shutdown_asyncgens())
                except Exception:
                    pass
                try:
                    _loop.close()
                except Exception:
                    pass

            # If we were told to stop, don't reconnect
            if not self._running:
                break

            # Exponential backoff reconnect
            logging.info(f"Discord: reconnecting in {retry_delay}s…")
            time.sleep(retry_delay)
            retry_delay = min(retry_delay * 2, max_retry_delay)
