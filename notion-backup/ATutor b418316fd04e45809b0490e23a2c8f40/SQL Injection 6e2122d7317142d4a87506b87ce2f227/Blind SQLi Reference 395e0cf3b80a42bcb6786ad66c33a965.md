# Blind SQLi Reference

Blind SQLi attacks are used when no data is transferred from the web application as the result of the injected payload. Attackers have to inject queries that ask YES and NO questions to the database and construct the sought information based on the question responses. 

- Boolean-based injections: Attackers able to infer the outcome of the Boolean SQL payload by observing differences in HTTP response content.
- Time-based injections: Only way to infer information is introducing artificial query execution delays in the injected queries with database-native functions like MySQL `sleep`