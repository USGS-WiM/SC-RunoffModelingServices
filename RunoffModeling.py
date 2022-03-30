import owslib.wcs as wcs
from secrets import jossoSessionId # Use this jossoSessionId to access the service before the ScienceBase item is published; update as needed in secrets.py

# Get a list of all the coverages in the service

def curveNumber(x, y):

    # Gridded South Carolina StreamStats Runoff Curve Numbers by NLCD Landcover and SSURGO Soils Class
    # https://www.sciencebase.gov/catalog/item/6241fcc0d34e915b67eae16a
    ScienceBaseWCS = "https://www.sciencebase.gov/catalogMaps/mapping/ows/6241fcc0d34e915b67eae16a?josso=" + jossoSessionId # Link to Web Coverage Service (WCS)
    w = wcs.WebCoverageService(ScienceBaseWCS, version='1.0.0') # The WCS
    print(list(w.contents)) # Print the coverages available in this WCS
    c = w["sb:SC_RCN_LU_CO"] # The coverage of interest
    print(dir(c)) # Print properties of the WCS
    for f in c.supportedFormats: # Print the formats available 
        print(f)
    resx = 1000
    resy = 1000
    rfmt = "GeoTIFF"
    rCRS = c.boundingboxes[0]['nativeSrs']
    rBBOX = c.boundingboxes[0]['bbox']
    response = w.getCoverage(identifier=c.id, bbox=rBBOX, format=rfmt, crs=rCRS, width=resx, height=resy) # Will not work until ScienceBase item is published
    with open("output.tif", 'wb') as file:
        file.write(response.read())

    return "Hello, World!"

