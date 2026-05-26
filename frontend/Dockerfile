# Stage 1: Build the React application
FROM node:18-alpine as build-stage

WORKDIR /app

# Copy package configuration files
COPY package.json package-lock.json ./

# Install dependencies
RUN npm ci

# Copy all source files
COPY . .

# Set Vite API URL to proxy endpoint /api
ENV VITE_API_URL=/api

# Build for production
RUN npm run build

# Stage 2: Serve the application with Nginx
FROM nginx:stable-alpine as production-stage

# Copy custom Nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copy build files from the build-stage to Nginx public folder
COPY --from=build-stage /app/dist /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
