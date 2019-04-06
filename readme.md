Tool for creating maps in the style of engraved maps.

### Usage

`python3 map-engraver/map-engraver.py myMap.yml`

Where `myMap.yml` contains some config on what to draw. See the `example` directory for how this is structured.

### Example

```
# Download data from OSM
wget -O example/data.osm https://api.openstreetmap.org/api/0.6/map?bbox=-3.23028126,55.94554937,-3.21659279,55.95352525

# Render the map
python3 map-engraver/map-engraver.py ./example/map.yml
```

![An example of the output](example.png)
