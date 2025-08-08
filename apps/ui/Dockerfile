# apps/ui/Dockerfile

# syntax=docker/dockerfile:1.7
FROM node:20
WORKDIR /app

COPY package*.json ./
RUN npm ci             # dev deps included

COPY . .
EXPOSE 3000
CMD ["npm","run","dev"]
