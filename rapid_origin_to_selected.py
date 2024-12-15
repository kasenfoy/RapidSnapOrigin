bl_info = {
	"name": "Rapid Snap Origin to Selected",
	"author": "Kasen (LowSoyGames)",
	"version": (1, 0, 0),
	"blender": (4, 2, 0),
	"description": "A simple tool for snapping an Object's Origin to the selected Vertices, Edges, or Faces",
	"category": "View",
}

import bpy
from mathutils import Vector


class RapidSnapOrigin(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "object.rapid_snap_origin"
    bl_label = "Rapid Snap Origin"
    context = None

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        self.context = context        
        self.main(context)
        return {'FINISHED'}
        
    
    def main(self, context):
        """
        This function will calculate the center point of selected Vertices and set the Object's Origin to it.
        """    
        selected_objects = bpy.context.selected_objects
        
        # Confirm there is only one selected object
        if len(selected_objects) > 1:
            self.report({'WARNING'}, "Rapid Snap Origin - Does not support multiple objects at this time.")
            return    
        elif len(bpy.context.selected_objects) == 0:
            self.report({'WARNING'}, 'Rapid Snap Origin - Must have at least one object selected.')
            return
        
        # Get the object
        obj = bpy.context.selected_objects[0]
        
        # Have to move out of edit mode and in to Object mode for some reason?
        # Otherwise the values from obj.data.vertices are not accurate (Example, uncomment this, select a new vertex, then run the script. Will either use old selection or error out)
        bpy.ops.object.mode_set(mode='OBJECT')
        
        # Snapshot the Cursor's current position
        # Cast to Vector to create a copy not a reference
        cursor_loc_orig = Vector(context.scene.cursor.location)
        
        
        # Get the center of the selected vertices
        selected_vertices = [Vector(v.co) for v in obj.data.vertices if v.select]
        
        # Must have at least one selected Vertex
        if len(selected_vertices) == 0:
            self.report({'WARNING'}, "Rapid Snap Origin - Must have at least 1 vertex selected.")
            return    
            
        # Calculate Center    
        center = self.get_center(selected_vertices)

        # Convert the calculated center to world coordinates using the objects matrix (Scale, Rotation ,Position)
        center = obj.matrix_world @ Vector(center)
        
        try:
            # Set the 3D Cursor's new location        
            bpy.context.scene.cursor.location = center
            
            # Switch to Object Mode
            bpy.ops.object.mode_set(mode='OBJECT')
                        
            # Set Origin to Cursor
            bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
            
            # Switch back to Edit Mode
            bpy.ops.object.mode_set(mode='EDIT')
            
            
        except Exception as e:
            print(e)
            self.report({'ERROR'}, "Rapid Snap Origin - Unknown Failure...Resetting Cursor...")
        
        finally:
            # Always Reset to the cursors original location.
            bpy.context.scene.cursor.location = cursor_loc_orig

        
    def get_center(self, vertices):            
        # Algo for this is just taking the average of all Vertices
        # Add Vector call otherwise it actually transforms the vertices
        center = Vector(vertices[0])
        for vertex in vertices[1:]:
            center += vertex
            
        center = center / len(vertices)
        
        return center
            


def menu_func(self, context):
    self.layout.operator(RapidSnapOrigin.bl_idname, text=RapidSnapOrigin.bl_label)


# Register and add to the "object" menu (required to also use F3 search "Simple Object Operator" for quick access).
def register():
    bpy.utils.register_class(RapidSnapOrigin)
    bpy.types.VIEW3D_MT_edit_mesh_context_menu.append(menu_func)
    bpy.types.VIEW3D_MT_view.append(menu_func)


def unregister():
    bpy.utils.unregister_class(RapidSnapOrigin)
    bpy.types.VIEW3D_MT_edit_mesh_context_menu.append(menu_func)
    bpy.types.VIEW3D_MT_view.append(menu_func)


if __name__ == "__main__":
    register()
    # test call
    bpy.ops.object.rapid_snap_origin()
    

        