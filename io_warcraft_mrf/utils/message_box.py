import bpy

class MessageBox:
    @staticmethod
    def show(message="", title="Message Box", icon='INFO'):
        def draw(self, context):
            self.layout.label(text=message)

        bpy.context.window_manager.popup_menu(draw, title=title, icon=icon)
        print(f"{title} {message}")