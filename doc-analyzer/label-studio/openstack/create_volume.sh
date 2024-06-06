#!/bin/bash

# 5 GB volume for PGSQL Database
openstack volume create --description "Volume for Label Studio PGSQL Database" --size 5 label-studio-pgsql-db

# 
openstack server add volume mse-pi-services label-studio-pgsql-db