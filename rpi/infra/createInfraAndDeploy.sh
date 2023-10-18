#!/bin/bash

# create resource group
echo "Creating resource group RPI-Cloud."
az group create --location westeurope --name RPI-Cloud

# create storage account
echo "Creating storage account harrpistorage."
az storage account create --resource-group RPI-Cloud --name harrpistorage --location westeurope --kind StorageV2 --sku Standard_LRS

# create file share
echo "Creating file share nats-config."
az storage share-rm create --resource-group RPI-Cloud --storage-account harrpistorage --name nats-config --quota 1 --enabled-protocols SMB

# upload config files
echo "Uploading files to harrpistorage..."
cd ../nats-config

for file in ./*; do
    az storage file upload --account-name harrpistorage --share-name nats-config --source $file --path $file
done

echo "Files uploaded."

# deploy app 
cd ../
docker context use har-azure
docker compose up