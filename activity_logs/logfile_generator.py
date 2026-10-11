# logging module, used here to configure the activity log, basicConfig sets the filename, 
# level threshold and format, without this import logging.basicConfig cannot be called
import logging 

from datetime import datetime # datetime class from the datetime library, used here to dynamically name the log file with today's date
import os  # operating system module, provides functions to interact with the file system and OS

# creates the log directory if it doesn't exist and 'exist_ok=True' prevents error if folder already exists
os.makedirs('projectB_logs', exist_ok=True)

# logging.basicConfig configures the activity log for the entire session
# filename: path and name of the log file, uses an f-string to embed datetime.now().strftime() directly
#           f-string evaluates whatever is inside {} at runtime, allowing functions, attributes,
#           and expressions to be called inline without storing them in separate variables first
#           strftime formats the date as a readable string e.g. 2026-08-24
#           each day generates a new file, easier for management and debugging
# level: minimum threshold for what gets logged, INFO and everything above it gets captured
#        levels in order: DEBUG, INFO, WARNING, ERROR, CRITICAL — setting INFO skips DEBUG only
# format: defines how each log line is written, three fields separated by ' - '
#         %(asctime)s: timestamp formatted as readable ASCII text, e.g. 2026-08-24 14:32:01,123
#         %(levelname)s: the level of the log entry, INFO, WARNING, ERROR or CRITICAL
#         %(message)s: the message passed to logging.info() or logging.error() etc.
#         %()s syntax: % marks the start, () holds the variable name, s outputs it as a string

# filename includes date and time to generate a unique file per session, 
# preventing entries from different sessions being written to the same file

logging.basicConfig(
    filename = f'projectB_logs/{datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}-activity.log',
    level = logging.INFO,
    format = '%(asctime)s - %(levelname)s - %(message)s'

    )