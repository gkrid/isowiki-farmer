<VirtualHost *:80>
    ServerName $(animal_name).$(farmer_domain)
    RewriteEngine On
    RewriteCond %{HTTPS}  !=on
    RewriteRule ^/?(.*) https://%{SERVER_NAME}/$1 [R,L]
</VirtualHost>

<VirtualHost *:443>
    ServerAdmin admin@$(farmer_domain)
    ServerName $(animal_name).$(farmer_domain)

    # SSL configuration
    $(ssl_include)
    SSLCertificateFile	$(ssl_certificate_file)
    SSLCertificateKeyFile $(ssl_certificate_key_file)

    # Encoded slashes need to be allowed
    AllowEncodedSlashes NoDecode

    # Container uses a unique non-signed certificate
    SSLProxyEngine On
    SSLProxyVerify None
    SSLProxyCheckPeerCN Off
    SSLProxyCheckPeerName Off

    # keep the host
    ProxyPreserveHost On

    # pod jaki port ma kierować (ip+nr portu)
     <Location />
                ProxyPass http://127.0.0.1:$(port)/
                ProxyPassReverse http://127.0.0.1:$(port)/
     </Location>
</VirtualHost>
