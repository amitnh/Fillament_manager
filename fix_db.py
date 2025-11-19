import sqlite3
conn = sqlite3.connect('filament_manager.db')
cursor = conn.cursor()
cursor.execute("UPDATE filaments SET color_hex = '#000000' WHERE id = 1")
conn.commit()
print("Updated ID 1 to Black")
conn.close()
