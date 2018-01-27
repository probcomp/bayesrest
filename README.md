# Overview

## Initial Setup

### setup probcomp/nginx-proxy repo

Follow the instructions at https://github.com/probcomp/nginx-proxy -- nginx-proxy must be running before you can access bayesrest.

### add /etc/hosts entry (if you don't already have one)
```
echo "127.0.0.1 bayesrest.probcomp.dev" | sudo tee -a /etc/hosts
```

### start the app
```
docker-compose up
```

Service is accessible at `https://bayesrest.probcomp.dev:8443`
