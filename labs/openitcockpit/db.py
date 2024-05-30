import sqlite3
import argparse
import os
import re

# Reference: https://stackoverflow.com/a/58138810
def escapeString(s):
	s = s.replace("\"", "\"\"")
	s = s.replace("\'", "\'\'")
	return s

class sqlDB(object):
	"""docstring for sqlDB"""
	def __init__(self, database):
		self.database = database
		
	def create_connection(self):
		conn = None
		try:
			conn = sqlite3.connect(self.database)
		except Exception as e:
			print(e)
		return conn

	def create_db(self):
		conn = self.create_connection()
		create_table = ("CREATE TABLE IF NOT EXISTS content(\n"
		"id integer PRIMARY KEY,\n"
		"location text NOT NULL,\n"
		"content blob);")
		try:
			c = conn.cursor()
			c.execute(create_table)
		except Exception as e:
			print(e)

	def get_content(self, args):
		conn = self.create_connection()
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
		except Exception as e:
			print(e)

	def insert_content(self, args):
		conn = self.create_connection()
		location = args[0]
		content = args[1]

		content = escapeString(content)
		location = escapeString(location)

		print(f"Inserting with location: {location}")
		command = ("INSERT INTO content\n"
		"(location, content) VALUES")
		command += "(\"" + location + "\",\"" + content + "\")"

		try:
			c = conn.cursor()
			c.execute(command)
			conn.commit()
		except Exception as e:
			print(e)

	def get_locations(self):
		conn = self.create_connection()
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
		except Exception as e:
			print(e)

def main():
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

	database = r"html_pages.db"
	db_obj = sqlDB(database)

	print()
	if (args.create):
		print("[+] Creating Database")
		db_obj.create_db()
	elif (args.insert):
		if(args.location is None and args.content is None):
			parser.error("--insert requires --location, --content.")
		else:
			print("[+] Inserting Data")
			db_obj.insert_content((args.location, args.content))
	elif (args.get):
		if(args.location is None):
			parser.error("--get requires --location, --content.")
		else:
			print("[+] Getting Content")
			db_obj.get_content((args.location,))
	if (args.getLocations):
		print("[+] Getting All Locations")
		db_obj.get_locations()

if __name__ == '__main__':
	main()