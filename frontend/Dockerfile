FROM node:20-slim AS builder

WORKDIR /app

# Install dependencies
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci

# Copy the application code
COPY frontend/ .
RUN npm run build

# Runtime
FROM node:20-slim

WORKDIR /app

#copy only the output from the builder and the dependences
COPY --from=builder /app/.output ./.output

# Expose the port the app runs on
EXPOSE 3000

# Command to run the application
CMD ["node", ".output/server/index.mjs"]
