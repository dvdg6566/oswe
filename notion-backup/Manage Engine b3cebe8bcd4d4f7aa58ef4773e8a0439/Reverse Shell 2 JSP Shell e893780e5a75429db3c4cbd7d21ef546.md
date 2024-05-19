# Reverse Shell 2: JSP Shell

[webshell/fuzzdb-webshell/jsp/CmdServlet.java at master · tennc/webshell (github.com)](https://github.com/tennc/webshell/blob/master/fuzzdb-webshell/jsp/CmdServlet.java)

We can inject a JSP webshell into the working directory `C:\Program Files (x86)\ManageEngine\AppManager12\working`. However, visiting our shellcode in the webserver gives us a blank page.

As such, we look for the log files of the webserver, which can be found at `C:\Program Files (x86)\ManageEngine\AppManager12\logs`. We find the file `stderr.txt.1`, which contains recent STDERR logs. 

![Untitled](Reverse%20Shell%202%20JSP%20Shell%20e893780e5a75429db3c4cbd7d21ef546/Untitled.png)

Stderr logs:

```python
# \logs\stderr
[25 Feb 2024 10:28:18:705] SYS_ERR: Caused by: java.lang.NoSuchMethodError: org.eclipse.jdt.internal.compiler.Compiler.<init>(Lorg/eclipse/jdt/internal/compiler/env/INameEnvironment;Lorg/eclipse/jdt/internal/compiler/IErrorHandlingPolicy;Lorg/eclipse/jdt/internal/compiler/impl/CompilerOptions;Lorg/eclipse/jdt/internal/compiler/ICompilerRequestor;Lorg/eclipse/jdt/internal/compiler/IProblemFactory;)V
[25 Feb 2024 10:28:18:705] SYS_ERR: 	at org.apache.jasper.compiler.JDTCompiler.generateClass(JDTCompiler.java:442)
[25 Feb 2024 10:28:18:705] SYS_ERR: 	at org.apache.jasper.compiler.Compiler.compile(Compiler.java:378)
[25 Feb 2024 10:28:18:705] SYS_ERR: 	at org.apache.jasper.compiler.Compiler.compile(Compiler.java:353)
[25 Feb 2024 10:28:18:705] SYS_ERR: 	at org.apache.jasper.compiler.Compiler.compile(Compiler.java:340)
[25 Feb 2024 10:28:18:705] SYS_ERR: 	at org.apache.jasper.JspCompilationContext.compile(JspCompilationContext.java:644)
[25 Feb 2024 10:28:18:705] SYS_ERR: 	at org.apache.jasper.servlet.JspServletWrapper.service(JspServletWrapper.java:358)
[25 Feb 2024 10:28:18:705] SYS_ERR: 	at org.apache.jasper.servlet.JspServlet.serviceJspFile(JspServlet.java:389)
[25 Feb 2024 10:28:18:705] SYS_ERR: 	at org.apache.jasper.servlet.JspServlet.service(JspServlet.java:333)
```

```python
# \logs\stderr.txt.1
Position: 75
[25 Feb 2024 10:17:28:551] SYS_ERR: 	at org.postgresql.core.v3.QueryExecutorImpl.receiveErrorResponse(QueryExecutorImpl.java:2102)
[25 Feb 2024 10:17:28:551] SYS_ERR: 	at org.postgresql.core.v3.QueryExecutorImpl.processResults(QueryExecutorImpl.java:1835)
[25 Feb 2024 10:17:28:551] SYS_ERR: 	at org.postgresql.core.v3.QueryExecutorImpl.execute(QueryExecutorImpl.java:257)
[25 Feb 2024 10:17:28:551] SYS_ERR: 	at org.postgresql.jdbc2.AbstractJdbc2Statement.execute(AbstractJdbc2Statement.java:500)
[25 Feb 2024 10:17:28:551] SYS_ERR: 	at org.postgresql.jdbc2.AbstractJdbc2Statement.executeWithFlags(AbstractJdbc2Statement.java:374)
[25 Feb 2024 10:17:28:551] SYS_ERR: 	at org.postgresql.jdbc2.AbstractJdbc2Statement.executeQuery(AbstractJdbc2Statement.java:254)
[25 Feb 2024 10:17:28:551] SYS_ERR: 	at com.adventnet.appmanager.db.AMConnectionPool.executeQueryStmt(AMConnectionPool.java:156)
[25 Feb 2024 10:17:28:551] SYS_ERR: 	at com.adventnet.appmanager.server.archiver.AMDataArchiverImpl.getTimeStamps(AMDataArchiverImpl.java:758)
[25 Feb 2024 10:17:28:551] SYS_ERR: 	at com.adventnet.appmanager.server.archiver.AMDataArchiverImpl.archiveData(AMDataArchiverImpl.java:433)
[25 Feb 2024 10:17:28:551] SYS_ERR: 	at com.adventnet.appmanager.server.archiver.AMDataArchiverProcess.run(AMDataArchiverProcess.java:162)
[25 Feb 2024 10:17:28:551] SYS_ERR: 	at com.adventnet.management.scheduler.WorkerThread.run(WorkerThread.java:84)
[25 Feb 2024 10:17:28:551] SYS_ERR: org.postgresql.util.PSQLException: ERROR: relation "am_mongodb_5feb24" does not exist
  Position: 75
[25 Feb 2024 10:17:28:551] SYS_ERR: 	at org.postgresql.core.v3.QueryExecutorImpl.receiveErrorResponse(QueryExecutorImpl.java:2102)
[25 Feb 2024 10:17:28:551] SYS_ERR: 	at org.postgresql.core.v3.QueryExecutorImpl.processResults(QueryExecutorImpl.java:1835)
[25 Feb 2024 10:17:28:551] SYS_ERR: 	at org.postgresql.core.v3.QueryExecutorImpl.execute(QueryExecutorImpl.java:257)
[25 Feb 2024 10:17:28:551] SYS_ERR: 	at org.postgresql.jdbc2.AbstractJdbc2Statement.execute(AbstractJdbc2Statement.java:500)
[25 Feb 2024 10:17:28:551] SYS_ERR: 	at org.postgresql.jdbc2.AbstractJdbc2Statement.executeWithFlags(AbstractJdbc2Statement.java:374)
[25 Feb 2024 10:17:28:551] SYS_ERR: 	at org.postgresql.jdbc2.AbstractJdbc2Statement.executeQuery(AbstractJdbc2Statement.java:254)
[25 Feb 2024 10:17:28:551] SYS_ERR: 	at com.adventnet.appmanager.db.AMConnectionPool.executeQueryStmt(AMConnectionPool.java:156)
[25 Feb 2024 10:17:28:551] SYS_ERR: 	at com.adventnet.appmanager.server.archiver.AMDataArchiverImpl.getTimeStamps(AMDataArchiverImpl.java:758)
[25 Feb 2024 10:17:28:551] SYS_ERR: 	at com.adventnet.appmanager.server.archiver.AMDataArchiverImpl.archiveData(AMDataArchiverImpl.java:433)
[25 Feb 2024 10:17:28:551] SYS_ERR: 	at com.adventnet.appmanager.server.archiver.AMDataArchiverProcess.run(AMDataArchiverProcess.java:162)

```