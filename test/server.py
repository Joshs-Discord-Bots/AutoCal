"""
SERVER.PY - THE SERVER

Nelio ALVES FERNANDES (10525748)
Joshua HOLLANDER (10526178)
"""

import xmlrpc.server
from statistics import mean
import re
import sqlite3

# -------------------------- SEVER SETTINGS --------------------------

port = 3000
address = "localhost" # Change address to access remote server
server = xmlrpc.server.SimpleXMLRPCServer((address, port), logRequests=True, allow_none=True)
db = "database.db"

# ------------------------ TWO-TIER FUNCTIONS ------------------------

def validate_units(units):
    # Check if units is a list
    if not isinstance(units, list): return False
    # Check if length of units list is between 12 and 30
    if len(units) < 12 or len(units) > 30: return False
    # Check if units contains only lists
    if not all([isinstance(e, list) for e in units]): return False
    for unit in units:
        # If unit does not contain 2 elements
        if len(unit) != 2: return False
        # If unit code not ABC1234 format
        if not re.match(r"^[A-Z]{3}[0-9]{4}$", unit[0]): return False
        # If mark is not a float between 0 and 100
        if not isinstance(unit[1], float) or unit[1] < 0 or unit[1] > 100: return False
    return True

def hepa_evaluation(units):
    # If the units are not valid
    if not validate_units(units): return

    # "displaying individual scores (or <unit_code, mark> pairs) on the screen in their input order"
    for unit in units:
        print(f"Unit: {unit[0]} | {unit[1]}%")
    
    results = {}
    
    units, marks = zip(*units) # Separate marks and units into two lists
    # Calculate course average (avarage of all marks)
    results["course_average"] = round(mean(marks), 2)
    # Calculate average of top 8 marks
    results["octad_average"] = round(mean(sorted(marks, reverse=True)[:8]), 2)

    # If 6 or more "Fails" (Marks under 50%)
    if sum(map(lambda mark : mark < 50, marks)) >= 6:
        results["evaluation"] = "6 or more Fails! DOES NOT QUALIFY FOR HONORS STUDY!"
    elif results["course_average"] >= 70:
        results["evaluation"] = "QUALIFIED FOR HONORS STUDY!"
    elif results["course_average"] < 70 and results["course_average"] >= 65 and results["octad_average"] < 80:
        results["evaluation"] = "MAY HAVE GOOD CHANCE! Need further assessment!"
    elif results["course_average"] < 65 and results["octad_average"] >= 80:
        results["evaluation"] = "MAY HAVE A CHANCE! Must be carefully reassessed and get the coordinator's permission!"
    else:
        results["evaluation"] = "DOES NOT QUALIFY FOR HONORS STUDY!"

    return results

# ----------------------- THREE-TIER FUNCTIONS -----------------------

def validate_login(student_id, password):
    # Check id and password formats
    if not re.match(r"^[0-9]{8}$", student_id): return # Student ID: 8 digits
    if not re.match(r"^[A-z0-9!\"#$%&()*\\+,\-./:;<=>?@\[\]^_`{|}~]{6,12}$", password): return # Password: 8-12 unicode chars

    connection = sqlite3.connect(db)
    if connection:
        if connection.cursor().execute(f"SELECT * FROM STUDENT WHERE STUDENT_ID='{student_id}' AND PASSWORD='{password}'").fetchone():
            connection.close()
            return True

    else: print(f'Failed to establish a connection to "{db}"')
    connection.close()
    return False

def get_eou_units(student_id):
    results = []
    connection = sqlite3.connect(db)
    if connection:
        units = connection.cursor().execute(f"SELECT * FROM RESULTS WHERE STUDENT_ID='{student_id}'").fetchall()
        if units:
            # Format units into ["unit_id", "score"]
            for unit in units:
                results.append([unit[2], unit[3]])
    
    else: print(f'Failed to establish a connection to "{db}"')
    connection.close()
    return results
    
# ---------------------------- RUN SERVER ----------------------------

def main():
    # Register server functions
    functions = [
        # 2-Tier
        validate_units,
        hepa_evaluation,
        # 3-Tier
        validate_login,
        get_eou_units,
    ]
    for function in functions:
        server.register_function(function)

    # Run the server
    try:
        print("Server Running...")
        server.serve_forever()
    except:
        print("Exiting...")

if __name__ == "__main__":
    main()