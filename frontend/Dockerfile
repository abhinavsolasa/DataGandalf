FROM node:20 AS base
SHELL ["/bin/bash", "-c"]
WORKDIR /frontend
ENV NEXT_TELEMETRY_DISABLED 1

# Install dependencies, run dev server. 
FROM base AS dev-runner
COPY package.json package-lock.json ./
RUN npm install
COPY . .
EXPOSE 3000
CMD ["npm", "run", "dev"]


# # Install dependencies.
# FROM base AS deps
# COPY package.json package-lock.json ./
# RUN npm install

# # Build project.
# FROM base AS builder
# COPY --from=deps /frontend/node_modules ./node_modules
# COPY . .
# RUN npm build

# # Production image.
# FROM base AS runner
# ENV NODE_ENV production
# COPY --from=builder /app/public ./public
# COPY --from=builder /app/.next/standalone ./
# COPY --from=builder /app/.next/static ./.next/static

# ENV HOSTNAME "0.0.0.0"
# ENV PORT 3000
# EXPOSE 3000
# CMD ["node", "server.js"]
