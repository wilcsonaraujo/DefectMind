FROM node:20-slim AS builder

WORKDIR /app

# Install dependencies
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci

# Copy the application code
COPY frontend/ .
RUN npm run build

# Runtime
FROM nginx:alpine

#copy the built files from the builder stage
COPY --from=builder /app/dist /usr/share/nginx/html
COPY frontend/nginx.conf /etc/nginx/conf.d/default.conf

# Expose the port the app runs on
EXPOSE 80

# Command to run the application
CMD ["nginx", "-g", "daemon off;"]
