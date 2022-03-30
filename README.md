![WiM](wim.png)

# South Carolina StreamStats Runoff Modeling Services

This is the FastAPI setup of runoff modeling services for South Carolina StreamStats Phase II.

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
```

Alternate instructions for the Windows Anaconda3 prompt:

```bash
# create a new Conda environment
conda create --name ss-runoffmodelingservices
# active the Conda environment
conda activate ss-runoffmodelingservices
# install the project's dependencies
conda install pip
pip install -r requirements.txt
# deploy at a local server
uvicorn main:app --host 0.0.0.0 --port 8000
```

Add `--reload` to the end of the `uvicorn main:app --host 0.0.0.0 --port 8000` to enable hot reload for local testing purposes only.

Once the above code has been run successfully, the service documentation will be available at http://127.0.0.1:8000/docs/.

## Authors

- **[Andrea Medenblik](https://github.com/amedenblik)**  - *Web Developer* - [USGS Web Informatics & Mapping](https://wim.usgs.gov/)

See also the list of [contributors](../../graphs/contributors) who participated in this project.

## License

This project is licensed under the Creative Commons CC0 1.0 Universal License - see the [LICENSE.md](LICENSE.md) file for details

## Suggested Citation

In the spirit of open source, please cite any re-use of the source code stored in this repository. Below is the suggested citation:

`This project contains code produced by the Wyoming-Montana Water Science Center and the Web Informatics and Mapping (WIM) team at the United States Geological Survey (USGS). As a work of the United States Government, this project is in the public domain within the United States. https://wim.usgs.gov`

## About WIM

- This project authored by the [USGS WIM team](https://wim.usgs.gov)
- WIM is a team of developers and technologists who build and manage tools, software, web services, and databases to support USGS science and other federal government cooperators.
- WIM is a part of the [Upper Midwest Water Science Center](https://www.usgs.gov/centers/upper-midwest-water-science-center).
