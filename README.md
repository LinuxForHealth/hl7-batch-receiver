# whpa-cdp-hl7-batch-receiver

This project provides the service to receive batches of hl7 messages and save them for later processing (e.g., convert to FHIR and persist).

A docker image for this project is created from the [LinuxForHealth py-service-wrapper](https://github.com/LinuxForHealth/py-service-wrapper) utility docker image.

## Deployment

Docker images were initially manually pushed to cdp artifactory with image name: `wh-imaging-cdp-docker-local.artifactory.swg-devops.com/cdp/hl7batchreceiver:<version>` See [Changelog](#changelog) for information on versions.

Since version 1.0.0, the build has been integrated with the Jenkins CI and images are now pushed automatically. See the Jenkinsfile for image path and version configurations. There's also a version in the build.gradle file.

This image can be used to test the service/ run it locally without building etc.

---

## Development

### Setup

We are using Gradle through a [python gradle plugin](https://github.com/xvik/gradle-use-python-plugin) for the build environment. The build.gradle file is configured for CD builds and may pose challenges for local development. To make local development simpler use the local.build.gradle file and execute the build like `gradle -b local.build.gradle build`.

A virtual env is created at location `python.envPath` as defined in the `build.gradle` `python` closure. By default the virtual env location is `./opt/ibm/whi/app` which may cause permission issues when running locally. Changing this to different directory may make life easier. Sourcing your virtual env during local development is also advised. By default your local python binary is used to create that virtual env. The gradle files mimic what we expect in Jenkins but you can provide `python.pythonBinary` to override local python that will be used.

```bash
gradle tasks # will list all the available tasks
gradle build # will setup virtualenv, run all tests, and create reports and distribution
```

Note: you will need the `taasArtifactoryUsername` and `taasArtifactoryPassword` variables in `gradle.properties`

> [Refer](https://pages.github.ibm.com/WH-Imaging/DevOps-CDP/docs/Dev_setup/Python.html) and see `local.build.gradle` for more information.

Update gradle.properties as needed.
### How to Create the Image for this Project

See [LinuxForHealth py-service-wrapper](https://github.com/LinuxForHealth/py-service-wrapper) for background on the service wrapper.

1. Open a terminal window and navigate to the hl7BatchReceiver project parent directory.

2. There are two ways to create an installable `whl` fil
   - Way 1: Use the docker builder image [refer](https://pages.github.ibm.com/WH-Imaging/DevOps-CDP/docs/Dev_setup/Python.html) section "Building projects using builder Image"
   - Way 2: Use local build gradle file

   ```bash
   gradle clean build -b local.build.gradle # dist is under build/dist by default as per gradle.properties file
   ```

   Note: on Windows clean step will fail in Powershell, it needs linux `rm` command which is in git bash.

3. Create the container using the docker build command below. Add your artifactory id (this is likely your w3 email) and key where specified.

    ```bash
    docker build --build-arg USERNAME=<your artifactory email> --build-arg PASSWORD=<your artifactory api-key> -t hl7batchreceiver:0.0.3 .
    ```

If the steps completed successfully, the image specified by the `-t` option should now exist.

### Running the Image

Note that the versions may need updated in the examples below.

```bash
docker run -e CONFIG_FILE_LOCATION='/opt/app/mount/config.ini' -v $(pwd)/config/:/opt/app/mount/ --name hl7batchreceiver-c1 -p 5000:5000 hl7batchreceiver:0.0.3
```

To run the image with all services, use the docker-compose file. To run with a locally build image, update the docker-compose.yml batch-receiver image name to the one created in the [image creating steps](###-How-to-Create-the-Image-for-this-Project) above. Example:

```yml
batch-receiver:
    #image: "wh-imaging-cdp-docker-local.artifactory.swg-devops.com/cdp/hl7batchreceiver:0.0.3"
    image: "hl7batchreceiver:0.0.3"
```

Run the image with all services from the project directory using edited docker-compose.yml:

```bash
docker-compose up -d
```

Note: Make sure you are mounting the config.ini file to make it available to application at runtime.

See the project.yaml for the endpoints available.
GET API to verify the service is running in the container:

```bash
http://localhost:5000/ping  # http GET
```

```bash
http://localhost:5000/hl7_batch  # http POST
```

```bash
http://localhost:5000/hl7_batchzip  # http POST
```

Possible http return codes returned by the batch-receiver service:

* 200 Successful.
* 400 Bad request (occurs if input to htl7_batchzip is identified as a non-zip file).
* 412 Precondition Failed. The tenant-id may be missing.
* 422 Validation Error. Data payload issue.
* 500 Internal server error.


#### OpenApi/Swagger URL

http://localhost:5000/docs

An alternative view:
http://localhost:5000/redoc

---

### Development Tips

#### Adding Dependencies

Update the `build.gradle` file to add dependencies.

#### Formatting

We are using [Python Black](https://pypi.org/project/black/) which is a python code formatter. If you are using vscode you can set it up to use `black` as default formatter for py files

Alternatively you can just run (from within the virtualenv):

```bash
black <file or directory>
```

#### VS Code Python

To setup vscode with the virtualenv and `black` as default python formatter for the project, create a file  `.vscode/settings.json`  , sample below:
```json
#settings.json
{
    "python.formatting.provider": "black",
    "python.pythonPath": "/Users/ayush.garg/.local/share/virtualenvs/whpa-cdp-hl7-batch-receiver-fH1xTusc/bin/python"
}
```

Note: you can set `editor.formatOnSave` to True to automatically formatting files on save

---

## Testing

To run unit tests, execute:

```bash
gradle clean test -b local.build.gradle
```

For a integration tests, you can leverage the `docker-compose.yml` file to bring up all services needed for testing (e.g. kafka) and try sending data through curl/postman. If you are testing local changes, update the docker-compose.yml file to use your local image for the batch-receiver.

You can run integration tests via the `cdpHl7IntegrationBatchTest` gradle task. Note that only one file is currently parsed by pytest and if more test files are needed, the gradle.properties file will need updated (see `pyIntegrationTestDir` property).
```bash
gradle cdpHl7IntegrationBatchTest
```

To bring up services:

```bash
docker-compose up -d
```

* Kafka internal to docker available via broker: `kafka:9092`
* kafdrop (UI to view kafka) is at http://localhost:9000/
* hl7 batch service at http://localhost:5000/ping
* Minio available at http://localhost:9001/minio
* Postgres is available at localhost:5432


Note: to make sure you have latest images, execute:

```bash
docker-compose down -v
docker-compose pull
docker-compose up -d
```

You can curl the service like:
```bash
curl -X POST 'http://localhost:5000/upload_hl7_batchzip' \
 -H 'accept: application/json' \
 -H 'tenant-id: tenant-4-30-b' \
 -H 'Content-Type: multipart/form-data' \
 -F 'file=@batchedhl7s-example.zip;type=application/x-zip-compressed'
```


### Example Flow for test

Prerequisites

1. `docker-compose up -d`
2. Create a bucket=tenant-id in [Minio](http://localhost:9001)
  * Use the UI or
  * Use the [MinIO client](https://docs.min.io/docs/minio-client-complete-guide.html)
    1. Point client to local container
    ```bash
    mc alias set local http://localhost:9001 minioadmin minioadmin
    ```
    2. Create bucket
    ```bash
    mc mb local/<tenant_id>
    ```
3. Create the hl7 batch database
  1. Create the database
  ```bash
  createdb -h localhost -U postgres whpa_cdp_orch
  ```
  2. Install the [schema](https://github.ibm.com/WH-Imaging/whpa-cdp-schemas/blob/master/batch_processing/batch_processing.sql)
  ```bash
  psql -h localhost -U postgres -f /<path_to_schema>/whpa-cdp-schemas/batch_processing/batch_processing.sql
  ```
  Note that the linked schema has been templated and the [template is the source of truth](https://github.ibm.com/WH-Imaging/whpa-cdp-orchestration-db-init/blob/master/files/opt/ibm/whuser/bin/orchestration-onboarding-template.sql) for the schema.

Steps

1. A batch payload is sent to rest service
2. Verify on minio UI is file was uploaded
3. you can have nifi service as well in docker-compose and verify (can copy the actual flow that is used downstream), ideally nifi integration can done in explorys env

Note: Windows user might want to update the host path in the volumes section of docker-compose file

---

## Changelog

NOTE: Versions are tied to specific release targets. For specific tags, use the appended timestamp tag and commit hash (docker label: `org.label-schema.vcs-ref `) from [Artifactory](https://na.artifactory.swg-devops.com/ui/repos/tree/General/wh-imaging-cdp-docker-local%2Fwhpa-cdp%2Fwhpa-cdp-hl7-batch-receiver) to determine code to image linkage.

### 06/23/2021 Version 1.0.0

* Use the whpa-cdp-lib-postgres library for postgres connectivity
* Refactor configuration files


### 05/21/2021 Version 1.0.0

NOTE: Version 1.0.0 was used for Alpha release. However, paperwork has designated the GA release as being version 1.0.0. Note that this version (1.0.0) will be reused in the future for GA.

* Adding support for using postgres for HL7 batch metadata (batch tracking)
* Migrated to using Dockerfile to create hardened image
* Adding Jenkinsfile to integrate with CI
  * Image url changed from wh-imaging-cdp-docker-local.artifactory.swg-devops.com/`cdp/hl7batchreceiver` to wh-imaging-cdp-docker-local.artifactory.swg-devops.com/`whpa-cdp/hl7batchreceiver`


### 05/20/2021 Version 0.0.3

* Refactoring to remove local disk related code
* Adding support for using Minio for storage

### 04/23/2021 / version 0.0.2

* [Story 148](https://github.ibm.com/WH-Imaging/Clinical-Data-Pipeline/issues/148) - add and handle hl7 batch zip file.
** The above story added the 'python-multipart:0.0.5' dependency. It is used indirectly by hl7batchzip API. [Related reference.](https://fastapi.tiangolo.com/tutorial/request-files/)
* 05/5/2021: Added Java http client code example for using POST hl7_batchzip endpoint.

### Version 1.0.0
