# Mallowsbot
A discord bot used on my friends Discord Server




# Settings File
[DEFAULT]
path = *working path*
ffmpeg = *ffmpeg executable path*

[KEY]
clientkey = *Discord Bot API key*
testclientkey = *Discord Test Bot API key* only need if you used a test bot

[EmailServer]
smtpserver = *SMTP Server*
port = *SMTP Port*
email = *Email to use for SMTP*
password = *Password for Email*

# Soundboard
Soundboard items are specific to each Discord server. Use `-soundboard` to open
the reaction menu, then react with the emoji next to a sound to play it. The
reacting member must be in a voice channel. For direct playback, use
`-playsound "name"`.

- `-addsound "name"` with one supported audio attachment adds a sound.
- `-updatesound "old name" "new name"` with one audio attachment replaces a sound and can rename it.
- `-deletesound "name"` removes a sound.
- `-help soundboard` shows the commands.

Supported attachment extensions: `.aac`, `.flac`, `.m4a`, `.mp3`, `.mp4`, `.ogg`,
`.opus`, `.wav`, and `.wma`.
