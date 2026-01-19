"""
SPIN THE WHEEL - Python Android App
Works with Pydroid 3

Install required library first:
pip install kivy

Then run this file!
"""

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.popup import Popup
from kivy.core.window import Window
from kivy.graphics import PushMatrix, PopMatrix, Rotate
from kivy.uix.widget import Widget
from kivy.clock import Clock
from kivy.properties import NumericProperty
import random

# ============================================
# CUSTOMIZATION - CHANGE COLORS HERE
# ============================================
COLOR_PRIMARY = (0.13, 0.59, 0.95, 1)      # Blue
COLOR_ACCENT = (1, 0.34, 0.13, 1)          # Red-Orange
COLOR_SUCCESS = (0.30, 0.69, 0.31, 1)      # Green
COLOR_BACKGROUND = (0.96, 0.96, 0.96, 1)   # Light gray
COLOR_WHITE = (1, 1, 1, 1)                 # White
COLOR_TEXT = (0.13, 0.13, 0.13, 1)         # Dark text

# ============================================
# CUSTOMIZATION - CHANGE TEXT HERE
# ============================================
APP_TITLE = "🎡 Spin the Wheel"
INPUT_HINT = "Enter an item"
BTN_ADD = "ADD"
BTN_SPIN = "🎯 SPIN THE WHEEL"
LIST_HEADER = "Your Items (Tap to delete):"
INITIAL_MESSAGE = "Add items and spin!"
SPINNING_MESSAGE = "Spinning..."
RESULT_PREFIX = "🎉 Result: "
EMPTY_LIST_ERROR = "Add items first!"
EMPTY_INPUT_ERROR = "Please enter an item"

# ============================================
# CUSTOMIZATION - ANIMATION SPEED
# ============================================
SPIN_DURATION = 3  # 3 seconds


class RotatingWheel(Widget):
    """Custom widget that can rotate using Kivy properties"""
    angle = NumericProperty(0)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        with self.canvas.before:
            PushMatrix()
            self.rotation = Rotate(angle=0, origin=self.center)
        
        with self.canvas.after:
            PopMatrix()
        
        self.bind(center=self.update_rotation_origin)
        self.bind(pos=self.update_rotation_origin, size=self.update_rotation_origin)
        self.bind(angle=self.update_angle)
    
    def update_rotation_origin(self, *args):
        """Update rotation center when widget moves"""
        self.rotation.origin = self.center
    
    def update_angle(self, *args):
        """Update rotation angle"""
        self.rotation.angle = self.angle


class SpinTheWheelApp(App):
    """Main application class"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.wheel_items = []  # Store all items
        self.items_layout = None
        self.result_label = None
        self.wheel_widget = None
        self.spin_button = None
        self.item_input = None
        self.is_spinning = False
        
    def build(self):
        """Build the UI"""
        Window.clearcolor = COLOR_BACKGROUND
        
        # Main container
        main_layout = BoxLayout(
            orientation='vertical',
            padding=20,
            spacing=15
        )
        
        # Title
        title = Label(
            text=APP_TITLE,
            size_hint_y=None,
            height=60,
            font_size='28sp',
            color=COLOR_PRIMARY,
            bold=True
        )
        main_layout.add_widget(title)
        
        # Input row (text field + add button)
        input_row = BoxLayout(
            size_hint_y=None,
            height=50,
            spacing=10
        )
        
        self.item_input = TextInput(
            hint_text=INPUT_HINT,
            multiline=False,
            font_size='16sp',
            background_color=COLOR_WHITE
        )
        input_row.add_widget(self.item_input)
        
        add_button = Button(
            text=BTN_ADD,
            size_hint_x=None,
            width=100,
            background_color=COLOR_SUCCESS,
            color=COLOR_WHITE,
            bold=True
        )
        add_button.bind(on_press=self.add_item)
        input_row.add_widget(add_button)
        
        main_layout.add_widget(input_row)
        
        # List header
        list_header = Label(
            text=LIST_HEADER,
            size_hint_y=None,
            height=30,
            font_size='14sp',
            color=(0.46, 0.46, 0.46, 1)
        )
        main_layout.add_widget(list_header)
        
        # Scrollable items list
        scroll_view = ScrollView(size_hint=(1, 1))
        
        self.items_layout = GridLayout(
            cols=1,
            spacing=2,
            size_hint_y=None
        )
        self.items_layout.bind(minimum_height=self.items_layout.setter('height'))
        
        scroll_view.add_widget(self.items_layout)
        main_layout.add_widget(scroll_view)
        
        # Wheel container with rotating widget and label
        wheel_container = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=100
        )
        
        # Create rotating wheel widget
        self.wheel_widget = RotatingWheel(size_hint=(1, None), height=80)
        
        # Add label on top of rotating widget
        wheel_label = Label(
            text="⚙",
            font_size='60sp',
            color=(1, 0.60, 0, 1),
            size_hint=(1, 1),
            pos_hint={'center_x': 0.5, 'center_y': 0.5}
        )
        self.wheel_widget.add_widget(wheel_label)
        
        wheel_container.add_widget(self.wheel_widget)
        main_layout.add_widget(wheel_container)
        
        # Result display
        self.result_label = Label(
            text=INITIAL_MESSAGE,
            size_hint_y=None,
            height=50,
            font_size='18sp',
            color=COLOR_ACCENT,
            bold=True
        )
        main_layout.add_widget(self.result_label)
        
        # Spin button
        self.spin_button = Button(
            text=BTN_SPIN,
            size_hint_y=None,
            height=60,
            font_size='18sp',
            background_color=COLOR_PRIMARY,
            color=COLOR_WHITE,
            bold=True
        )
        self.spin_button.bind(on_press=self.spin_wheel)
        main_layout.add_widget(self.spin_button)
        
        return main_layout
    
    def add_item(self, instance):
        """Add new item to the wheel"""
        item_text = self.item_input.text.strip()
        
        if not item_text:
            self.show_message(EMPTY_INPUT_ERROR)
            return
        
        # Add to list
        self.wheel_items.append(item_text)
        
        # Clear input
        self.item_input.text = ""
        
        # Refresh display
        self.refresh_items_list()
        
        self.show_message("Item added!")
    
    def refresh_items_list(self):
        """Rebuild the items list display"""
        self.items_layout.clear_widgets()
        
        for i, item in enumerate(self.wheel_items):
            # Create button for each item
            item_button = Button(
                text=f"• {item}",
                size_hint_y=None,
                height=50,
                font_size='16sp',
                background_color=COLOR_WHITE if i % 2 == 0 else (0.98, 0.98, 0.98, 1),
                color=COLOR_TEXT,
                halign='left',
                valign='middle'
            )
            item_button.bind(texture_size=item_button.setter('text_size'))
            item_button.bind(on_press=lambda btn, idx=i: self.delete_item(idx))
            
            self.items_layout.add_widget(item_button)
    
    def delete_item(self, index):
        """Show confirmation dialog to delete item"""
        item = self.wheel_items[index]
        
        # Create popup
        content = BoxLayout(orientation='vertical', spacing=10, padding=10)
        
        message = Label(
            text=f'Delete "{item}"?',
            size_hint_y=None,
            height=40
        )
        content.add_widget(message)
        
        buttons_row = BoxLayout(spacing=10, size_hint_y=None, height=50)
        
        popup = Popup(
            title='Delete Item',
            content=content,
            size_hint=(0.8, 0.3)
        )
        
        delete_btn = Button(
            text='Delete',
            background_color=(0.9, 0.3, 0.3, 1),
            color=COLOR_WHITE
        )
        delete_btn.bind(on_press=lambda x: self.confirm_delete(index, popup))
        
        cancel_btn = Button(
            text='Cancel',
            background_color=(0.5, 0.5, 0.5, 1),
            color=COLOR_WHITE
        )
        cancel_btn.bind(on_press=popup.dismiss)
        
        buttons_row.add_widget(delete_btn)
        buttons_row.add_widget(cancel_btn)
        
        content.add_widget(buttons_row)
        popup.open()
    
    def confirm_delete(self, index, popup):
        """Actually delete the item"""
        self.wheel_items.pop(index)
        self.refresh_items_list()
        popup.dismiss()
        self.show_message("Item deleted")
    
    def spin_wheel(self, instance):
        """Spin the wheel and select random item"""
        if not self.wheel_items:
            self.show_message(EMPTY_LIST_ERROR)
            return
        
        if self.is_spinning:
            return
        
        # Disable button
        self.spin_button.disabled = True
        self.is_spinning = True
        self.result_label.text = SPINNING_MESSAGE
        
        # Calculate target angle: 5 full rotations + random
        extra_rotation = random.randint(0, 360)
        start_angle = self.wheel_widget.angle % 360
        target_angle = start_angle + 1800 + extra_rotation
        
        # Use Clock to animate manually
        self.spin_start_time = Clock.get_time()
        self.spin_start_angle = start_angle
        self.spin_target_angle = target_angle
        self.spin_duration = SPIN_DURATION
        
        Clock.schedule_interval(self.update_spin, 1.0 / 60.0)  # 60 FPS
    
    def update_spin(self, dt):
        """Update spin animation each frame"""
        elapsed = Clock.get_time() - self.spin_start_time
        progress = min(elapsed / self.spin_duration, 1.0)
        
        # Easing function (ease out cubic)
        eased_progress = 1 - pow(1 - progress, 3)
        
        # Calculate current angle
        angle_diff = self.spin_target_angle - self.spin_start_angle
        current_angle = self.spin_start_angle + (angle_diff * eased_progress)
        
        self.wheel_widget.angle = current_angle
        
        # Check if animation is complete
        if progress >= 1.0:
            Clock.unschedule(self.update_spin)
            self.on_spin_complete()
            return False
    
    def on_spin_complete(self):
        """Called when spin animation finishes"""
        self.is_spinning = False
        
        # Pick random item
        selected = random.choice(self.wheel_items)
        
        # Display result
        self.result_label.text = f"{RESULT_PREFIX}{selected}"
        
        # Re-enable button
        self.spin_button.disabled = False
    
    def show_message(self, message):
        """Show a toast-like message"""
        popup = Popup(
            title='',
            content=Label(text=message),
            size_hint=(0.7, 0.2)
        )
        popup.open()
        # Auto close after 1 second
        Clock.schedule_once(lambda dt: popup.dismiss(), 1)


# ============================================
# RUN THE APP
# ============================================
if __name__ == '__main__':
    SpinTheWheelApp().run()