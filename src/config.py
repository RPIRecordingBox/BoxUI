INFO_TEXT = """
<h3>Box v{version}</h3><br>

<b>By:</b> [Insert names here]<br>
<b>Support:</b> [Insert emails here]<br>
<b>Github:</b>  <span style="color: #0044AA">https://github.com/RPIRecordingBox/BoxUI</span><br><br>

<b>Last check for update:</b> {lastUpdated}<br><br>

{update}<br><br>

<span style="color: #444">(Note: updating will restart the program,<br>recordings in progress may be lost)</span><br><br>

{root}
"""

# Chunk size to read from stream in # of bytes
CHUNK = 8192

#  ultiplier for waveform in postprocessing
GAIN = 6

# Time of each snippet
SECONDS = 10 

RECORD_DIR = "recordings/"