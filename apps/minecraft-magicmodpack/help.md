https://help.akliz.net/docs/setup-a-whitelist-for-your-minecraft-server#:~:text=In%20your%20console%2C%20type%3A%20whitelist,add%20to%20the%20white%20list.


docker exec -i mc rcon-cli


https://docker-minecraft-server.readthedocs.io/en/latest/


wget -O ./apps/minecraft-magicmodpack/neoforge-21.1.214-installer.jar https://maven.neoforged.net/releases/net/neoforged/neoforge/21.1.214/neoforge-21.1.214-installer.jar
cd ./apps/minecraft-magicmodpack/
java -jar neoforge-21.1.214-installer.jar --installServer
cd ../..
