
# Load required libraries
library(leaflet)
library(leafgl)
library(leafem)
library(sf)
library(htmlwidgets)

# Load polygon data
polygonData <- read_sf("data/dandy-sun-104_crowns.geojson")

# Create a leaflet map object
myMap <- leaflet() %>%
  setView(lng = 0.12187521791306695, lat = 52.20412436973221, zoom = 14) %>% # Set initial map view
  addTiles(urlTemplate = "https://api.mapbox.com/styles/v1/ancazugo/cli9ibqvv02td01pn4mgib4qv/tiles/256/{z}/{x}/{y}@2x?access_token=pk.eyJ1IjoiYW5jYXp1Z28iLCJhIjoiY2w0NHJqZngyNTBteDNmcG5iM3ZsbDQyNCJ9.6cVqIepyKP7oNzV0RqzkMA",
           group = 'Antique') %>% 
  addTiles(urlTemplate = "http://mt0.google.com/vt/lyrs=y&hl=en&x={x}&y={y}&z={z}", group = "Google") %>% 
  addTiles(group = "OSM") #%>% # Add default base layer
  # addProviderTiles("Stamen.Toner", group = "Stamen") %>% # Add Stamen Toner base layer
  # addProviderTiles("CartoDB.Positron", group = "Positron") %>% # Add CartoDB Positron base layer
  # addProviderTiles("Esri.WorldImagery", group = "Esri Image")

# myMap <- myMap %>%
#   addProviderTiles(
#     provider = "MapBox",
#     options = providerTileOptions(
#       id = "https://api.mapbox.com/styles/v1/ancazugo/cli9ibqvv02td01pn4mgib4qv/tiles/256/{z}/{x}/{y}@2x?access_token=pk.eyJ1IjoiYW5jYXp1Z28iLCJhIjoiY2w0NHJqZngyNTBteDNmcG5iM3ZsbDQyNCJ9.6cVqIepyKP7oNzV0RqzkMA",
#       accessToken = Sys.getenv('MAPBOX_TOKEN')
#     )
#   )

# Add polygon layer
myMap <- myMap %>%
  # addPolygons(data = st_transform(polygonData, 4326), fillOpacity = 0.5, 
  #             fillColor = "green", color='green', group = "Polygon Layer")
  addGlPolygons(data = st_transform(polygonData, 4326), #fillOpacity = 0.9,
              fillColor = "green", color='darkgreen', group = "Trees")

myMap <- myMap %>%
  addEasyButton(easyButton(
    icon="fa-globe", title="Zoom to Level 14",
    onClick=JS("function(btn, map){ map.setZoom(14); }"))) %>%
  addEasyButton(easyButton(
    icon="fa-crosshairs", title="Locate Me",
    onClick=JS("function(btn, map){ map.locate({setView: true}); }")))

# Add layer control
myMap <- myMap %>%
  addLayersControl(
    baseGroups = c("Antique", "Google", "OSM"), #"Stamen", "Positron", "Esri Image"),
    overlayGroups = c("Trees"),
    options = layersControlOptions(collapsed = T)
  ) %>%
  addMiniMap(toggleDisplay = T, minimized = T) %>%
  addMeasure(
    position = "topright",
    primaryLengthUnit = "meters",
    primaryAreaUnit = "sqmeters",
    activeColor = "#3D535D",
    completedColor = "#7D4479") %>%
  addMouseCoordinates() %>% 
  addLogo(img = "images/QR.png", url = "https://ancazugo.github.io/detectree2-Cambridge", src = 'local', position = 'bottomleft',
          width = 100, height = 100)
  
# Print the map
myMap

saveWidget(myMap, "index.html", selfcontained = T)
