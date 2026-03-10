import sqlite3
conn = sqlite3.connect('database.db')
cursor = conn.cursor()

table_name = "state_button_data"
column_to_update = "uploaded_mining"
new_value =  0
datetime_column = "datetime" # The column containing datetime values
start_datetime = "2025-10-27 13:00:00" # Start of your datetime range
end_datetime = "2025-10-27 17:45:00"   # End of your datetime range

sql_query = f"""
UPDATE {table_name}
SET {column_to_update} = ?
WHERE {datetime_column} BETWEEN ? AND ?;
"""

cursor.execute(sql_query, (new_value, start_datetime, end_datetime))
conn.commit()
cursor.close()
conn.close()
