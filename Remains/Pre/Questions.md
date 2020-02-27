# Warehouse Drone Demo Questions

## Purpose of this Demo
* Setup requirements?
* will the drone keep working once we stop paying?
  * Eyesee Cloud?
  * Vendor lock?


* Deliverables?
  * List of barcodes and locations?
  * Found Barcodes and X, Y coordinates?
    * Licence Plate
    * EAN codes?
  * empty locations?
  * locations which are not empty, but no barcode was found.
  * which formats are supported? (JSON, XML, CSV)


## Setup
* How long does it take to set up a new Location?
  * new warehouse?
  * difficulty of setup?
  * can setups be saved and shared?
* Multiple warehouses support?
  * One drone per WH?
  * Setup per Drone?
  * Setup per warehouse?
* variable Heights
  * variable beam height
  * variable heigth of warehouse
* variable Labels
  * different barcode types
  * different location of labels
  * location labels?
  * covered labels?
  * multiple labels
    * multiple correct labels
    * single label with multiple barcodes
    * "other" barcodes (SKU codes, EAN etc.)
  * product with NO label
  * empty locations
* configure locations it should not check?



## Flight
* Flight time?
* locations per minute? (from pamflet: 34000 locations, 5 drones, 200 hours == 34 locations per HOUR (with TWO operators per drone) or 170?)
* charge time / reset time / restart time?
* Multiple simultaneous Drones?
* Fully autonomous?
  * per row?
  * per warehouse?
  * from base?
* operator required?
  * operator role?
  * operator skill level?
* Indoor Positioning?


## Recognition
* Zebra 2D imager
* barcode distance?
* how does the drone find the label?
* how does it match the exact coordinates?
* matching to actual locations?
* Smart Image matching on incomplete pallets?
* damage checks?
* Photos of products?


## Safety
* crashes?
* support?
* backup / replacement drones / parts?
* if autonomous, alerting messages?
* wireless signal disruptions?


## Systems
* where is the "intelligence" in the drone, or in a "Master Controller"
* no internet available in warehouses!


