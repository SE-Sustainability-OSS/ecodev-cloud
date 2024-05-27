# ecodev-cloud

<p align="center">
<a href="https://github.com/FR-PAR-ECOACT/ecodev-cloud/actions" target="_blank">
    <img src="https://github.com/FR-PAR-ECOACT/ecodev-cloud/blob/main/badges/coverage.svg" alt="Coverage">
</a>
<a href="https://github.com/FR-PAR-ECOACT/ecodev-cloud/actions" target="_blank">
    <img src="https://github.com/FR-PAR-ECOACT/ecodev-cloud/blob/main/badges/pylint.svg" alt="Publish">
</a>
<a href="https://github.com/FR-PAR-ECOACT/ecodev-cloud/actions/workflows/code-quality.yml/badge.svg" target="_blank">
    <img src="https://github.com/FR-PAR-ECOACT/ecodev-cloud/actions/workflows/code-quality.yml/badge.svg" alt="Package version">
</a>
</p>

Read/write helpers for disk/aws s3/azure blob storage

## Installation of this package

You are strongly encouraged to install this package via Docker.

Starting from a project with a Docker file:
* add the module ecodev-cloud in the `requirements.txt` file
* make sure the `.env` file includes all required fields (see documentation)
* build the new version of the Docker container (typically `docker build --tag xxx .`)
* run it with docker compose (`dc up -d`).

## Documentation

Please find it in the [associated mkdoc website!](https://ecodev-doc.lcabox.com/)
