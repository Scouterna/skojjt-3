call gcloud config set project skojjt-3

if "%VIRTUAL_ENV%" == "" (call .\env\Scripts\activate.bat)

set GOOGLE_APPLICATION_CREDENTIALS=C:\Users\marti\AppData\Roaming\gcloud\skojjt-3-9fa7c72a34a7.json
set DATASTORE_EMULATOR_HOST=localhost:8081
set REDIS_CACHE_URL=redis://localhost:6379
start run_datastore.bat
start run_redis.bat

code .

