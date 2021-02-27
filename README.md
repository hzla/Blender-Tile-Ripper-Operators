# Blender-Tile-Ripper-Operators
Blender addon to help rip tiles

Available Operators:


## Scale and Tris to Quad

Before running operator: Be in obj mode, click any obj, press a to select all objects
Result: scales 4x and performs tri to quad
 
## Split Tile All

Before running operator: make sure all objects are scaled properly (1 tile = 1 meter), be in obj mode
Result: attempts to convert every polygon into 1x1 squares 
 

## Split Tile Single Object

Before running operator: make sure all objects are scaled properly (1 tile = 1 meter), be in obj mode

Result: attempts to convert every polygon into 1x1 squares on selected obj


## Filter Duplicates

Before running operator: be in obj mode

Result: removes all objects that use texture names already in current directory

Notes: also removes objects with textures in the hardcoded filters array, does not work reliably for HGSS due to how textures are named
 

## Center by Vertex

Before running operator: select desired objects in object mode, switch to edit mode, select desired vertex

Result: moves object to center based on selected vertex
 

## Export Selected Faces

Before running operator: edit mode,then select all faces you want to include in obj

Result: detatches selected obj, combines into new obj, autocenters and then exports

Notes: Must name file after running operator to finish exporting


## Export All

Before running operator: be in obj mode

Result: exports every object on its current xyz coordinates

Notes: some tiles are composed of multiple objects but this command will still export them separately, use Export Selected Faces if you need to customize your export 
