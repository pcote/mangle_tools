# mangle_tools.py (c) 2011 Phil Cote (cotejrp1)
#
# ***** BEGIN GPL LICENSE BLOCK *****
#
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.	See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ***** END GPL LICENCE BLOCK *****

bl_info = {
    'name': 'Mangle Tools',
    'author': 'Phil Cote, cotejrp1, (http://www.blenderaddons.com)',
    'version': (0,1),
    "blender": (2, 6, 0),
    "api": 41098,
    'location': 'VIEW 3D -> TOOLS',
    'description': 'Set of tools to mangle curves, meshes, and shape keys',
    'warning': '',
    'category': 'Object'}


import bpy
import random
import time
from math import pi

class MeshManglerOperator(bpy.types.Operator):
    '''push vertices on the selected object around in random directions to 
    create a crumpled look'''
    bl_idname = "ba.mesh_mangler"
    bl_label = "Mesh Mangler"
    bl_options = { "REGISTER", "UNDO" }
    

    @classmethod
    def poll(cls, context):
        ob = context.active_object
        return ob != None and ob.type == 'MESH'

    def execute(self, context):
        random.seed( time.time() )
        
        mesh = context.active_object.data
        
        if mesh.shape_keys != None:
            self.report( {"INFO"}, "Cannot mangle mesh: Shape keys present" )
            return {'CANCELLED'}
        
        randomMag = bpy.context.scene.random_magnitude
        
        for vert in mesh.vertices:
            xVal = .01 * random.randrange( -randomMag, randomMag )
            yVal = .01 * random.randrange( -randomMag, randomMag)
            zVal = .01 * random.randrange( -randomMag, randomMag )
            vert.co.x = vert.co.x + xVal
            vert.co.y = vert.co.y + yVal
            vert.co.z = vert.co.z + zVal
                
            
        return {'FINISHED'}

class AnimanglerOperator(bpy.types.Operator):
    '''makes a shape key and pushes the verts around on it to set up for random pulsating animation'''
    bl_idname = "ba.ani_mangler"
    bl_label = "Ani-Mangle"
    

    @classmethod
    def poll(cls, context):
        ob = context.active_object
        return ob != None and ob.type in [ 'MESH', 'CURVE' ]

    def execute(self, context):
        scn = context.scene
        random.seed( time.time() )
        randomMag = scn.random_magnitude
        mangleName = scn.mangle_name
        ob = context.object
        shapeKey = ob.shape_key_add( name=mangleName )
        verts = shapeKey.data
        
        for vert in verts:
            xVal = .01 * random.randrange( -randomMag, randomMag )
            yVal = .01 * random.randrange( -randomMag, randomMag )
            zVal = .01 * random.randrange( -randomMag, randomMag )
            vert.co.x = vert.co.x + xVal
            vert.co.y = vert.co.y + yVal
            vert.co.z = vert.co.z + zVal    
            
        return {'FINISHED'}

def curve_main(context):
    
    def mangle_points(points):
        for point in points:
            random.seed(time.time())
            random_mag = bpy.context.scene.random_magnitude
            
            new_x = point.co.x + (2 * pi *.01 * random.randrange(-random_mag, random_mag))
            new_y = point.co.y + (2 * pi * .01 * random.randrange(-random_mag, random_mag))
            new_z = point.co.z + (2 * pi* .01 * random.randrange(-random_mag, random_mag))
            point.co.xyz = new_x, new_y, new_z
    
    
    ob = context.active_object
    random.seed( time.time() )
    splines = context.object.data.splines
    
    for spline in splines:
        if spline.type == 'BEZIER':
            mangle_points(spline.bezier_points)
        elif spline.type in ('POLY', 'NURBS'):
            mangle_points(spline.points)
        
    
class CurveManglerOp(bpy.types.Operator):
    '''Mangles a curve to the degree the user specifies'''
    bl_idname = "ba.curve_mangler"
    bl_label = "Curve Mangler"
    bl_options = { 'REGISTER', 'UNDO' }

    @classmethod
    def poll(cls, context):
        ob = context.active_object
        return ob != None and ob.type == "CURVE"


    def execute(self, context):
        curve_main(context)
        return {'FINISHED'}


class MangleToolsPanel(bpy.types.Panel):
    bl_label = "Mangle Tools"
    bl_space_type = "VIEW_3D"
    bl_region_type="TOOLS"
    bl_context = "objectmode"

    def draw(self, context):
        scn = context.scene
        layout = self.layout
        col = layout.column()
        col.prop(scn, "random_magnitude")   
        col.prop(scn, "mangle_name")     
        col.operator("ba.curve_mangler")
        col.operator("ba.mesh_mangler")
        col.operator("ba.ani_mangler")


IntProperty = bpy.props.IntProperty
StringProperty = bpy.props.StringProperty

def register():
    bpy.utils.register_class(AnimanglerOperator)
    bpy.utils.register_class(MeshManglerOperator)
    bpy.utils.register_class(CurveManglerOp)
    bpy.utils.register_class(MangleToolsPanel)
    scnType = bpy.types.Scene
    scnType.random_magnitude = IntProperty( name = "How Much Mangling", 
                              default = 20, min = 1, max = 30, 
                              description = "The (+) and (-) number range for a random number to be picked from" )
    
    scnType.mangle_name = StringProperty(name="Mangle Shape Key Name",
                             default="mangle",
                             description="Name given for mangled shape keys")
def unregister():
    bpy.utils.unregister_class(AnimanglerOperator)
    bpy.utils.unregister_class(MeshManglerOperator)
    bpy.utils.unregister_class(MangleToolsPanel)
    bpy.utils.unregister_class(CurveManglerOp)


if __name__ == "__main__":
    register()