import bpy
import os
import time
import gpu
import blf

from gpu_extras.batch import batch_for_shader

from .addon_prefs import get_addon_preferences
from . import global_variables
from . import functions

class AUTORELOAD_OT_reload_images(bpy.types.Operator):
    bl_idname = "autoreload.reload_images"
    bl_label = "Reload Images"
    bl_description = "Reload Images in the blend. if modified"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        wm = context.window_manager
        modified_list, missing_list = functions.reload_modified_images()
        if len(modified_list)!=0: functions.update_viewers(context)
        if len(missing_list) == 0: wm.autoreload_missing_images = False
        else: wm.autoreload_missing_images = True
        for m in modified_list: print(global_variables.print_statement + m + global_variables.reloaded_msg)
        for m in missing_list: print(global_variables.print_statement + m + global_variables.missing_msg)
        if len(modified_list)==0 and len(missing_list)==0: print(global_variables.no_modif_statement)
        return {"FINISHED"}


### UI ###

def load_font(self):
    if self.font_id is not None:
        return
    try:
        self.font_id = blf.load(self.font_path)   
    except:
        raise Exception

def unload_font(self):
    if self.font_id is not None:
        self.font_id = None
        blf.unload(self.font_path)   

def draw_prepare(self):
    blf.color(self.font_id, *self.prefs.icon_color, 1)
    blf.size(self.font_id, self.prefs.icon_size, 72)
    blf.position(self.font_id, self.prefs.icon_offset_x, self.prefs.icon_offset_y, 0)

# callback for loading bar in 3D view 
def draw_callback_px(self, context):
    # Text
    text = "T"
    blf.draw(self.font_id, text)
        

class AUTORELOAD_OT_reload_images_timer(bpy.types.Operator):
    bl_idname = "autoreload.reload_images_timer"
    bl_label = "Reload Images timer"
    bl_description = "Look for modified Images every N seconds and reload them"

    font_id = None
    font_path = os.path.join(functions.get_current_dir(), os.path.join("misc", "heydings_icons.ttf"))
    _timer = None
    oldtimer : bpy.props.FloatProperty()
    prefs = None

    @classmethod
    def poll(cls, context):
        return not bpy.context.window_manager.reload_modal
    
    def __init__(self):     
        bpy.context.window_manager.reload_modal=True
        print(global_variables.timer_start_statement)
        self.prefs = get_addon_preferences()
        if self.prefs.icon_toggle :
            load_font(self)
            draw_prepare(self)

    def modal(self, context, event):
        wm=context.window_manager
        # redraw area
        if self.prefs.icon_toggle :
            try:
                for area in context.screen.areas:
                    if area.type == 'PROPERTIES': area.tag_redraw()
            except AttributeError: pass

        # stop
        if wm.reload_modal==False:
            self.finish(context)
            return {'FINISHED'}

        # timer
        elif event.type == 'TIMER':
            if self.oldtimer!=self._timer.time_duration:
                modified_list, missing_list = functions.reload_modified_images()

                if len(modified_list)!=0: 
                    functions.update_viewers(context)

                if len(missing_list)==0: 
                    wm.autoreload_missing_images=False
                else: 
                    wm.autoreload_missing_images=True

                for m in modified_list: 
                    print(global_variables.print_statement + m + global_variables.reloaded_msg)
                for m in missing_list:
                    print(global_variables.print_statement + m + global_variables.missing_msg)

                self.oldtimer=self._timer.time_duration

        return {'PASS_THROUGH'}

    def execute(self, context):
        addon_preferences = get_addon_preferences()
        freq=addon_preferences.check_frequency

        wm = context.window_manager
        # the arguments we pass the callback
        args = (self, context)
        self._timer = wm.event_timer_add(freq, window=context.window)
        if self.prefs.icon_toggle :
            self._handle = bpy.types.SpaceProperties.draw_handler_add(draw_callback_px, args, 'WINDOW', 'POST_PIXEL')
        wm.modal_handler_add(self)
        return {'RUNNING_MODAL'}

    def finish(self, context):
        if self.prefs.icon_toggle:
            bpy.types.SpaceProperties.draw_handler_remove(self._handle, 'WINDOW')
            unload_font(self)
        wm = context.window_manager
        wm.event_timer_remove(self._timer)
        print(global_variables.timer_end_statement)

    def cancel(self, context):
        if self.prefs.icon_toggle:
            bpy.types.SpaceProperties.draw_handler_remove(self._handle, 'WINDOW')
            unload_font(self)
        wm = context.window_manager
        wm.event_timer_remove(self._timer)
        wm.reload_modal = False
        print(global_variables.timer_end_statement)


class AUTORELOAD_OT_check_libraries(bpy.types.Operator):
    bl_idname = "autoreload.check_libraries"
    bl_label = "Check Libraries"
    bl_description = "Check if external libraries has changed"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        wm = context.window_manager
        modified_list, missing_list = functions.check_libraries()
        if len(missing_list) == 0: wm.autoreload_missing_libraries = False
        else: wm.autoreload_missing_libraries = True
        for m in modified_list: print(global_variables.print_statement + m + global_variables.reloaded_msg)
        for m in missing_list: print(global_variables.print_statement + m + global_variables.missing_msg)
        return {"FINISHED"}


class AUTORELOAD_OT_reload_library(bpy.types.Operator):
    bl_idname = "autoreload.reload_library"
    bl_label = "Reload Library"
    bl_description = "Reload this external library"
    bl_options = {"INTERNAL", "UNDO"}

    name : bpy.props.StringProperty()

    def execute(self, context):
        functions.reload_library(self.name)
        return {"FINISHED"}


class AUTORELOAD_OT_save_revert(bpy.types.Operator):
    bl_idname = "autoreload.save_revert"
    bl_label = "Save and Revert"
    bl_description = "Save file and revert to reload all libraries"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return bpy.data.is_saved

    def execute(self, context):
        bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
        bpy.ops.wm.revert_mainfile()
        return {"FINISHED"}


### REGISTER ---

def register():
    bpy.utils.register_class(AUTORELOAD_OT_reload_images)
    bpy.utils.register_class(AUTORELOAD_OT_reload_images_timer)
    bpy.utils.register_class(AUTORELOAD_OT_check_libraries)
    bpy.utils.register_class(AUTORELOAD_OT_reload_library)
    bpy.utils.register_class(AUTORELOAD_OT_save_revert)

def unregister():
    bpy.utils.unregister_class(AUTORELOAD_OT_reload_images)
    bpy.utils.unregister_class(AUTORELOAD_OT_reload_images_timer)
    bpy.utils.unregister_class(AUTORELOAD_OT_check_libraries)
    bpy.utils.unregister_class(AUTORELOAD_OT_reload_library)
    bpy.utils.unregister_class(AUTORELOAD_OT_save_revert)