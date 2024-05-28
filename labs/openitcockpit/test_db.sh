rm sqlite.db

python3 db.py --create
python3 db.py --insert --location "http://test.txt" --content "hello"
python3 db.py --insert --location "http://test2.txt" --content "hello2"
python3 db.py --insert --location "http://test3.txt" --content "hello3"

python3 db.py --get --location "http://test.txt"
python3 db.py --get --location "http://test4.txt"
python3 db.py --getLocations