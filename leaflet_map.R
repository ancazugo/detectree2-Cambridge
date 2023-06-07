
# Load required libraries
library(leaflet)
library(sf)
library(htmlwidgets)

# Load polygon data
polygonData <- read_sf("data/dandy-sun-104_crowns.geojson")

# Create a leaflet map object
myMap <- leaflet() %>%
  setView(lng = 0.12187521791306695, lat = 52.20412436973221, zoom = 14)  # Set initial map view

# Add base layers
myMap <- myMap %>%
  addTiles(group = "Base Layer")  # Add default base layer

# Additional base layers
myMap <- myMap %>%
  addProviderTiles("Stamen.Toner", group = "Base Layer")  # Add Stamen Toner base layer
myMap <- myMap %>%
  addProviderTiles("CartoDB.Positron", group = "Positron Layer")  # Add CartoDB Positron base layer

# myMap <- myMap %>%
#   addProviderTiles(
#     provider = "MapBox",
#     options = providerTileOptions(
#       id = "https://api.mapbox.com/styles/v1/ancazugo/cli9ibqvv02td01pn4mgib4qv/tiles/256/{z}/{x}/{y}@2x?access_token=pk.eyJ1IjoiYW5jYXp1Z28iLCJhIjoiY2w0NHJqZngyNTBteDNmcG5iM3ZsbDQyNCJ9.6cVqIepyKP7oNzV0RqzkMA",
#       accessToken = Sys.getenv('MAPBOX_TOKEN')
#     )
#   )

myMap <- myMap %>%
  addTiles(urlTemplate = "https://api.mapbox.com/styles/v1/ancazugo/cli9ibqvv02td01pn4mgib4qv/tiles/256/{z}/{x}/{y}@2x?access_token=pk.eyJ1IjoiYW5jYXp1Z28iLCJhIjoiY2w0NHJqZngyNTBteDNmcG5iM3ZsbDQyNCJ9.6cVqIepyKP7oNzV0RqzkMA",
           group = 'Antique')

# Add polygon layer
myMap <- myMap %>%
  addPolygons(data = st_transform(polygonData, 4326), fillOpacity = 0.5, 
              fillColor = "green", color='green', group = "Polygon Layer")

# Add layer control
myMap <- myMap %>%
  addLayersControl(
    baseGroups = c("Base Layer"),
    overlayGroups = c("Polygon Layer"),
    options = layersControlOptions(collapsed = T)
  )

# Print the map
myMap

saveWidget(myMap, "index.html", selfcontained = TRUE)
