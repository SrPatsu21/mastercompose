# Usar Java 21 oficial, compatível com seu Neoforge
FROM openjdk:21

# Criar diretório do servidor
WORKDIR /data

# Copiar todos os arquivos necessários
COPY ./world ./world
COPY ./whitelist.json ./whitelist.json
COPY ./data ./data
COPY ./config ./config
COPY ./libraries ./libraries
COPY ./user_jvm_args.txt ./user_jvm_args.txt
COPY ./neoforge-21.1.214-installer.jar ./neoforge-server.jar

# Definir comando padrão para iniciar o Neoforge
CMD ["java", "-Xms2G", "-Xmx6G", "-jar", "/data/neoforge-server.jar", "nogui"]
