import discord
import calendar
import sqlite3
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta


def addCalendarEvent(sqldb, date_str, username, event_description=""):
    """
    Add an event to the calendar database.
    
    Args:
        sqldb (str): Path to the SQLite database file
        date_str (str): Date string in format "YYYY-MM-DD"
        username (str): Discord username
        event_description (str): Optional event description
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        sqliteConnection = sqlite3.connect(sqldb)
        cursor = sqliteConnection.cursor()
        
        # Validate date format
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            return False
        
        cursor.execute('''
            INSERT INTO calendarEvents (date, username, event_description)
            VALUES (?, ?, ?)
        ''', (date_str, username, event_description))
        
        sqliteConnection.commit()
        sqliteConnection.close()
        return True
    except sqlite3.Error as error:
        print(f"Error adding calendar event: {error}")
        return False


def getCalendarEventsForMonth(sqldb, year, month):
    """
    Retrieve all events for a specific month.
    
    Args:
        sqldb (str): Path to the SQLite database file
        year (int): The year
        month (int): The month (1-12)
    
    Returns:
        dict: Dictionary with date as key and list of events as value
    """
    try:
        sqliteConnection = sqlite3.connect(sqldb)
        cursor = sqliteConnection.cursor()
        
        # Create date range for the month
        start_date = f"{year}-{month:02d}-01"
        if month == 12:
            end_date = f"{year + 1}-01-01"
        else:
            end_date = f"{year}-{month + 1:02d}-01"
        
        cursor.execute('''
            SELECT date, username, event_description FROM calendarEvents
            WHERE date >= ? AND date < ?
            ORDER BY date, username
        ''', (start_date, end_date))
        
        events_dict = {}
        for row in cursor.fetchall():
            date = row[0]
            if date not in events_dict:
                events_dict[date] = []
            events_dict[date].append({
                'username': row[1],
                'description': row[2]
            })
        
        sqliteConnection.close()
        return events_dict
    except sqlite3.Error as error:
        print(f"Error retrieving calendar events: {error}")
        return {}


def removeCalendarEvent(sqldb, date_str, username):
    """
    Remove an event from the calendar database.
    
    Args:
        sqldb (str): Path to the SQLite database file
        date_str (str): Date string in format "YYYY-MM-DD"
        username (str): Discord username
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        sqliteConnection = sqlite3.connect(sqldb)
        cursor = sqliteConnection.cursor()
        
        cursor.execute('''
            DELETE FROM calendarEvents
            WHERE date = ? AND username = ?
        ''', (date_str, username))
        
        sqliteConnection.commit()
        rows_deleted = cursor.rowcount
        sqliteConnection.close()
        
        return rows_deleted > 0
    except sqlite3.Error as error:
        print(f"Error removing calendar event: {error}")
        return False


def addCalendarEventRange(sqldb, start_date, end_date, username, event_description=""):
    """
    Add an event to a range of dates in the calendar database.
    
    Args:
        sqldb (str): Path to the SQLite database file
        start_date (str): Start date string in format "YYYY-MM-DD"
        end_date (str): End date string in format "YYYY-MM-DD"
        username (str): Discord username
        event_description (str): Optional event description
    
    Returns:
        tuple: (success: bool, message: str, dates_added: int)
    """
    try:
        # Validate date formats
        try:
            start = datetime.strptime(start_date, "%Y-%m-%d")
            end = datetime.strptime(end_date, "%Y-%m-%d")
        except ValueError:
            return False, "Invalid date format. Use YYYY-MM-DD", 0
        
        # Check if end date is after start date
        if end < start:
            return False, f"End date ({end_date}) must be after or equal to start date ({start_date})", 0
        
        # Check if the range is too large (limit to 365 days to prevent abuse)
        day_diff = (end - start).days
        if day_diff > 365:
            return False, f"Date range is too large ({day_diff} days). Maximum is 365 days", 0
        
        sqliteConnection = sqlite3.connect(sqldb)
        cursor = sqliteConnection.cursor()
        
        # Add event for each date in the range
        current_date = start
        dates_added = 0
        
        while current_date <= end:
            date_str = current_date.strftime("%Y-%m-%d")
            cursor.execute('''
                INSERT INTO calendarEvents (date, username, event_description)
                VALUES (?, ?, ?)
            ''', (date_str, username, event_description))
            dates_added += 1
            current_date += timedelta(days=1)
        
        sqliteConnection.commit()
        sqliteConnection.close()
        
        return True, f"Successfully added event to {dates_added} date(s)", dates_added
    except Exception as error:
        print(f"Error adding calendar event range: {error}")
        return False, f"Error adding events: {str(error)}", 0


class CalendarDisplay:
    """Class to handle calendar display and interactions in Discord"""
    
    def __init__(self):
        self.months_dict = {
            1: "January", 2: "February", 3: "March", 4: "April",
            5: "May", 6: "June", 7: "July", 8: "August",
            9: "September", 10: "October", 11: "November", 12: "December"
        }
        self.days_abbr = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    
    def get_calendar_text(self, year, month, events_dict=None):
        """
        Generate calendar text for a specific month and year.
        
        Args:
            year (int): The year
            month (int): The month (1-12)
            events_dict (dict): Dictionary with dates as keys and events as values
        
        Returns:
            str: Formatted calendar text for Discord
        """
        # Get the month's calendar
        cal = calendar.monthcalendar(year, month)
        month_name = self.months_dict[month]
        
        # Build the calendar text
        calendar_text = f"{month_name} {year}\n"
        calendar_text += " ".join(self.days_abbr) + "\n"
        calendar_text += "─" * 28 + "\n"
        
        # Add each week
        for week in cal:
            week_str = ""
            for day in week:
                if day == 0:
                    week_str += "    "  # Empty cell for days outside the month
                else:
                    week_str += f"{day:>3} "
            calendar_text += week_str + "\n"
        
        return calendar_text
    
    def create_calendar_embed(self, year, month, events_dict=None, title="Calendar"):
        """
        Create a Discord embed with calendar information and events.
        
        Args:
            year (int): The year
            month (int): The month (1-12)
            events_dict (dict): Dictionary with dates as keys and events as values
            title (str): Title for the embed
        
        Returns:
            discord.Embed: Formatted embed with calendar
        """
        month_name = self.months_dict[month]
        
        embed = discord.Embed(
            title=f"{title} - {month_name} {year}",
            color=discord.Color.blue()
        )
        
        # Add calendar text
        calendar_text = self.get_calendar_text(year, month)
        embed.add_field(
            name="📆 Calendar",
            value=f"```\n{calendar_text}```",
            inline=False
        )
        
        # Add events if they exist
        if events_dict:
            events_display = self._format_events_for_embed(events_dict)
            if events_display:
                embed.add_field(
                    name="📅 Events",
                    value=events_display,
                    inline=False
                )
        
        # Add footer with navigation info
        embed.set_footer(text="Use -calendar [month] [year] to view different months | -addevent [date] [event]")
        
        return embed
    
    def _format_events_for_embed(self, events_dict):
        """
        Format events dictionary for display in embed.
        
        Args:
            events_dict (dict): Dictionary with dates as keys and events as values
        
        Returns:
            str: Formatted events text or empty string if no events
        """
        if not events_dict:
            return ""
        
        events_text = ""
        for date in sorted(events_dict.keys()):
            day = date.split("-")[2]
            events_text += f"\n**{day}**: "
            event_list = []
            for event in events_dict[date]:
                if event['description']:
                    event_list.append(f"{event['username']}: {event['description']}")
                else:
                    event_list.append(f"{event['username']}")
            events_text += " | ".join(event_list)
        
        return events_text if events_text else ""
    
    def parse_date_input(self, date_string):
        """
        Parse user input for month and year.
        
        Args:
            date_string (str): User input string (e.g., "january 2025", "1 2025")
        
        Returns:
            tuple: (year, month) or (None, None) if parsing fails
        """
        try:
            parts = date_string.strip().split()
            
            # Try to parse month
            month_input = parts[0].lower()
            
            # Check if it's a month name or number
            month = None
            for num, name in self.months_dict.items():
                if name.lower().startswith(month_input):
                    month = num
                    break
            
            if month is None:
                try:
                    month = int(month_input)
                    if month < 1 or month > 12:
                        return None, None
                except ValueError:
                    return None, None
            
            # Try to parse year
            year = None
            if len(parts) > 1:
                try:
                    year = int(parts[1])
                except ValueError:
                    return None, None
            else:
                year = datetime.now().year
            
            return year, month
        except:
            return None, None


async def displayCalendar(message, sqldb, args=""):
    """
    Display a calendar in the Discord channel with events.
    
    Usage:
        -calendar              # Shows current month
        -calendar january      # Shows specific month of current year
        -calendar 1 2025       # Shows specific month and year
        -calendar january 2025 # Shows specific month and year (text)
    
    Args:
        message (discord.Message): The Discord message object
        sqldb (str): Path to the SQLite database file
        args (str): Optional month and year arguments
    """
    # Find the Calendar channel in the guild
    calendar_channel = None
    for channel in message.guild.text_channels:
        if channel.name.lower() == "calendar":
            calendar_channel = channel
            break
    
    # If no Calendar channel exists, inform the user
    if calendar_channel is None:
        embed = discord.Embed(
            title="Calendar Error",
            color=discord.Color.red()
        )
        embed.add_field(
            name="Calendar Channel Not Found",
            value="A **#Calendar** channel does not exist in this server. Please create one to use calendar commands.",
            inline=False
        )
        await message.channel.send(embed=embed)
        return
    
    cal_display = CalendarDisplay()
    
    # Default to current date
    today = datetime.now()
    year = today.year
    month = today.month
    
    # Parse user input if provided
    if args.strip():
        parsed_year, parsed_month = cal_display.parse_date_input(args)
        if parsed_year is None:
            embed = discord.Embed(
                title="Calendar Error",
                color=discord.Color.red()
            )
            embed.add_field(
                name="Invalid Date Format",
                value="Usage: `-calendar [month] [year]`\n"
                      "Examples: `-calendar`, `-calendar january`, `-calendar 1 2025`, `-calendar january 2025`",
                inline=False
            )
            await message.channel.send(embed=embed)
            return
        
        year = parsed_year
        month = parsed_month
    
    # Fetch events for the month
    events_dict = getCalendarEventsForMonth(sqldb, year, month)
    
    # Create and send the calendar embed to Calendar channel
    embed = cal_display.create_calendar_embed(year, month, events_dict)
    await calendar_channel.send(embed=embed)
    
    # Send confirmation to the user
    confirmation = discord.Embed(
        title="Calendar Posted",
        color=discord.Color.green()
    )
    confirmation.add_field(
        name="Status",
        value=f"Calendar for {cal_display.months_dict[month]} {year} has been posted to #Calendar",
        inline=False
    )
    await message.channel.send(embed=confirmation)


async def addEventToCalendar(message, sqldb, args=""):
    """
    Add an event to the calendar database.
    
    Usage:
        -addevent 2025-12-25 Birthday Party
        -addevent 2025-01-15 New Years!
    
    Args:
        message (discord.Message): The Discord message object
        sqldb (str): Path to the SQLite database file
        args (str): Date and event description
    """
    # Find the Calendar channel in the guild
    calendar_channel = None
    for channel in message.guild.text_channels:
        if channel.name.lower() == "calendar":
            calendar_channel = channel
            break
    
    # If no Calendar channel exists, inform the user
    if calendar_channel is None:
        embed = discord.Embed(
            title="Add Event Error",
            color=discord.Color.red()
        )
        embed.add_field(
            name="Calendar Channel Not Found",
            value="A **#Calendar** channel does not exist in this server. Please create one to use calendar commands.",
            inline=False
        )
        await message.channel.send(embed=embed)
        return
    
    if not args.strip():
        embed = discord.Embed(
            title="Add Event Error",
            color=discord.Color.red()
        )
        embed.add_field(
            name="Missing Arguments",
            value="Usage: `-addevent [YYYY-MM-DD] [event description]`\n"
                  "Example: `-addevent 2025-12-25 Birthday Party`",
            inline=False
        )
        await message.channel.send(embed=embed)
        return
    
    # Parse the input
    parts = args.split(" ", 1)
    
    if len(parts) < 1:
        embed = discord.Embed(
            title="Add Event Error",
            color=discord.Color.red()
        )
        embed.add_field(
            name="Invalid Format",
            value="Usage: `-addevent [YYYY-MM-DD] [event description]`\n"
                  "Example: `-addevent 2025-12-25 Birthday Party`",
            inline=False
        )
        await message.channel.send(embed=embed)
        return
    
    date_str = parts[0].strip()
    event_description = parts[1].strip() if len(parts) > 1 else ""
    username = message.author.name
    
    # Validate date format
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        embed = discord.Embed(
            title="Add Event Error",
            color=discord.Color.red()
        )
        embed.add_field(
            name="Invalid Date Format",
            value="Date must be in format: YYYY-MM-DD\n"
                  "Example: 2025-12-25 for December 25, 2025",
            inline=False
        )
        await message.channel.send(embed=embed)
        return
    
    # Add event to database
    success = addCalendarEvent(sqldb, date_str, username, event_description)
    
    if success:
        embed = discord.Embed(
            title="Event Added",
            color=discord.Color.green()
        )
        embed.add_field(
            name="Date",
            value=date_str,
            inline=True
        )
        embed.add_field(
            name="User",
            value=username,
            inline=True
        )
        if event_description:
            embed.add_field(
                name="Event",
                value=event_description,
                inline=False
            )
        await calendar_channel.send(embed=embed)
        
        # Send confirmation to user
        confirmation = discord.Embed(
            title="Event Added",
            color=discord.Color.green()
        )
        confirmation.add_field(
            name="Status",
            value=f"Your event for {date_str} has been added to #Calendar",
            inline=False
        )
        await message.channel.send(embed=confirmation)
    else:
        embed = discord.Embed(
            title="Add Event Error",
            color=discord.Color.red()
        )
        embed.add_field(
            name="Failed to Add Event",
            value="There was an error adding your event to the calendar.",
            inline=False
        )
        await message.channel.send(embed=embed)


async def addEventRangeToCalendar(message, sqldb, args=""):
    """
    Add an event to a date range in the calendar database.
    
    Usage:
        -addeventrange 2025-12-20 2025-12-25 Holiday Break
        -addeventrange 2025-01-01 2025-01-07 New Year Week
    
    Args:
        message (discord.Message): The Discord message object
        sqldb (str): Path to the SQLite database file
        args (str): Start date, end date, and event description
    """
    # Find the Calendar channel in the guild
    calendar_channel = None
    for channel in message.guild.text_channels:
        if channel.name.lower() == "calendar":
            calendar_channel = channel
            break
    
    # If no Calendar channel exists, inform the user
    if calendar_channel is None:
        embed = discord.Embed(
            title="Add Event Range Error",
            color=discord.Color.red()
        )
        embed.add_field(
            name="Calendar Channel Not Found",
            value="A **#Calendar** channel does not exist in this server. Please create one to use calendar commands.",
            inline=False
        )
        await message.channel.send(embed=embed)
        return
    
    if not args.strip():
        embed = discord.Embed(
            title="Add Event Range Error",
            color=discord.Color.red()
        )
        embed.add_field(
            name="Missing Arguments",
            value="Usage: `-addeventrange [start-date] [end-date] [event description]`\n"
                  "Example: `-addeventrange 2025-12-20 2025-12-25 Holiday Break`",
            inline=False
        )
        await message.channel.send(embed=embed)
        return
    
    # Parse the input - need start date, end date, and optional description
    parts = args.split(" ", 2)
    
    if len(parts) < 2:
        embed = discord.Embed(
            title="Add Event Range Error",
            color=discord.Color.red()
        )
        embed.add_field(
            name="Invalid Format",
            value="Usage: `-addeventrange [start-date] [end-date] [event description]`\n"
                  "Example: `-addeventrange 2025-12-20 2025-12-25 Holiday Break`",
            inline=False
        )
        await message.channel.send(embed=embed)
        return
    
    start_date = parts[0].strip()
    end_date = parts[1].strip()
    event_description = parts[2].strip() if len(parts) > 2 else ""
    username = message.author.name
    
    # Validate date formats
    try:
        datetime.strptime(start_date, "%Y-%m-%d")
        datetime.strptime(end_date, "%Y-%m-%d")
    except ValueError:
        embed = discord.Embed(
            title="Add Event Range Error",
            color=discord.Color.red()
        )
        embed.add_field(
            name="Invalid Date Format",
            value="Dates must be in format: YYYY-MM-DD\n"
                  "Example: `-addeventrange 2025-12-20 2025-12-25 Holiday Break`",
            inline=False
        )
        await message.channel.send(embed=embed)
        return
    
    # Add event range to database
    success, message_text, dates_added = addCalendarEventRange(sqldb, start_date, end_date, username, event_description)
    
    if success:
        embed = discord.Embed(
            title="Event Range Added",
            color=discord.Color.green()
        )
        embed.add_field(
            name="Start Date",
            value=start_date,
            inline=True
        )
        embed.add_field(
            name="End Date",
            value=end_date,
            inline=True
        )
        embed.add_field(
            name="Dates Added",
            value=str(dates_added),
            inline=True
        )
        embed.add_field(
            name="User",
            value=username,
            inline=True
        )
        if event_description:
            embed.add_field(
                name="Event",
                value=event_description,
                inline=False
            )
        await calendar_channel.send(embed=embed)
        
        # Send confirmation to user
        confirmation = discord.Embed(
            title="Event Range Added",
            color=discord.Color.green()
        )
        confirmation.add_field(
            name="Status",
            value=f"Event range ({start_date} to {end_date}) added to #Calendar ({dates_added} dates)",
            inline=False
        )
        await message.channel.send(embed=confirmation)
    else:
        embed = discord.Embed(
            title="Add Event Range Error",
            color=discord.Color.red()
        )
        embed.add_field(
            name="Error",
            value=message_text,
            inline=False
        )
        await message.channel.send(embed=embed)


async def removeEventFromCalendar(message, sqldb, args=""):
    """
    Remove an event from the calendar database.
    
    Usage:
        -removeevent 2025-12-25
    
    Args:
        message (discord.Message): The Discord message object
        sqldb (str): Path to the SQLite database file
        args (str): Date to remove event from
    """
    # Find the Calendar channel in the guild
    calendar_channel = None
    for channel in message.guild.text_channels:
        if channel.name.lower() == "calendar":
            calendar_channel = channel
            break
    
    # If no Calendar channel exists, inform the user
    if calendar_channel is None:
        embed = discord.Embed(
            title="Remove Event Error",
            color=discord.Color.red()
        )
        embed.add_field(
            name="Calendar Channel Not Found",
            value="A **#Calendar** channel does not exist in this server. Please create one to use calendar commands.",
            inline=False
        )
        await message.channel.send(embed=embed)
        return
    
    if not args.strip():
        embed = discord.Embed(
            title="Remove Event Error",
            color=discord.Color.red()
        )
        embed.add_field(
            name="Missing Arguments",
            value="Usage: `-removeevent [YYYY-MM-DD]`\n"
                  "Example: `-removeevent 2025-12-25`",
            inline=False
        )
        await message.channel.send(embed=embed)
        return
    
    date_str = args.strip()
    username = message.author.name
    
    # Validate date format
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        embed = discord.Embed(
            title="Remove Event Error",
            color=discord.Color.red()
        )
        embed.add_field(
            name="Invalid Date Format",
            value="Date must be in format: YYYY-MM-DD\n"
                  "Example: 2025-12-25 for December 25, 2025",
            inline=False
        )
        await message.channel.send(embed=embed)
        return
    
    # Remove event from database
    success = removeCalendarEvent(sqldb, date_str, username)
    
    if success:
        embed = discord.Embed(
            title="Event Removed",
            color=discord.Color.green()
        )
        embed.add_field(
            name="Date",
            value=date_str,
            inline=True
        )
        embed.add_field(
            name="User",
            value=username,
            inline=True
        )
        await calendar_channel.send(embed=embed)
        
        # Send confirmation to user
        confirmation = discord.Embed(
            title="Event Removed",
            color=discord.Color.green()
        )
        confirmation.add_field(
            name="Status",
            value=f"Your event on {date_str} has been removed from #Calendar",
            inline=False
        )
        await message.channel.send(embed=confirmation)
    else:
        embed = discord.Embed(
            title="Remove Event Error",
            color=discord.Color.red()
        )
        embed.add_field(
            name="No Event Found",
            value=f"Could not find an event for {username} on {date_str}",
            inline=False
        )
        await message.channel.send(embed=embed)


async def helpCalendar(message):
    """
    Display help information for calendar commands.
    
    Args:
        message (discord.Message): The Discord message object
    """
    # Find the Calendar channel in the guild
    calendar_channel = None
    for channel in message.guild.text_channels:
        if channel.name.lower() == "calendar":
            calendar_channel = channel
            break
    
    # If no Calendar channel exists, inform the user
    if calendar_channel is None:
        embed = discord.Embed(
            title="Calendar Help Error",
            color=discord.Color.red()
        )
        embed.add_field(
            name="Calendar Channel Not Found",
            value="A **#Calendar** channel does not exist in this server. Please create one to use calendar commands.",
            inline=False
        )
        await message.channel.send(embed=embed)
        return
    
    embed = discord.Embed(
        title="Calendar Help",
        color=discord.Color.blurple()
    )
    embed.add_field(
        name="-calendar",
        value="Display the current month's calendar",
        inline=False
    )
    embed.add_field(
        name="-calendar [month]",
        value="Display calendar for a specific month (current year)\n"
              "Example: `-calendar january` or `-calendar 1`",
        inline=False
    )
    embed.add_field(
        name="-calendar [month] [year]",
        value="Display calendar for a specific month and year\n"
              "Examples: `-calendar january 2025` or `-calendar 1 2025`",
        inline=False
    )
    embed.add_field(
        name="-addevent [date] [description]",
        value="Add an event to a single date\n"
              "Format: `-addevent YYYY-MM-DD Event Name`\n"
              "Example: `-addevent 2025-12-25 Birthday Party`\n"
              "Description is optional",
        inline=False
    )
    embed.add_field(
        name="-addeventrange [start] [end] [description]",
        value="Add an event to a range of dates\n"
              "Format: `-addeventrange YYYY-MM-DD YYYY-MM-DD Event Name`\n"
              "Example: `-addeventrange 2025-12-20 2025-12-25 Holiday Break`\n"
              "Maximum range: 365 days. Description is optional",
        inline=False
    )
    embed.add_field(
        name="-removeevent [date]",
        value="Remove your event from a specific date\n"
              "Format: `-removeevent YYYY-MM-DD`\n"
              "Example: `-removeevent 2025-12-25`",
        inline=False
    )
    embed.add_field(
        name="Supported Month Formats",
        value="Full names: january, february, march, etc.\n"
              "Numbers: 1-12",
        inline=False
    )
    
    await calendar_channel.send(embed=embed)
    
    # Send confirmation to user
    confirmation = discord.Embed(
        title="Calendar Help Posted",
        color=discord.Color.blurple()
    )
    confirmation.add_field(
        name="Status",
        value="Calendar help has been posted to #Calendar",
        inline=False
    )
    await message.channel.send(embed=confirmation)
