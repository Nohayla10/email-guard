
FROM node:18-alpine as build

WORKDIR /app

COPY package*.json ./
RUN npm install --silent


COPY . .


RUN npm run build


FROM nginx:stable-alpine


COPY nginx/default.conf /etc/nginx/conf.d/default.conf


COPY --from=build /app/build /usr/share/nginx/html


EXPOSE 80

# Command to start Nginx in the foreground
CMD ["nginx", "-g", "daemon off;"]