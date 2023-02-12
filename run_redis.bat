rem use docker to run an instance of docker (Redis is not supported on windows)
docker run --name skojjt-redis -p 6379:6379 -d redis redis-server --save 60 1 --loglevel warning