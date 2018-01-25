# Overview

## Initial Setup

### trust the cert
```
sudo security add-trusted-cert -d -r trustRoot \
        -k /Library/Keychains/System.keychain certs/probcomp.rootCA.pem
```
### add /etc/hosts entry (if you don't already have one)
```
echo "127.0.0.1 bayesrest.probcomp.dev" | sudo tee -a /etc/hosts
```

### start the app
```
docker-compose up
```

Service is accessible at `https://bayesrest.probcomp.dev:8443`
