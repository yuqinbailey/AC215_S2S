#FROM node:14.5.0-alpine as build
FROM nginx:stable
WORKDIR /app
ENV PUBLIC_URL /


# Nginx wrapper to serve static files
COPY . /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]