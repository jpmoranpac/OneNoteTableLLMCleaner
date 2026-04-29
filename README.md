Implementation plan:

1. Ingest table format of text
2. Insert into SQLite database (cursor)
 - ID, content, status, result, retries (int), lastattempt (time)
3. Read Groq API key and select model
4. Lookup rate limits from model, noting both RPM and TPM; RPD, TPD.
 - https://console.groq.com/docs/rate-limits
5. Calculate optimal request strategy and schedule requests. Report to user expected time to completion.
6. Basic implementation: busy loop. Future extension: APScheduler

