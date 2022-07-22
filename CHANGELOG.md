# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html).

## [Unreleased](https://github.com/USGS-WiM/SC-RunoffModelingServices/tree/dev)

### Added 

- lagtimetc endpoint: computes Time of Concentration by the Lag Time Equation Method
- traveltimetc endpoint: computes Time of Concentration by the Travel Time Method
- curveNumberData endpoint: returns data for curve number determination (currently returns placeholder data)
- PRF endpoint: returns PRF and gamma N value (currently returns placeholder PRF data)
- runoffweightedCN endpoint: calculates runoff-weighted curve number
- areaweightedCN endpoint: calculates area-weighted curve number
### Changed  

-

### Deprecated 

-

### Removed 

- 

### Fixed  

- 

### Security  



## [v0.1.1](https://github.com/USGS-WiM/SC-RunoffModelingServices/releases/tag/v0.1.1) - 2022-06-30
### Fixed  

- Renamed custom response header for warning messages from `warning` to `X-warning`
- Exposed custom response header"Access-Control-Expose-Headers"

## [v0.1.0](https://github.com/USGS-WiM/SC-RunoffModelingServices/releases/tag/v0.1.0) - 2022-06-29
### Added

- rainfalldata endpoint: replicates "Rainfall Data" sheet in SC Unit Hydrograph spreadsheet
- rainfalldistributioncurve endpoint: returns the NOAA rainfall distribution curve letter and number
- RI2 endpoint: returns I2H2Y value from NOAA precipitation server 
- urbanhydrographbohman199 endpoint: implements Bohman 1992 report
- ruralhydrographbohman1989 endpoint: implements Bohman 1989 report