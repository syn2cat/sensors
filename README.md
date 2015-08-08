# Level2's sensors

----
## Installation

----
### Requirements
* docker
* docker-compose
* web server with uwsgi support

----
### Application configuration

1. Create mongodb data container: `docker create --name=sensors-mongodb-data mongo`
2. Set basic ACL on mongodb:
  a. `docker start sensors-mongodb-data`
  b. `docker exec -it sensors-mongodb-data mongo particule`
  c. > `db.createUser({user: "sensors", pwd: "<password>", roles: [ "dbOwner" ]});`
  d. > `exit`
  e. `docker stop sensors-mongodb-data`
3. Create data container: `docker create --name=sensors-data -v /etc/l2-sensors debian`
4. Create configuration file in data container: `docker run -it --rm --volumes-from sensors-data busybox vi /etc/l2-sensors/conf.yml`
Example of conf.yml

    devices:
      - id: <ID>
        variables:
          - temperatureC
          - humidity
          - pressure
    db:
      mongo: {username: sensors, password: <password>}
    token: <token>

### Reverse proxy configuration

Example of configuration for nginx

    server {
        listen 443 ssl;
        server_name  sensors.level2.lu;

        location / {
            include uwsgi_params;
            uwsgi_pass 172.17.42.1:3031;
        }
    }


----
## Usage
* To start (in project root directory): `docker-compose up -d`
