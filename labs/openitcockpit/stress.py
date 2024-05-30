# Stress testing code
import db
x = db.sqlDB("test.db")
x.create_db()
x.insert_content(("a\"", "b"))