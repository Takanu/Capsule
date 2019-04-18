
from bpy.utils import register_class

from .export_format import CAP_ExportFormat
from .export_format_fbx import CAP_FormatData_FBX
from .export_format_obj import CAP_FormatData_OBJ
from .export_format_gltf import CAP_FormatData_GLTF
from .export_format_abc import CAP_FormatData_Alembic
from .export_format_dae import CAP_FormatData_Collada
from .export_format_stl import CAP_FormatData_STL

# classes = (
#     # CAP_ExportFormat,
#     CAP_FormatData_FBX,
#     CAP_FormatData_OBJ,
#     CAP_FormatData_GLTF
# )

# def register():
#     for cls in classes:
#         register_class(cls)

# def unregister():
#     for cls in classes:
#         register_class(cls)
