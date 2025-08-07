# apps/ui/Dockerfile

FROM node:20

WORKDIR /app

COPY package*.json ./
ENV npm_config_cache=/tmp/.npm
RUN npm install --omit=dev  # 👈

COPY . .

EXPOSE 3000
CMD ["npm", "run", "dev"]
