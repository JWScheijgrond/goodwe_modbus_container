# goodwe_modbus_container

I have taken the goodwe library of MarcelBlijleven (https://github.com/marcelblijleven/goodwe) and added a docker file and script for continuosly calling the modbus interface on my Goodwe 3000D-NS inverter equipped with the wifi/lan adapter. 

The local_search is added to activate the modbus when the inverter is starting. This is a variation on the broadcast the solargo app does when searching inverters. 

This script depends on the inverter having a fixed IP address because performing a broadcast on the entire network (255.255.255.255) results in an error 13 when running the script from inside the docker container. 

Set the environment variables for the IP address of the Inverter, the API code for PVOutput and the systemID for PVOutput




## Prerequisites

- Docker installed on your machine

## Building the Docker Image

You can choose to update the environment variables in the docker file or set them when running the image. 

To build the Docker image, run the following command in the directory containing the Dockerfile:

```sh
docker build -t goodwe_modbus_logger .
```

## Running the Docker image

```sh
docker run -e PVO_APIKEY="your_api_key" -e PVO_SYSTEMID="your_system_id" -e INV_IP="your_inverter_ip" -e INV_FAM="your_inverter_family" goodwe_modbus_logger
```

## Timezone

The Dockerfile sets the timezone to Europe/Amsterdam. If you need to change the timezone, modify the ENV TZ line in the Dockerfile.

## Environment variables

| Name         | Example Value       | Description                      |
|--------------|---------------------|----------------------------------|
| `PVO_APIKEY` | PVOUTPUTAPIKEY      | Your PVOutput API key            |
| `PVO_SYSTEMID` | 1111111           | Your PVOutput system ID          |
| `INV_IP`     | 192.168.0.239       | The IP address of your inverter  |
| `INV_FAM`    | D-NS                | The family of your inverter      |
| `TZ`         | Europe/Amsterdam    | The timezone used for sending to PVO | 



