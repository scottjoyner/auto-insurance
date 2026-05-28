FROM node:18-alpine

WORKDIR /app

COPY package*.json ./
COPY scripts/ ./scripts/
COPY hardhat.config.* ./
COPY contracts/ ./contracts/

RUN npm ci --production

CMD ["npx", "hardhat", "node"]
