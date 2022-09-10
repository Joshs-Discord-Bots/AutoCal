from secrets import choice
import sqlite3

connection = sqlite3.connect('calendar.db')

# Resets DB
try:
    connection.execute('DROP TABLE CALENDAR')
except:
    pass

# Table Creation
connection.execute('''
CREATE TABLE CALENDAR (
    BLOCK_ID        INTEGER         PRIMARY KEY AUTOINCREMENT,
    USER_ID         INTEGER         NOT NULL,
    WEEKDAY         NVARCHAR(9)     NOT NULL,
    START_TIME      TIME            NOT NULL,
    END_TIME        TIME            NOT NULL,
    CONSTRAINT CHK_Weekday CHECK (WEEKDAY IN ('monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday'))
)
''')

print('Database Created')