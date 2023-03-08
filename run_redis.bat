rem use docker to run an instance of docker (Redis is not supported on windows)
docker start skojjt-redis
IF %ERRORLEVEL% NEQ 0 (
docker run --name skojjt-redis -p 6379:6379 -d redis redis-server --save 60 1 --loglevel verbose
)

rem for production env:
rem gcloud redis instances create --project=skojjt-3  redis-instance-skojjt --tier=basic --size=1 --region=europe-west1 --redis-version=redis_6_x --network=projects/skojjt-3/global/networks/default --connect-mode=DIRECT_PEERING --maintenance-window-day=SATURDAY --maintenance-window-hour=0
rem gcloud redis instances describe redis-instance-skojjt --region=europe-west1
rem -> use host and port to set:
rem export REDIS_CACHE_URL=10.220.95.155:6379