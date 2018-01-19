#! /bin/bash

export DOMAIN=probcomp.dev
OPENSSL=/usr/bin/openssl
if [[ $OSTYPE == darwin* ]]; then
  OPENSSL=/usr/local/opt/openssl/bin/openssl
fi

${OPENSSL} req -newkey rsa:2048 -keyout "$DOMAIN".key -sha256 -new -nodes -out "$DOMAIN".csr \
  -subj "/C=US/ST=Massachusetts/L=Cambridge/O=probcomp/CN=$DOMAIN/emailAddress=probcomp-admins@googlegroups.com"
${OPENSSL} x509 -req -in $DOMAIN.csr -CAkey probcomp.rootCA.key -CA probcomp.rootCA.pem \
  -CAcreateserial -out $DOMAIN.crt -days 1825 -sha256 -extfile v3.ext
rm probcomp.srl
unset DOMAIN
