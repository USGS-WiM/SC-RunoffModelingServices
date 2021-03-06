![WiM](wim.png)

# South Carolina StreamStats Runoff Modeling Services

This is the FastAPI setup of runoff modeling services for South Carolina StreamStats Phase II. These runoff modeling services will allow a user to compute hydrographs for the USGS SC Flood Hydrograph for Rural Watersheds, USGS SC Flood Hydrograph for Urban Watersheds, and SC Synthetic Unit Hydrograph. Service documentation for the `master` branch can be found at https://sc-runoffmodelingservices.streamstats.usgs.gov/docs.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites

- Python 3

### Secrets file

If any ScienceBase map services have not been published, you will need to use and update a secrets file to access these files. [Download the file here](https://doimspp.sharepoint.com/:u:/r/sites/GS-UMidWIM/Shared%20Documents/Projects/Streamstats%20Ecosystem/South%20Carolina%20Customizations/secrets.py?csf=1&web=1&e=N5bf8W) and follow the instructions in the file. 

### Running locally

Run the following in your Windows command prompt:

```bash
# create a virtual environment
python -m venv env
# active the virtual environment
.\env\Scripts\activate
# install the project's dependencies
pip install -r requirements.txt
# deploy at a local server
uvicorn main:app --host 0.0.0.0 --port 8000
# deploy at a local server with hot reload
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

Alternate instructions for the Windows Anaconda3 prompt:

```bash
# create a new Conda environment
conda create --name sc-runoffmodelingservices
# active the Conda environment
conda activate sc-runoffmodelingservices
# install the project's dependencies
conda install pip
pip install -r requirements.txt
# deploy at a local server
uvicorn main:app --host 0.0.0.0 --port 8000
# deploy at a local server with hot reload
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

Once the above code has been run successfully, the service documentation will be available at http://127.0.0.1:8000/docs/.

## Deployment

1. [Contact SysOps](https://github.com/USGS-WiM/wim-infrastructure/issues/new) to request access to the FastAPI_Services server
2. Connect to Pulse Secure or ask SysOps to add your IP address to the IP address allowlist in AWS
3. Use [Putty](https://www.putty.org/) to SSH onto the FastAPI_Services server. In the Putty Configuration:
     - Host Name: `<you_username>@FastAPI_Services_hostname_or_IP_address`
     - Port: 22
     - Connection type: SSH
     - In the sidebar, Connection > SSH > Auth: "Private key file for authentication:" click "Browse" to upload your private key file
     - Click "Open" to connect
 4. Go to the app directory: `cd /var/www/SC-RunoffModelingServices`
 5. Pull the latest code: `sudo git pull origin master`
 6. Restart the daemon: `sudo systemctl restart SC-RunoffModelingServices`
 7. Check that the services were updated: https://sc-runoffmodelingservices.streamstats.usgs.gov/docs
 8. Exit when finished: `exit`

## Authors

- **[Andrea Medenblik](https://github.com/amedenblik)**  - *Web Developer* - [USGS Web Informatics & Mapping](https://wim.usgs.gov/)
- **[Harper Wavra](https://github.com/harper-wavra)**  - *Web Developer* - [USGS Web Informatics & Mapping](https://wim.usgs.gov/)

See also the list of [contributors](../../graphs/contributors) who participated in this project.

## License

This project is licensed under the Creative Commons CC0 1.0 Universal License - see the [LICENSE.md](LICENSE.md) file for details

## Scientific Documentation

This project implements methodology described in the following reports:

[Bohman, L.R., 1989, Determination of flood hydrographs for streams in South Carolina: Volume 1. Simulation of flood hydrographs for rural watersheds in South Carolina: U.S. Geological Survey Water-Resources Investigations Report 89-4087, 79 p.](https://pubs.er.usgs.gov/publication/wri894087)

[Bohman, L.R., 1992, Determination of flood hydrographs for streams in South Carolina: Volume 2. Estimation of peak-discharge frequency, runoff volumes, and flood hydrographs for urban watersheds: U.S. Geological Survey Water-Resources Investigations Report 92-4040, 79 p.](https://pubs.er.usgs.gov/publication/wri924040)

[Meadows, M.E., 2020, South Carolina Unit Hydrograph Method Applications Manual: South Carolina Department of Transportation FHWA-SC-20-02, 139 p.](https://www.scdot.org/business/technicalPDFs/hydraulic/SPR-738-SC-UH-Method-Application-Manual-May-2020.pdf)                                 

## Suggested Citation

In the spirit of open source, please cite any re-use of the source code stored in this repository. Below is the suggested citation:

`This project contains code produced by the Wyoming-Montana Water Science Center and the Web Informatics and Mapping (WIM) team at the United States Geological Survey (USGS). As a work of the United States Government, this project is in the public domain within the United States. https://wim.usgs.gov`

## Internal documentation

Detailed internal documentation can be found in the [StreamStats guide](https://doimspp.sharepoint.com/sites/GS-UMidWIM/_layouts/OneNote.aspx?id=%2Fsites%2FGS-UMidWIM%2FShared%20Documents%2FProjects%2FStreamstats%20Ecosystem%2FKJ%27s%20Guide%20to%20StreamStats%201&wd=target%28Introduction.one%7CFA6D5C1D-D7FB-4D35-B339-992EF3438208%2FRunoff%20Modeling%20Services%7C3C3FF549-F709-4E55-B005-19903B30253B%2F%29).

## About WIM

- This project authored by the [USGS WIM team](https://wim.usgs.gov)
- WIM is a team of developers and technologists who build and manage tools, software, web services, and databases to support USGS science and other federal government cooperators.
- WIM is a part of the [Upper Midwest Water Science Center](https://www.usgs.gov/centers/upper-midwest-water-science-center).
