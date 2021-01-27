# ISL-BCFL

## kvstore scable test
```bash=
docker-compose -f docker-compose-kvtest.yml up --scale nodes=5

docker-compose -f docker-compose-kvtest.yml down -v
```