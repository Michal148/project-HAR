FROM redis:6.2.0

COPY ./redis.conf  /usr/local/etc/redis/redis.conf
COPY ./redis-cert.pem /usr/local/etc/redis/redis.crt
COPY ./redis-key.pem /usr/local/etc/redis/redis.key
COPY ./CA.pem /usr/local/etc/redis/ca.crt

RUN chown -R redis:redis /usr/local/etc/redis
USER root
CMD [ "redis-server", "/usr/local/etc/redis/redis.conf"]