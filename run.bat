set DATASTORE_EMULATOR_HOST=localhost:8081
set REDIS_CACHE_URL=redis://localhost:6379
start run_redis.bat
start run_datastore.bat

python main.py