import sqlite3
import argparse
import os

def create_connection(db_file):
	conn = None
	try:
		conn = sqlite3.connect(db_file)
	except Error as e:
		print(e)
	return conn

def create_db(conn):
	create_table = ("CREATE TABLE IF NOT EXISTS content(\n"
	"id integer PRIMARY KEY,\n"
	"location text NOT NULL,\n"
	"content blob);")
	try:
		c = conn.cursor()
		c.execute(create_table)
	except Error as e:
		print(e)

def get_content(conn, args):
	location = args[0]
	print(f"Querying data with key {location}")
	command = ("SELECT location,content from content\n"
	f"WHERE location=\"{location}\"")

	try:
		c = conn.cursor()
		c.execute(command)
		res = c.fetchall()
		res = [i[1] for i in res]
		if len(res) == 0:
			print("No items found!")
		else:
			print("Printing results....")
			for r in res:
				print(r)
		return res
	except Error as e:
		print(e)

def insert_content(conn, args):
	location = args[0]
	content = args[1]
	print(f"Inserting with location: {location}")
	command = ("INSERT INTO content\n"
	"(location, content) VALUES"
	f"(\"{location}\", \"{content}\")")
	print(command)

	try:
		c = conn.cursor()
		c.execute(command)
	except Error as e:
		print(e)

def get_locations(conn):
	print("Listing locations.....")
	command = ("SELECT location FROM content")

	try:
		c = conn.cursor()
		c.execute(command)
		res = c.fetchall()
		res = [i[0] for i in res]
		if len(res) == 0:
			print("No items found!")
		else:
			print("Printing results....")
			for r in res:
				print(r)
		return res
	except Error as e:
		print(e)

def main():
	database = r"sqlite.db"
	parser = argparse.ArgumentParser()
	group = parser.add_mutually_exclusive_group(required=True)
	group.add_argument('--create','-c', help='Create Database', action='store_true')
	group.add_argument('--insert','-i', help='Insert Content', action='store_true')
	group.add_argument('--get','-g', help='Get Content', action='store_true')
	group.add_argument('--getLocations','-l', help='Get all Locations', 
	action='store_true')
	parser.add_argument('--location','-L')
	parser.add_argument('--content','-C')
	args = parser.parse_args()

	conn = create_connection(database)
	print()
	if (args.create):
		print("[+] Creating Database")
		create_db(conn)
	elif (args.insert):
		if(args.location is None and args.content is None):
			parser.error("--insert requires --location, --content.")
		else:
			print("[+] Inserting Data")
			insert_content(conn, (args.location, args.content))
		conn.commit()
	elif (args.get):
		if(args.location is None):
			parser.error("--get requires --location, --content.")
		else:
			print("[+] Getting Content")
			get_content(conn, (args.location,))
	if (args.getLocations):
		print("[+] Getting All Locations")
		get_locations(conn)

if __name__ == '__main__':
	main()