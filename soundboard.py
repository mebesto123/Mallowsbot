import asyncio
from contextlib import closing
import os
import platform
import shlex
import sqlite3
import uuid
from dataclasses import dataclass
from typing import Optional, Tuple

import discord
import EasyErrors


ALLOWED_AUDIO_EXTENSIONS = {
    ".aac",
    ".flac",
    ".m4a",
    ".mp3",
    ".mp4",
    ".ogg",
    ".opus",
    ".wav",
    ".wma",
}
MAX_SOUND_NAME_LENGTH = 80
SOUNDS_PER_PAGE = 18
SOUND_EMOJIS = [
    "1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "0️⃣",
] + [chr(0x1F1E6 + index) for index in range(8)]
PREVIOUS_PAGE_EMOJI = "◀️"
NEXT_PAGE_EMOJI = "▶️"


@dataclass
class SoundboardMenu:
    sounds: list[str]
    page: int = 0


soundboardMenus: dict[int, SoundboardMenu] = {}


def getSound(sqldb: str, guildId: int, name: str) -> Optional[str]:
    with closing(sqlite3.connect(sqldb)) as connection:
        cursor = connection.cursor()
        cursor.execute(
            "SELECT filename FROM soundboard WHERE guild = ? AND name = ?",
            (str(guildId), name),
        )
        row = cursor.fetchone()
        return row[0] if row else None


def getSounds(sqldb: str, guildId: int) -> list[str]:
    with closing(sqlite3.connect(sqldb)) as connection:
        cursor = connection.cursor()
        cursor.execute(
            "SELECT name FROM soundboard WHERE guild = ? ORDER BY name COLLATE NOCASE",
            (str(guildId),),
        )
        return [row[0] for row in cursor.fetchall()]


def addSound(sqldb: str, guildId: int, name: str, filename: str) -> bool:
    with closing(sqlite3.connect(sqldb)) as connection:
        try:
            cursor = connection.cursor()
            cursor.execute(
                "INSERT INTO soundboard (guild, name, filename) VALUES (?, ?, ?)",
                (str(guildId), name, filename),
            )
            connection.commit()
            return True
        except sqlite3.IntegrityError:
            return False


def updateSound(
    sqldb: str, guildId: int, oldName: str, newName: str, filename: str
) -> Tuple[str, Optional[str]]:
    with closing(sqlite3.connect(sqldb)) as connection:
        cursor = connection.cursor()
        cursor.execute(
            "SELECT filename FROM soundboard WHERE guild = ? AND name = ?",
            (str(guildId), oldName),
        )
        row = cursor.fetchone()
        if row is None:
            return "not_found", None

        try:
            cursor.execute(
                """
                UPDATE soundboard
                SET name = ?, filename = ?
                WHERE guild = ? AND name = ?
                """,
                (newName, filename, str(guildId), oldName),
            )
            connection.commit()
            return "updated", row[0]
        except sqlite3.IntegrityError:
            return "name_taken", None


def deleteSound(sqldb: str, guildId: int, name: str) -> Optional[str]:
    with closing(sqlite3.connect(sqldb)) as connection:
        cursor = connection.cursor()
        cursor.execute(
            "SELECT filename FROM soundboard WHERE guild = ? AND name = ?",
            (str(guildId), name),
        )
        row = cursor.fetchone()
        if row is None:
            return None

        cursor.execute(
            "DELETE FROM soundboard WHERE guild = ? AND name = ?",
            (str(guildId), name),
        )
        connection.commit()
        return row[0]


def _parseArguments(message: discord.Message, command: str) -> Optional[list[str]]:
    try:
        return shlex.split(message.content[len(command) :].strip())
    except ValueError:
        return None


def _validName(name: str) -> bool:
    return bool(name.strip()) and len(name) <= MAX_SOUND_NAME_LENGTH


def isCommand(message: discord.Message, command: str) -> bool:
    content = message.content.lower()
    return content == command or content.startswith(command + " ")


async def _saveAttachment(
    message: discord.Message, repoPath: str
) -> Optional[str]:
    if len(message.attachments) != 1:
        await EasyErrors.easyError(
            message,
            "Attach exactly one audio file to this command."
        )
        return None

    attachment = message.attachments[0]
    extension = os.path.splitext(attachment.filename)[1].lower()
    if extension not in ALLOWED_AUDIO_EXTENSIONS:
        await EasyErrors.easyError(
            message,
            "Unsupported audio file type. Use mp3, ogg, m4a, wav, flac, aac, opus, wma, or mp4."
        )
        return None

    audioPath = os.path.join(repoPath, "Video.Audio")
    os.makedirs(audioPath, exist_ok=True)
    filename = uuid.uuid4().hex + extension
    await attachment.save(os.path.join(audioPath, filename))
    return filename


def _removeAudioFile(repoPath: str, filename: str) -> None:
    if os.path.basename(filename) != filename:
        raise ValueError("Soundboard database contains an invalid audio filename")

    path = os.path.join(repoPath, "Video.Audio", filename)
    if os.path.exists(path):
        os.remove(path)


async def addSoundFromMessage(
    message: discord.Message, sqldb: str, repoPath: str
) -> None:
    if message.guild is None:
        await EasyErrors.easyError(message, "Soundboard management is only available in a server.")
        return

    arguments = _parseArguments(message, "-addsound")
    if arguments is None or len(arguments) != 1 or not _validName(arguments[0]):
        await EasyErrors.easyError(message, 'Usage: `-addsound "sound name"` with one audio attachment.')
        return

    filename = await _saveAttachment(message, repoPath)
    if filename is None:
        return

    if not addSound(sqldb, message.guild.id, arguments[0], filename):
        _removeAudioFile(repoPath, filename)
        await EasyErrors.easyError(message, "A sound with that name already exists in this server.")
        return

    await message.channel.send(f"Added sound **{arguments[0]}**.")


async def updateSoundFromMessage(
    message: discord.Message, sqldb: str, repoPath: str
) -> None:
    if message.guild is None:
        await EasyErrors.easyError(message, "Soundboard management is only available in a server.")
        return

    arguments = _parseArguments(message, "-updatesound")
    if (
        arguments is None
        or len(arguments) != 2
        or not _validName(arguments[0])
        or not _validName(arguments[1])
    ):
        await EasyErrors.easyError(
            message,
            'Usage: `-updatesound "old name" "new name"` with one replacement audio attachment.'
        )
        return

    filename = await _saveAttachment(message, repoPath)
    if filename is None:
        return

    status, previousFilename = updateSound(
        sqldb, message.guild.id, arguments[0], arguments[1], filename
    )
    if status != "updated":
        _removeAudioFile(repoPath, filename)
        if status == "not_found":
            await EasyErrors.easyError(message, f"No sound named **{arguments[0]}** was found.")
        else:
            await EasyErrors.easyError(
                message,
                f"A sound named **{arguments[1]}** already exists in this server."
            )
        return

    if previousFilename is not None:
        _removeAudioFile(repoPath, previousFilename)
    await message.channel.send(
        f"Updated sound **{arguments[0]}** to **{arguments[1]}**."
    )


async def deleteSoundFromMessage(
    message: discord.Message, sqldb: str, repoPath: str
) -> None:
    if message.guild is None:
        await EasyErrors.easyError(message, "Soundboard management is only available in a server.")
        return

    arguments = _parseArguments(message, "-deletesound")
    if arguments is None or len(arguments) != 1 or not _validName(arguments[0]):
        await EasyErrors.easyError(message, 'Usage: `-deletesound "sound name"`.')
        return

    filename = deleteSound(sqldb, message.guild.id, arguments[0])
    if filename is None:
        await EasyErrors.easyError(message, f"No sound named **{arguments[0]}** was found.")
        return

    _removeAudioFile(repoPath, filename)
    await message.channel.send(f"Deleted sound **{arguments[0]}**.")


async def playSound(
    message: discord.Message,
    sqldb: str,
    repoPath: str,
    name: str,
    member: Optional[discord.Member] = None,
) -> None:
    if message.guild is None:
        await EasyErrors.easyError(message, "Soundboard playback is only available in a server.")
        return

    member = member or message.author
    if member.voice is None or member.voice.channel is None:
        await EasyErrors.easyError(message, "Join a voice channel before playing a sound.")
        return

    filename = getSound(sqldb, message.guild.id, name)
    if filename is None:
        await EasyErrors.easyError(message, f"No sound named **{name}** was found.")
        return
    if os.path.basename(filename) != filename:
        raise ValueError("Soundboard database contains an invalid audio filename")

    path = os.path.join(repoPath, "Video.Audio", filename)
    if not os.path.isfile(path):
        await EasyErrors.easyError(message, f"The audio file for **{name}** is missing.")
        return

    channel = member.voice.channel
    voiceClient = message.guild.voice_client
    if voiceClient is not None and voiceClient.is_connected():
        if voiceClient.is_playing():
            await EasyErrors.easyError(message, "The bot is already playing audio.")
            return
        if voiceClient.channel != channel:
            await voiceClient.move_to(channel)
    else:
        voiceClient = await channel.connect(timeout=30, reconnect=False)

    executable = (
        os.path.join(repoPath, "ffmpeg", "bin", "ffmpeg.exe")
        if platform.system() == "Windows"
        else "/usr/bin/ffmpeg"
    )
    loop = asyncio.get_running_loop()
    playbackFinished: asyncio.Future[Optional[Exception]] = loop.create_future()

    def playbackComplete(error: Optional[Exception]) -> None:
        loop.call_soon_threadsafe(playbackFinished.set_result, error)

    try:
        voiceClient.play(
            discord.FFmpegPCMAudio(path, executable=executable),
            after=playbackComplete,
        )
        playbackError = await asyncio.shield(playbackFinished)
        if playbackError is not None:
            await EasyErrors.easyError(message, f"Soundboard playback failed: {playbackError}")
    finally:
        if voiceClient.is_connected():
            await voiceClient.disconnect()


async def playSoundFromMessage(
    message: discord.Message, sqldb: str, repoPath: str, command: str
) -> None:
    arguments = _parseArguments(message, command)
    if arguments is None or len(arguments) != 1 or not _validName(arguments[0]):
        await EasyErrors.easyError(message, f'Usage: `{command} "sound name"`.')
        return

    await playSound(message, sqldb, repoPath, arguments[0])


def _menuEmbed(menu: SoundboardMenu) -> discord.Embed:
    start = menu.page * SOUNDS_PER_PAGE
    pageSounds = menu.sounds[start : start + SOUNDS_PER_PAGE]
    entries = [
        f"{emoji}  {name}"
        for emoji, name in zip(SOUND_EMOJIS, pageSounds)
    ]
    pageCount = (len(menu.sounds) + SOUNDS_PER_PAGE - 1) // SOUNDS_PER_PAGE
    embed = discord.Embed(
        title="Soundboard",
        description="React with the emoji next to a sound to play it."
        + "\n\n"
        + "\n".join(entries),
        color=discord.Color.blurple(),
    )
    if pageCount > 1:
        embed.set_footer(text=f"Page {menu.page + 1} of {pageCount} · Use ◀️ ▶️ to browse")
    return embed


async def sendSoundboardMenu(
    message: discord.Message, sqldb: str
) -> None:
    if message.guild is None:
        await EasyErrors.easyError(message, "The soundboard is only available in a server.")
        return

    sounds = getSounds(sqldb, message.guild.id)
    if not sounds:
        await EasyErrors.easyError(message, "There are no sounds in this server's soundboard yet.")
        return

    menu = SoundboardMenu(sounds=sounds)
    menuMessage = await message.channel.send(embed=_menuEmbed(menu))
    soundboardMenus[menuMessage.id] = menu
    try:
        for emoji in SOUND_EMOJIS[: min(len(sounds), SOUNDS_PER_PAGE)]:
            await menuMessage.add_reaction(emoji)
        if len(sounds) > SOUNDS_PER_PAGE:
            await menuMessage.add_reaction(PREVIOUS_PAGE_EMOJI)
            await menuMessage.add_reaction(NEXT_PAGE_EMOJI)
    except discord.HTTPException as error:
        soundboardMenus.pop(menuMessage.id, None)
        await EasyErrors.easyError(message, f"Could not add soundboard reactions: {error}")


async def handleSoundboardReaction(
    reaction: discord.Reaction,
    user: discord.User,
    sqldb: str,
    repoPath: str,
) -> None:
    if user.bot:
        return

    menu = soundboardMenus.get(reaction.message.id)
    if menu is None or reaction.message.guild is None:
        return

    if reaction.emoji == PREVIOUS_PAGE_EMOJI and menu.page > 0:
        menu.page -= 1
        await reaction.message.edit(embed=_menuEmbed(menu))
        return

    lastPage = (len(menu.sounds) - 1) // SOUNDS_PER_PAGE
    if reaction.emoji == NEXT_PAGE_EMOJI and menu.page < lastPage:
        menu.page += 1
        await reaction.message.edit(embed=_menuEmbed(menu))
        return

    start = menu.page * SOUNDS_PER_PAGE
    pageSounds = menu.sounds[start : start + SOUNDS_PER_PAGE]
    selectedSound = next(
        (
            name
            for emoji, name in zip(SOUND_EMOJIS, pageSounds)
            if str(reaction.emoji) == emoji
        ),
        None,
    )
    if selectedSound is None:
        return

    member = reaction.message.guild.get_member(user.id)
    if member is None:
        await EasyErrors.easyError(
            reaction.message, "Could not find your server membership to play this sound."
        )
        return

    await playSound(
        reaction.message,
        sqldb,
        repoPath,
        selectedSound,
        member=member,
    )
