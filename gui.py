from tkinter import *
from tkinter import ttk
import sqlite3
try:
    import configparser
except ImportError:
    import ConfigParser as configparser
import os

try:
	sqlite_connection = sqlite3.connect("ypsonas.db")
	cursor = sqlite_connection.cursor()
	print("База данных создана и успешно подключена!")

	sqlite_select_query = "select sqlite_version();"
	cursor.execute(sqlite_select_query)
	version = cursor.fetchall()
	print("Версия базы данных SQLite: ", version)
except sqlite3.Error as error:
	print("Ошибка при подключении базы данных: ", error)

def readConfig(path):
	if not os.path.exists(path):
		createConfig(path)

	config = configparser.ConfigParser()
	config.read(path)
	data = {
		"database_created": config.get("Settings", "database_created"),
		"counter_player": config.get("Team", "counter_player")
	}
	return data

def readPlayers():
	try:
		query = '''SELECT * FROM players'''
		cursor.execute(query)
		return cursor.fetchall()
	except sqlite3.Error as error:
		print("Не удалось загрузить данные игроков из Базы Данных!")
		print("Ошибка SQLite: ", error)

def main():
	settings = readConfig("settings.ini")
	settings['counter_player'] = int(settings['counter_player'])

	root = Tk()
	frm = ttk.Frame(root, padding=10)
	frm.grid()

	all_players = readPlayers()
	i = 1
	ttk.Label(frm, text="FC Krasava").grid(column=1, row=0)
	for player in all_players:
		ttk.Label(frm, text=player[1]).grid(column=0, row=i)
		ttk.Label(frm, text=player[2]).grid(column=1, row=i)
		ttk.Label(frm, text=player[3]).grid(column=2, row=i)
		i += 1

	ttk.Button(frm, text="Quit", command=root.destroy).grid(column=1, row=i)
	root.mainloop() 

if __name__ == "__main__":
	main()