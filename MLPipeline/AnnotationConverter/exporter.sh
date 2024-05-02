#!/bin/bash

TOKEN=5de1b33339f5cc8762eb7672b78bd9bdbeaff92c

# curl -X GET https://mse-pi.pasche-net.ch/label-studio/api/projects/ -H "Authorization: Token $TOKEN" > projects.json
# curl -X GET https://mse-pi.pasche-net.ch/label-studio/api/projects/1/export?exportType=JSON -H "Authorization: Token $TOKEN" --output 'annotations_json.json'
# curl -X GET https://mse-pi.pasche-net.ch/label-studio/api/projects/1/export/formats -H "Authorization: Token $TOKEN" --output 'formats.json'
curl -X GET https://mse-pi.pasche-net.ch/label-studio/api/projects/1/export?exportType=COCO -H "Authorization: Token $TOKEN" --output 'annotations_coco.json'
