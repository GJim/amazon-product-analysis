FROM node:20-alpine AS builder

WORKDIR /app

# Copy package.json and package-lock.json/yarn.lock
COPY frontend/package.json frontend/yarn.lock ./

# Install dependencies
RUN yarn install

# Copy the rest of the application
COPY frontend/ ./

# Build the application
RUN yarn build

# Production image
FROM nginx:alpine

# Copy the built files to nginx
COPY --from=builder /app/out /usr/share/nginx/html

# Copy nginx configuration
COPY containers/frontend/nginx.conf /etc/nginx/conf.d/default.conf

# Expose port 80
EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
