Trust the cert with:

```
sudo security add-trusted-cert -d -r trustRoot \
        -k /Library/Keychains/System.keychain probcomp.rootCA.pem
```
