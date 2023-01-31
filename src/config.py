# Base github url without a trailing /, ie https://github.com/User/Repo
GITHUB_URL = "https://github.com/RPIRecordingBox/BoxUI"

# Raw file to check for updates (version.txt)
UPDATE_URL = "https://raw.githubusercontent.com/RPIRecordingBox/BoxUI/master/version.txt"

# Text to display on the info tab, not a format string
# the {var} are placeholders for the info.py screen
# Supports HTML-like formatting
INFO_TEXT = """
<h3>Box v{version}</h3><br>

<span style="color: #00AA00">{updateAvail}</span>

<b>By:</b> Radke Lab  &nbsp;   <b>Support:</b> <span style="color: #0044AA">rjradke@ecse.rpi.edu</span><br>
<b>Github:</b>  <span style="color: #0044AA">{github}</span><br><br>

<b>Last check for update:</b> {lastUpdated}<br><br>

{update}<br>

<span style="color: #444">(Note: updating will restart the program, recordings in progress may be lost)<br>
You should only revert update if there is a breaking change!</span><br><br>

{root}
""".replace("{github}", GITHUB_URL)

# Chunk size to read from stream in # of bytes
CHUNK = 8192

#  ultiplier for waveform in postprocessing
GAIN = 6

# Time of each snippet
SECONDS = 10

RECORD_DIR = "recordings/"

# Clicks required for revert confirmation
CLICKS_TO_REVERT = 5

# Time for revert confirmation (s) before time out confirmation
TIME_TO_REVERT = 7