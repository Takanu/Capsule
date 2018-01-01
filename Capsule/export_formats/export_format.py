
import bpy
from bpy.props import IntProperty, FloatProperty, BoolProperty, StringProperty, PointerProperty, CollectionProperty, EnumProperty
from bpy.types import AddonPreferences, PropertyGroup
from bpy.types import UILayout

# used to define the properties for different formats that Capsule can export to.

class CAP_FormatData_Undefined(PropertyGroup):
        test = BoolProperty(
           name="Test!",
           description="TEEEEEEST!",
           default=True,
        )

class CAP_ExportFormat:
	"""
	Defines a single export format that Capsule can export to.
	"""

	def __init__(self):
		self.type = 'Undefined'

	def draw_addon_preferences(self, layout):
		"""
		Draws the panel that represents all the options that the export format has.
		"""

		column = layout.column(align=True)
		column.label("This export type is undefined, someone let a base class here! D:")
		return

	def draw_selection_preferences(self, layout):
		"""
		Draws the panel that represents all the options that the export format 
		has for specific selections of objects and groups.
		"""

		column = layout.column(align=True)
		column.label("This export type is undefined, someone let a base class here! D:")
		return



