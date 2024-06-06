#!/bin/sh
openstack server create --image "Ubuntu 22.04 LTS Jammy Jellyfish" \
    --flavor a2-ram4-disk50-perf1 \
    --key-name mse-pi-keypair \
    --network ext-net1 \
    mse-pi-services