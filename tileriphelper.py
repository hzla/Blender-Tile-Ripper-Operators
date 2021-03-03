bl_info = {
    "name": "Pokemon Tile Ripper Operators",
    "blender": (2, 80, 0),
    "category": "Object",
}

import bpy
import os
import bmesh


def view3d_find(return_area=False): #used to get context
        for area in bpy.context.window.screen.areas:
            if area.type == 'VIEW_3D':
                v3d = area.spaces[0]
                rv3d = v3d.region_3d
                for region in area.regions:
                    if region.type == 'WINDOW':
                        if return_area: 
                            return region, rv3d, v3d, area
                        return region, rv3d, v3d
        return None, None

def ShowMessageBox(message = "", title = "Message Box", icon = 'INFO'):
    def draw(self, context):
        self.layout.label(text=message)
    bpy.context.window_manager.popup_menu(draw, title = title, icon = icon)
    

class ObjectCenterP(bpy.types.Operator):
    bl_idname = "object.center_p" 
    bl_label = "Center by Vertex"  
    bl_options = {'REGISTER', 'UNDO'} 

    def execute(self, context):    

        bpy.ops.mesh.select_mode(type="VERT")
        bpy.ops.object.editmode_toggle() #go toobject mode
        ob = bpy.context.selected_objects[0] #store selected object
        bpy.ops.object.editmode_toggle() # go to edit mode
        for area in bpy.context.screen.areas:
            if area.type == 'VIEW_3D':
                ctx = bpy.context.copy()
                ctx['area'] = area
                ctx['region'] = area.regions[-1]
                bpy.ops.view3d.snap_cursor_to_selected(ctx) #move cursor to selected vertex
        bpy.ops.object.editmode_toggle() # go to obj mode
        bpy.ops.object.origin_set(type='ORIGIN_CURSOR', center='MEDIAN') #set obj origin to cursor
        matrix = ob.matrix_world #set the matrix from where we get the cordinates of the vertex/origin
        bpy.ops.transform.translate(value=(((0-1) * matrix[0][3]), ((0-1) * matrix[1][3]), ((0-1) * matrix[2][3])), orient_type='GLOBAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='GLOBAL', constraint_axis=(True, True, True), mirror=True, use_proportional_edit=False, proportional_edit_falloff='SMOOTH', proportional_size=1, use_proportional_connected=False, use_proportional_projected=False) #translate the inverse of the vertex cordinates
      
        return {'FINISHED'}

class ObjectTileAll(bpy.types.Operator):
    bl_idname = "object.tile_all" 
    bl_label = "Split Tile All"  
    bl_options = {'REGISTER', 'UNDO'} 

    def execute(self, context):    

        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
        region, rv3d, v3d, area = view3d_find(True)
        override = {
        'scene'  : bpy.context.scene,
        'region' : region,
        'area'   : area,
        'space'  : v3d} 
        bpy.ops.object.select_all(action='DESELECT')
        objects = bpy.context.scene.objects
        for obj in objects:
            bpy.context.view_layer.objects.active = obj 
            #set current object as active
            obj.select_set(True)
            bpy.ops.object.editmode_toggle()
            mesh_data = bmesh.from_edit_mesh(obj.data)
            mesh_data.edges.ensure_lookup_table() 
            #have to refresh edges array each time you add an edge to avoid error
            try:
                num_edges = mesh_data.edges[-1].index
            except IndexError:
                continue
            for edge_index in range(num_edges): 
                #iterate through a range instead of edges array to avoid infinitly creating edges
                edge = mesh_data.edges[edge_index]
                length = edge.calc_length()
                rounded_length = str(round(length, 2)) 
                #round numbers to account for SDSME import imprecisions
                length_is_dividable_integer = (length > 1) and ((length % 1 <= 0.05) or (length % 1 >= 0.95)) 
                if length_is_dividable_integer: 
                    #loop cut every edge with integer length over 1 into 1 unit sections
                    num_cuts = round(length, 0) - 1
                    bpy.ops.mesh.loopcut_slide(override, MESH_OT_loopcut={"number_cuts":num_cuts, "smoothness":0, "falloff":'INVERSE_SQUARE', "object_index":0, "edge_index":edge_index, "mesh_select_mode_init":(True, False, False)}, TRANSFORM_OT_edge_slide={"value":0, "single_side":False, "use_even":False, "flipped":False, "use_clamp":True, "mirror":True, "snap":False, "snap_target":'CLOSEST', "snap_point":(0, 0, 0), "snap_align":False, "snap_normal":(0, 0, 0), "correct_uv":True, "release_confirm":False, "use_accurate":False})
                    bpy.ops.mesh.select_all(action='SELECT')
                    mesh_data.edges.ensure_lookup_table() 
                    #refresh edges again
            bpy.ops.object.editmode_toggle()
            bpy.ops.object.select_all(action='DESELECT')
        bpy.ops.object.select_all(action='SELECT')
        bpy.ops.object.editmode_toggle() 
        #end in edit mode to more quickly see result
      

        return {'FINISHED'}

class ObjectScale(bpy.types.Operator):
    bl_idname = "object.scale" 
    bl_label = "Scale and Tris to Quad"  
    bl_options = {'REGISTER', 'UNDO'} 
    scale = bpy.props.IntProperty(name="Scale", default=4, min=0, max=1000000)
    def execute(self, context):    

        bpy.ops.object.editmode_toggle()
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.tris_convert_to_quads()
        bpy.ops.transform.resize(value=(self.scale, self.scale, self.scale), orient_type='GLOBAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='GLOBAL', mirror=True, use_proportional_edit=False, proportional_edit_falloff='SMOOTH', proportional_size=1, use_proportional_connected=False, use_proportional_projected=False, release_confirm=True)
      
        return {'FINISHED'}
    
class ObjectFilter(bpy.types.Operator):
    bl_idname = "object.filter" 
    bl_label = "Filter Duplicates"  
    bl_options = {'REGISTER', 'UNDO'} 

    def execute(self, context):    
        bpy.ops.object.select_all(action='DESELECT') 
        #array to store textures already added
        mats = []
        #filter out textures containing the following
        filters = ["criff", "ngrass", "conttree", "ckado", "newstep", "wcliff", "imped", "sea", "hana","tree2", "tshadow", "sand", "snow","nectgr", "lambert"]
        for file in os.listdir(bpy.path.abspath("//")):
            if file.endswith(".png"):
                mats.append(file[0:-4])
            scene = bpy.context.scene
            for ob in scene.objects:
                filtered = False
                print(ob)
                for f in filters:
                    if f in ob.active_material.name:
                        filtered = True
                        print("filtered by " + f)
                        break
                if filtered:    
                    ob.select_set(True)
                    continue
                if ob.active_material.name in mats:
                    print(ob.active_material.name +  " already present")
                    ob.select_set(True)
                else:
                    print(ob.active_material.name)
        bpy.ops.object.delete()
        return {'FINISHED'}
    
class ObjectTile(bpy.types.Operator):
    bl_idname = "object.tile" 
    bl_label = "Split Tile Single Object"  
    bl_options = {'REGISTER', 'UNDO'} 

    def execute(self, context):    

        region, rv3d, v3d, area = view3d_find(True)
        override = {
        'scene'  : bpy.context.scene,
        'region' : region,
        'area'   : area,
        'space'  : v3d}
        objects = bpy.context.scene.objects
        obj = bpy.context.view_layer.objects.active 
        obj.select_set(True)
        bpy.ops.object.editmode_toggle()
        mesh_data = bmesh.from_edit_mesh(obj.data)
        mesh_data.edges.ensure_lookup_table()
        num_edges = mesh_data.edges[-1].index
        for edge_index in range(num_edges):
            edge = mesh_data.edges[edge_index]
            length = edge.calc_length()
            print(length)
            rounded_length = str(round(length, 2))
            length_is_dividable_integer = (length > 1) and ((length % 1 <= 0.05) or (length % 1 >= 0.95))
            if length_is_dividable_integer:
                num_cuts = round(length, 0) - 1
                bpy.ops.mesh.loopcut_slide(override, MESH_OT_loopcut={"number_cuts":num_cuts, "smoothness":0, "falloff":'INVERSE_SQUARE', "object_index":0, "edge_index":edge_index, "mesh_select_mode_init":(True, False, False)}, TRANSFORM_OT_edge_slide={"value":0, "single_side":False, "use_even":False, "flipped":False, "use_clamp":True, "mirror":True, "snap":False, "snap_target":'CLOSEST', "snap_point":(0, 0, 0), "snap_align":False, "snap_normal":(0, 0, 0), "correct_uv":True, "release_confirm":False, "use_accurate":False})
                bpy.ops.mesh.select_all(action='SELECT')
                mesh_data.edges.ensure_lookup_table()
      
        return {'FINISHED'}

class ObjectExportAll(bpy.types.Operator):
    bl_idname = "object.export_all" 
    bl_label = "Export All as .obj"  
    bl_options = {'REGISTER', 'UNDO'} 

    def execute(self, context):    
        basedir = bpy.path.abspath('//')
        bpy.ops.object.select_all(action='DESELECT') 
        scene = bpy.context.scene
        for ob in scene.objects:
            ob.select_set(True)
            name = os.path.join(basedir, ob.name + '.obj')
            bpy.ops.export_scene.obj(filepath=name, check_existing=True, axis_forward='Y', axis_up='Z', filter_glob="*.obj;*.mtl", use_selection=True, use_animation=False, use_mesh_modifiers=True, use_edges=True, use_smooth_groups=False, use_smooth_groups_bitflags=False, use_normals=True, use_uvs=True, use_materials=True, use_triangles=False, use_nurbs=False, use_vertex_groups=False, use_blen_objects=True, group_by_object=False, group_by_material=False, keep_vertex_order=False, global_scale=1, path_mode='AUTO')
            ob.select_set(False)
        ShowMessageBox(message="Exported to " + basedir, title="Export")
        return {'FINISHED'}
    
class ObjectExportFaces(bpy.types.Operator):
    bl_idname = "object.export_faces" 
    bl_label = "Export Selected Faces"  
    bl_options = {'REGISTER', 'UNDO'} 
    file_name = bpy.props.StringProperty(name="Type Name, Press Enter", default="", maxlen=100, subtype='NONE', update=None, get=None, set=None)
    

    def execute(self, context):    
        scn = bpy.context.scene
        names = [ obj.name for obj in scn.objects] 
        #get current objects
        bpy.ops.mesh.separate(type='SELECTED') 
        #separate selected faces from their respective object
        new_objs = [ obj for obj in scn.objects if not obj.name in names] 
        #get new objects by comparing to old objs
        original_object_name = bpy.context.view_layer.objects.active.name
        bpy.ops.object.editmode_toggle()
        bpy.ops.object.select_all(action='DESELECT')
        for obj in new_objs: 
            #select all newly created objects
            obj.select_set(True)
        bpy.context.view_layer.objects.active = new_objs[0] 
        #need to set one of the new objects as active for join() to work
        scn = bpy.context.scene
        names = [ obj.name for obj in scn.objects] #get current objects
        bpy.ops.object.join()
        new_objs = [ obj for obj in scn.objects if not obj.name in names] 
        #get newly created objects from joining
        bpy.ops.object.select_all(action='DESELECT')
        bpy.context.view_layer.objects.active.select_set(True)
        o  = bpy.context.view_layer.objects.active  
        # the joined object is automatically made active from before
        mw = o.matrix_world      
        # Active object's world matrix
        glob_vertex_coordinates = [ mw @ v.co for v in o.data.vertices ] # Global 
        # Find the lowest Z value amongst the object's verts
        minZ = min( [ co.z for co in glob_vertex_coordinates ] ) 
        # Select all the vertices that are on the lowest Z
        for v in o.data.vertices:
            if (mw @ v.co).z == minZ: 
                v.select = True
                break
        bpy.ops.object.editmode_toggle() 
        # go to edit mode
        ObjectCenterP.execute(ObjectCenterP,bpy.context)
        if self.file_name:
            basedir = bpy.path.abspath('//')
            bpy.ops.object.select_all(action='DESELECT') 
            scene = bpy.context.scene
            ob = bpy.context.view_layer.objects.active
            ob.select_set(True)
            name = os.path.join(basedir, self.file_name + '.obj')
            bpy.ops.export_scene.obj(filepath=name, check_existing=True, axis_forward='Y', axis_up='Z', filter_glob="*.obj;*.mtl", use_selection=True, use_animation=False, use_mesh_modifiers=True, use_edges=True, use_smooth_groups=False, use_smooth_groups_bitflags=False, use_normals=True, use_uvs=True, use_materials=True, use_triangles=False, use_nurbs=False, use_vertex_groups=False, use_blen_objects=True, group_by_object=False, group_by_material=False, keep_vertex_order=False, global_scale=1, path_mode='AUTO')
            ob.select_set(False)
            self.report({'INFO'}, "Exported to " + name)
            ShowMessageBox(message="Exported to " + name, title="Export")
            return {'FINISHED'}
        return {'FINISHED'}

def register():
    bpy.utils.register_class(ObjectCenterP)
    bpy.utils.register_class(ObjectTileAll)
    bpy.utils.register_class(ObjectTile)
    bpy.utils.register_class(ObjectExportAll)
    bpy.utils.register_class(ObjectExportFaces)
    bpy.utils.register_class(ObjectScale)
    bpy.utils.register_class(ObjectFilter)


def unregister():
    bpy.utils.unregister_class(ObjectCenterP)
    bpy.utils.unregister_class(ObjectTileAll)
    bpy.utils.unregister_class(ObjectTile)
    bpy.utils.unregister_class(ObjectExportAll)
    bpy.utils.unregister_class(ObjectExportFaces)
    bpy.utils.unregister_class(ObjectScale)
    bpy.utils.unregister_class(ObjectFilter)

if __name__ == "__main__":
    register()
