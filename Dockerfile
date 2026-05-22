FROM hugomods/hugo:latest AS builder
WORKDIR /src
COPY . .
RUN hugo --minify

FROM nginx:1.27-alpine
COPY --from=builder /src/public /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
# nginx по умолчанию не знает расширение .md — учим отдавать его как text/markdown
RUN sed -i 's#^}#    text/markdown                          md;\n}#' /etc/nginx/mime.types
EXPOSE 80
