# Dockerfile para el backend del proyecto LYNX
FROM node:20-alpine

# Directorio de trabajo
WORKDIR /app

# Instalar dependencias para compilar bcrypt
RUN apk add --no-cache make gcc g++ python3

# Copiar archivos de configuración del proyecto
COPY package.json package-lock.json ./

# Instalar dependencias
RUN npm ci

# Reconstruir bcrypt para la arquitectura actual
RUN npm rebuild bcrypt --build-from-source

# Copiar el código fuente
COPY . .

# Puerto en el que se ejecutará la aplicación
EXPOSE 5000

# Comando para iniciar el servidor
CMD ["node", "index.js"] 