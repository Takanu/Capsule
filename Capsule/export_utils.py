
import bpy, bmesh, os, platform

from mathutils import Vector
from math import pi, radians, degrees
from bpy.types import Operator

from .tk_utils import select as select_utils

def ReplaceSystemChar(context, name):
  # Replaces invalid directory characters in names

  print("Checking Directory...", name)
  returnName = name
  if platform.system() == 'Windows':
      invalidCharacters = ["/", "*", "?", "\"", "<", ">", "|", ":"]
      for char in invalidCharacters:
          returnName = returnName.replace(char, "_")

  elif platform.system() == 'Darwin':
      invalidCharacters = [":", "/"]
      for char in invalidCharacters:
          returnName = returnName.replace(char, "_")

  elif platform.system() == 'linux' or platform.system() == 'linux2':
      invalidCharacters = [":", "/"]
      for char in invalidCharacters:
          returnName = returnName.replace(char, "_")

  return returnName



def CheckSystemChar(context, name):
  # Checks for invalid directory characters in names

  print("Checking Directory...", name)
  if platform.system() == 'Windows':
      invalidCharacters = ["/", "*", "?", "\"", "<", ">", "|", ":"]
      invalidCaptured = []
      for char in invalidCharacters:
          if name.find(char) != -1:
              invalidCaptured.append(char)

  elif platform.system() == 'Darwin':
      invalidCharacters = [":", "/"]
      invalidCaptured = []
      for char in invalidCharacters:
          if name.find(char) != -1:
              invalidCaptured.append(char)

  elif platform.system() == 'linux' or platform.system() == 'linux2':
      invalidCharacters = [":", "/"]
      invalidCaptured = []
      for char in invalidCharacters:
          if name.find(char) != -1:
              invalidCaptured.append(char)

  print("Invalid characters found...", invalidCaptured)
  return invalidCaptured



def CheckAnimation(context):
  # Might end up in a future update, old code for fetching animation data.

  for item in context.scene.objects:
      print(item.name)
      print(item.animation_data)

      if item.animation_data is not None:
          print(item.animation_data.action)
          print(item.animation_data.drivers)
          print(item.animation_data.nla_tracks)

          for driver in item.animation_data.drivers:
              print("------Driver:", driver)
              print(len(driver.driver.variables))

              for variable in driver.driver.variables:
                  print("---Variable:", variable.name)
                  print(len(variable.targets))

                  for target in variable.targets:
                      print("-Target:", target)
                      print("Bone Target.....", target.bone_target)
                      print("Data Path.......", target.data_path)
                      print("ID..............", target.id)
                      print("ID Type.........", target.id_type)
                      print("Transform Space.", target.transform_space)
                      print("Transform Type..", target.transform_type)

          if item.animation_data.action is not None:
              action = item.animation_data.action
              print("FCurves......", action.fcurves)
              print("Frame Range..", action.frame_range)
              print("Groups.......", action.groups)
              print("ID Root......", action.id_root)

              for curve in action.fcurves:
                  print(curve.driver.data_path)
                  #for variable in curve.driver.variables:
                      #for target in variable.targets:
                          #print("-Target:", target)
                          #print("Bone Target.....", target.bone_target)
                          #print("Data Path.......", target.data_path)
                      #    print("ID..............", target.id)
                      #    print("ID Type.........", target.id_type)
                      #    print("Transform Space.", target.transform_space)
                      #    print("Transform Type..", target.transform_type)


  print(">>>> CHECKED ANIMATION <<<<")

def AddTriangulate(targetList):
  """
  Adds the triangulate modifier to any objects that don't yet have it.
  """

  modType = {'TRIANGULATE'}

  for item in targetList:
      if item.type == 'MESH':
          stm = item.CAPStm
          stm.has_triangulate = False

          for modifier in item.modifiers:
              if modifier.type in modType:
                  stm.has_triangulate = True

          # if we didn't find any triangulation, add it!
          if stm.has_triangulate == False:
              select_utils.FocusObject(item)
              bpy.ops.object.modifier_add(type='TRIANGULATE')

              for modifier in item.modifiers:
                  if modifier.type in modType:
                      #print("Triangulation Found")
                      modifier.quad_method = 'FIXED_ALTERNATE'
                      modifier.ngon_method = 'CLIP'
                      stm.has_triangulate = False

def RemoveTriangulate(targetList):
  """
  Adds the triangulate modifier from objects where it was added as an export option.
  """
  modType = {'TRIANGULATE'}

  for item in targetList:
      if item.type == 'MESH':
          if item.CAPStm.has_triangulate is False:
              for modifier in item.modifiers:
                  if modifier.type in modType:
                      select_utils.FocusObject(item)
                      bpy.ops.object.modifier_remove(modifier=modifier.name)


                      