FROM node:20-alpine

WORKDIR /app

ENV NEXT_TELEMETRY_DISABLED=1

ARG NEXT_PUBLIC_CRISOL_API_URL=https://crisol-api.jollysmoke-c46778ba.eastus.azurecontainerapps.io
ENV NEXT_PUBLIC_CRISOL_API_URL=$NEXT_PUBLIC_CRISOL_API_URL

COPY package*.json ./

RUN if [ -f package-lock.json ]; then npm ci --include=dev; else npm install --include=dev; fi

COPY . .

RUN npm run build

ENV NODE_ENV=production

EXPOSE 3000

CMD ["npx", "next", "start", "--hostname", "0.0.0.0", "--port", "3000"]
