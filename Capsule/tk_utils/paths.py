
import bpy, os, platform

from datetime import datetime


def CreateFilePath(location_preset, targets, collection, replace_invalid_chars, meta):
    """
    Extracts and calculates a final path with which to export the target to.
    """

    # First fetch the path
    location_path = location_preset.path

    if location_path == "":
            return 'WARNING: This location preset has no path defined, please define it!'

    elif location_path.find('//') != -1:
        location_path = bpy.path.abspath(location_path)

    # If Windows, split the drive indicator
    drive_indicator = ""
    if platform.system() == 'Windows':
        drive_index = location_path.find("\\")

        if drive_index is not -1:
            drive_split = location_path.split("\\", 1)
            drive_indicator = drive_split[0]
            location_path = drive_split[1]
    

    print("Current Location Path - ", location_path)

    # Now substitute any tags
    location_path = FillTags(location_path, targets, collection, replace_invalid_chars, meta)

    # directory failsafe
    if platform.system() == 'Windows':
        if location_path.endswith("\\") == False:
            location_path += "\\"
    else:
        if location_path.endswith("/") == False:
            location_path += "/"
    
    if replace_invalid_chars is True:
        location_path = SubstitutePathCharacters(location_path)

    # Windows drive indicator re-stitch
    if drive_indicator is not "":
        location_path = drive_indicator + "\\" + location_path
    
    # Build the file path
    if not os.path.exists(location_path):
        os.makedirs(location_path)
    
    print("Final Location Path - ", location_path)
    
    return location_path



def FillTags(location_path, targets, collection, replace_invalid_chars, meta):
    """
    Searches for and substitutes the tags in a path name.
    """

    slash = "/"
    if platform.system() == 'Windows':
        slash = "\\"

    if location_path.find('^export_name^'):

        if collection is not None:
            export_name = collection.name
        else:
            export_name = targets[0].name

        if replace_invalid_chars is True:
            export_name = SubstituteDirectoryCharacters(export_name)

        location_path = location_path.replace('^object_name^', export_name)
    

    # if location_path.find('^object_type^'):

    #     type_name = targets[0].type
    #     type_name = type_name.lower()
    #     type_name = type_name.capitalize()

    #     if replace_invalid_chars is True:
    #         type_name = SubstituteDirectoryCharacters(type_name)

    #     location_path = location_path.replace('^object_type^', type_name)
    

    # if location_path.find('^collection^'):
        
    #     collection_name = ''
    #     if collection != None:
    #         collection_name = collection.name
    #     else:
    #         if targets[0].users_collection[0]:
    #             collection_name = targets[0].users_collection[0].name
    #         else:
    #             collection_name = "Unknown Collection"
        
    #     if replace_invalid_chars is True:
    #         collection_name = SubstituteDirectoryCharacters(collection_name)
                
    #     location_path = location_path.replace('^collection^', collection_name)

    
    if location_path.find('^blend_file_name^'):

        blend_name = bpy.path.basename(bpy.context.blend_data.filepath)
        blend_name = blend_name.replace(".blend", "")

        if replace_invalid_chars is True:
            blend_name = SubstituteDirectoryCharacters(blend_name)

        location_path = location_path.replace('^blend_file_name^', blend_name)
    
    if location_path.find('^export_preset_name^'):

        preset_name = meta['preset_name']

        if replace_invalid_chars is True:
            blend_name = SubstituteDirectoryCharacters(preset_name)

        location_path = location_path.replace('^export_preset_name^', preset_name)
    
    # DATE AND TIME

    if location_path.find('export_date_ymd'):

        time = meta['export_time'].strftime('%Y-%m-%d')
        location_path = location_path.replace('^export_date_ymd^', time)

    if location_path.find('export_date_dmy'):

        time = meta['export_time'].strftime('%d-%m-%Y')
        location_path = location_path.replace('^export_date_dmy^', time)

    if location_path.find('export_date_mdy'):

        time = meta['export_time'].strftime('%m-%d-%Y')
        location_path = location_path.replace('^export_date_mdy^', time)
    
    if location_path.find('export_time_hm'):

        time = meta['export_time'].strftime('%H.%M')
        location_path = location_path.replace('^export_time_hm^', time)

    if location_path.find('export_time_hms'):

        time = meta['export_time'].strftime('%H.%M.%S')
        location_path = location_path.replace('^export_time_hms^', time)
    
    return location_path    

    
def SubstituteDirectoryCharacters(path):
  # Replaces invalid directory characters in names

  print("Checking Directory...", path)
  result = path
  if platform.system() == 'Windows':
      invalid_characters = ["\\", "/", "*", "?", "\"", "<", ">", "|", ":"]
      for char in invalid_characters:
          result = result.replace(char, "_")

  elif platform.system() == 'Darwin':
      invalid_characters = [":", "/"]
      for char in invalid_characters:
          result = result.replace(char, "_")

  elif platform.system() == 'linux' or platform.system() == 'linux2':
      invalid_characters = [":", "/"]
      for char in invalid_characters:
          result = result.replace(char, "_")

  return result

def SubstitutePathCharacters(path):
  # Replaces invalid directory characters in full export paths

  print("Checking Directory...", path)
  result = path
  if platform.system() == 'Windows':
      invalid_characters = ["*", "?", "<", ">", "|", ":"]
      for char in invalid_characters:
          result = result.replace(char, "_")

  elif platform.system() == 'Darwin':
      invalid_characters = [":"]
      for char in invalid_characters:
          result = result.replace(char, "_")

  elif platform.system() == 'linux' or platform.system() == 'linux2':
      invalid_characters = [":"]
      for char in invalid_characters:
          result = result.replace(char, "_")

  return result



def CheckSystemChar(path):
  # Checks for invalid directory characters in names

  print("Checking Directory...", path)
  if platform.system() == 'Windows':
      invalid_characters = ["/", "*", "?", "\"", "<", ">", "|", ":"]
      invalid_captured = []
      for char in invalid_characters:
          if path.find(char) != -1:
              invalid_captured.append(char)

  elif platform.system() == 'Darwin':
      invalid_characters = [":", "/"]
      invalid_captured = []
      for char in invalid_characters:
          if path.find(char) != -1:
              invalid_captured.append(char)

  elif platform.system() == 'linux' or platform.system() == 'linux2':
      invalid_characters = [":", "/"]
      invalid_captured = []
      for char in invalid_characters:
          if path.find(char) != -1:
              invalid_captured.append(char)

  print("Invalid characters found...", invalid_captured)
  return invalid_captured