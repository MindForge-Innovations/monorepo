#!/bin/bash

openstack server image create --name initial-state --wait mse-pi-services


aws s3 cp --endpoint-url=https://s3.pub1.infomaniak.cloud /Users/jeff/switchdrive/MSE_S2/PI/Doc_Hist/Grotius-dg s3://label-studio-data/ --recursive
aws s3 cp --endpoint-url=https://s3.pub1.infomaniak.cloud /Users/jeff/switchdrive/MSE_S2/PI/Doc_Hist/Puf-dng s3://label-studio-data/ --recursive
aws s3 cp --endpoint-url=https://s3.pub1.infomaniak.cloud /Users/jeff/switchdrive/MSE_S2/PI/Doc_Hist/Vattel-dg s3://label-studio-data/ --recursive

curl -X POST -H "X-Auth-Token: $OS_AUTH_TOKEN" \
  -H 'X-Container-Meta-Access-Control-Allow-Origin: https://mse-pi.pasche-net.ch' \
  https://s3.pub1.infomaniak.cloud/object/v1/AUTH_82aa75073b0845c286bc525b3309a448/label-studio-data

  curl -X POST -H "X-Auth-Token: $OS_AUTH_TOKEN" \
  -H 'X-Container-Meta-Access-Control-Allow-Origin: http://localhost' \
  https://s3.pub1.infomaniak.cloud/object/v1/AUTH_82aa75073b0845c286bc525b3309a448/label-studio-data

  curl -X POST -H "X-Auth-Token: $OS_AUTH_TOKEN" \
  -H 'X-Container-Meta-Access-Control-Allow-Origin: http://localhost' \
  https://label-studio-data.s3.pub1.infomaniak.cloud



  s3://mse-pi-lstudio-source/page_with_title/Grotius_Dg-012.png
  https://mse-pi-lstudio-source.s3.eu-north-1.amazonaws.com/page_with_title/Grotius_Dg-012.png

docker run --rm -i -v=traefik_acme:/tmp/myvolume busybox find /tmp/myvolume