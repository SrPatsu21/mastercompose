
# Help

- White list

<https://help.akliz.net/docs/setup-a-whitelist-for-your-minecraft-server#:~:text=In%20your%20console%2C%20type%3A%20whitelist,add%20to%20the%20white%20list.>

- Console

`docker exec -i mc rcon-cli`

- docs

<https://docker-minecraft-server.readthedocs.io/en/latest/>

- Download neoforge

```shell
wget -O ./apps/minecraft-magicmodpack/neoforge-21.1.214-installer.jar https://maven.neoforged.net/releases/net/neoforged/neoforge/21.1.214/neoforge-21.1.214-installer.jar
cd ./apps/minecraft-magicmodpack/
java -jar neoforge-21.1.214-installer.jar --installServer
cd ../..
```

- fix permission

```shell
sudo chown -R 1000:1000 ./apps/minecraft-magicmodpack
sudo chmod -R 775 ./apps/minecraft-magicmodpack
sudo chmod -R 777 ./apps/minecraft-magicmodpack/config
```
