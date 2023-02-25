# Import Library
from bs4 import BeautifulSoup
import requests
import sqlite3
try:
    import configparser
except ImportError:
    import ConfigParser as configparser
import os


backupMode = False # Если включён, то производится только резервное копирование
url = "https://www.transfermarkt.world/ypsonas-fc/startseite/verein/57870/saison_id/2022" # ФК Красава
#url = "https://www.transfermarkt.world/po-xylotymbou/startseite/verein/55927/saison_id/2022" #Ксилотимбу

headers = {
	"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
	"User-Agent": "Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36"
}

response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.text, "lxml")

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

def createBase():
	query = '''CREATE TABLE players (
			id INTEGER PRIMARY KEY,
			name TEXT,
			position TEXT,
			birthday TEXT,
			club TEXT);'''
	cursor.execute(query)
	sqlite_connection.commit()
	print("Таблица players создана!")

def createConfig(path):
	config = configparser.ConfigParser()
	config.add_section("Settings")
	config.set("Settings", "database_created", "1")
	config.set("Team", "counter_player", "0")

	with open(path, "w") as config_file:
		config.write(config_file)

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

def writeConfig(path, data):
	config = configparser.ConfigParser()
	config.read(path)
	config.set("Settings", "database_created", str(data['database_created']))
	config.set("Team", "counter_player", str(data['counter_player']))
	with open(path, "w") as config_file:
		config.write(config_file)

def AddPlayer(counter_player, data):
	try:
		query = '''INSERT INTO players 
				(id, name, position, birthday, club)
				VALUES (?, ?, ?, ?, ?)'''
		cursor.execute(query, (counter_player, data['name'], data['position'], data['birthday'], data['club']))
		sqlite_connection.commit()
	except sqlite3.Error as error:
		print("Не удалось добавить игрока в базу данных!")
		print("Ошибка SQLite: ", error)

def backupCopy():
	try:
	    sqlite_con = sqlite3.connect('ypsonas.db')
	    backup_con = sqlite3.connect('ypsonas_backup.db')
	    with backup_con:
	        sqlite_con.backup(backup_con)
	    print("Резервное копирование выполнено успешно")
	except sqlite3.Error as error:
	    print("Ошибка при резервном копировании: ", error)
	finally:
	    if(backup_con):
	        backup_con.close()
	        sqlite_con.close()

def main():
	#name_club = soup.find("h1", class_="data-header__headline-wrapper").text.strip()
	#print(name_club)
	if backupMode:
		backupCopy()
		return

	settings = readConfig("settings.ini")
	settings['counter_player'] = int(settings['counter_player'])
	if not int(settings['database_created']) == 1:
		createBase()
		settings['database_created'] = 1
		writeConfig("settings.ini", settings)

	positions = soup.find_all("table", class_="inline-table")
	for position in positions:
		player = {
		'name': position.find_next("span", class_="show-for-small").find_next("a").get("title"),
		'position': position.find_next("tr").find_next("tr").find_next("td").get_text(),
		'birthday': position.next.find_next('td', class_="zentriert").get_text(),
		'club': "FC Krasava"
		}
		AddPlayer(settings['counter_player'], player)
		settings['counter_player'] += 1
		writeConfig("settings.ini", settings)

if __name__ == "__main__":
	main()