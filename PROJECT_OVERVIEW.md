# Mallowsbot - Project Overview

## Project Summary
Mallowsbot is a Discord bot built with discord.py designed for a friend's Discord server. It provides various utilities for connection/disconnection audio notifications, team management, voice channel subscriptions, and email notifications.

## Technology Stack
- **Framework**: discord.py
- **Language**: Python 3
- **Database**: SQLite
- **Dependencies**: pandas, discord, configparser
- **Additional Services**: SMTP Email integration, FFmpeg for audio

## Core Features

### 1. **Connection/Disconnection Tunes** (`connectionTune.py`)
   - Users upload custom audio files (`.mp3`, `.ogg`, `.m4a`) as connection/disconnection sounds
   - Bot stores audio files with naming convention: `{user_id}{guild_id}{type}{extension}`
   - Tracks songs in CSV files (connection/disconnection tunes per user per guild)

### 2. **Voice Channel Notifications** (`voiceChannelNotification.py`)
   - Users can subscribe to notifications when specific members join voice channels
   - SQLite database stores subscription data with rate limiting (1 hour between notifications)
   - Handles subscriptions and unsubscriptions via `-vcsub` and `-vcunsub` commands
   - "Campfire" setup for special voice channel event notifications

### 3. **Teams Management** (`Teams.py`)
   - Users can create teams for organizing guild members

### 4. **Voice Chat Logging** (`voicechatlog.py`)
   - Logs voice channel activities for audit/reference purposes

### 5. **Admin Tools** (`AdminTools.py`)
   - Role-based admin management
   - Add/remove admin roles with confirmation reactions
   - Tracks admin roles per guild

### 6. **Email Notifications** (`EmailSender.py`)
   - SMTP integration for sending emails to users
   - Users can be added to mailing lists
   - Email functionality with list management

### 7. **Calendar Events** (`calendar.py`)
   - Display monthly calendars with events in the #Calendar channel
   - Users can add events to single dates or date ranges
   - Events are stored in SQLite database with username and description
   - Supports date range events (max 365 days)
   - **IMPORTANT**: All calendar commands restricted to #Calendar channel only

### 8. **Database Setup** (`databaseSetup.py`)
   - Initializes SQLite database
   - Voice channel notification table population
   - Calendar events table initialization

## Configuration Structure

### Settings Location
`settings/` folder contains:
- `botsettings.ini` - Main bot configuration
- `botsettingslinux.ini` - Linux-specific settings
- `guildsettings.ini` - Per-guild settings
- `{guildid}.ini` - Guild-specific configurations

### Configuration Required
```ini
[DEFAULT]
path = <working directory path>
ffmpeg = <ffmpeg executable path>
sqldb = <sqlite database path>
connectioncsv = <csv file for connection tunes>
disconnectioncsv = <csv file for disconnection tunes>
voicechannelnotifcsv = <csv file for voice notifications>

[KEY]
clientkey = <Discord Bot API key>
testclientkey = <Test Bot API key (optional)>

[EmailServer]
smtpserver = <SMTP server address>
port = <SMTP port>
email = <Sender email>
password = <Email password>
listpath = <Path to email list file>
```

## Command System

### Current Implementation
Bot uses **prefix-based commands** with message content parsing. Commands are handled in `mallow_bot.py` via:
- Message content checking: `if message.content.lower().startswith("-command"):`
- Direct string parsing for parameters

### Supported Commands
- `-vcsub <member>` - Subscribe to voice channel notifications
- `-vcunsub <member>` - Unsubscribe from voice channel notifications
- `-vcpop` - Populate voice channel notification database
- `-setupcampfire` - Setup campfire notifications
- `-connectiontune` - Upload connection sound (with audio file attachment)
- `-disconnectiontune` - Upload disconnection sound (with audio file attachment)
- `-playconnectiontune` / `-intro` - Play connection tune
- `-playdisconnectiontune` / `-outro` - Play disconnection tune
- `-teams` / `-newteams` - Create teams
- `-addtoemaillist` - Add user to email list
- `-showemaillist` - Display email list
- `-email` / `-sendemail` - Send email notification
- `-calendar [month] [year]` - Display calendar (only in #Calendar channel)
- `-addevent YYYY-MM-DD Event` - Add event to calendar (only in #Calendar channel)
- `-addeventrange YYYY-MM-DD YYYY-MM-DD Event` - Add event to date range (only in #Calendar channel)
- `-removeevent YYYY-MM-DD` - Remove event from calendar (only in #Calendar channel)
- `-help <command>` - Get help for specific commands

## Discord Intents Configuration
```python
intents.members = True          # For member information
intents.reactions = True        # For reaction-based confirmations
intents.voice_states = True     # For voice channel events
intents.message_content = True  # For message parsing
intents.messages = True         # For message events
```

## Important Architecture Notes

### Event Handlers
- `@client.event on_ready()` - Bot startup confirmation
- `@client.event on_guild_join()` - Welcome message to new guilds
- `@client.event on_message()` - Main command processing
- `@client.event on_voice_state_update()` (implied in modules) - Voice channel change detection
- `@client.event on_reaction_add()` - Reaction confirmations for admin tools

### Key Dependencies
- `EasyErrors.py` - Error message handling utilities
- `connectionTune.py` - Audio file management
- `Teams.py` - Team organization
- `voiceChannelNotification.py` - VC subscription system
- `EmailSender.py` - Email service integration
- `databaseSetup.py` - Database initialization

## Testing Files
- `test_bot.py` - Same as `mallow_bot.py` (for testing purposes)
- `mallow_bot_windows.py` - Windows-specific version
- `testfile.py` - General testing file
- `Backups/` - Contains backup copies of bot versions

---

## ⚠️ IMPORTANT DEVELOPMENT CONSTRAINTS

### **DO NOT REFACTOR TO bot.commands**
❌ **At this time, DO NOT convert the current prefix-based command system to `bot.commands` or Discord slash commands.**

- The bot is currently using traditional prefix-based message parsing
- This is a conscious architectural choice for this project
- Any future enhancements should maintain the existing message-based command system
- If modernizing the command system becomes necessary, this decision will be revisited explicitly

### **Preserve Discord API Calls**
❌ **DO NOT change Discord channel or API calls to use alternative patterns without explicit approval.**

- Maintain current `discord.Client` implementation
- Keep existing event handlers as-is unless specifically requested
- Message sending via `message.channel.send()` is the current standard
- DM creation via `discord.utils.get()` and user.create_dm() is standard

### **Calendar Channel Restriction**
⚠️ **Calendar display ONLY appears in a channel named "Calendar"**

- Users can TYPE calendar commands in ANY channel
- However, calendar DISPLAY results only appear in the #Calendar channel
- All calendar operations (`-calendar`, `-addevent`, `-addeventrange`, `-removeevent`, `-help calendar`) will post their results to #Calendar
- If a #Calendar channel doesn't exist, users will receive an error message asking them to create one
- Users receive a confirmation message in their current channel telling them the result was posted to #Calendar
- This keeps calendar activity organized in one place while allowing commands from anywhere

---

## Future Development Notes
- Consider logging improvements for troubleshooting
- Email error handling could be enhanced
- Voice channel notification cooldown could be made configurable per guild
- Team management could use additional features (team roster, team-specific channels)

## File Status Summary
- ✅ `connectionTune.py` - Fully functional
- ✅ `voiceChannelNotification.py` - Fully functional
- ✅ `Teams.py` - Functional
- ✅ `EmailSender.py` - Functional
- ✅ `AdminTools.py` - Partially implemented (commented out help/vcstop)
- ✅ `databaseSetup.py` - Database initialization utility
- ⚠️ `voicechatlog.py` - Present but usage unclear
