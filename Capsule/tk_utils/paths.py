
import bpy, os, platform


def CreateFilePath(location_preset, targets, collection, replace_invalid_chars):
    """
    Extracts and calculates a final path with which to export the target to.
    """

    # First fetch the path
    location_path = location_preset.path

    if location_path == "":
            return 'WARNING: This location preset has no path defined, please define it!'

    elif location_path.find('//') != -1:
        location_path = bpy.path.abspath(location_path)

    print(location_path)

    # Now substitute any tags
    location_path = FillTags(location_path, targets, collection, replace_invalid_chars)

    # directory failsafe
    if location_path.endswith("/") == False:
        location_path += "/"
    
    # Build the file path
    if not os.path.exists(location_path):
        os.makedirs(location_path)
    
    
    return location_path



def FillTags(location_path, targets, collection, replace_invalid_chars):
    """
    Searches for and substitutes the tags in a path name.
    """

    slash = "/"
    if platform.system() == 'Windows':
        slash = "\\"

    if location_path.find('^object_name^'):

        object_name = targets[0].name

        if replace_invalid_chars is True:
            object_name = ReplaceSystemChar(object_name)

        location_path = location_path.replace('^object_name^', object_name)
    

    if location_path.find('^object_type^'):

        type_name = targets[0].type
        type_name = type_name.lower()
        type_name = type_name.capitalize()

        if replace_invalid_chars is True:
            type_name = ReplaceSystemChar(type_name)

        location_path = location_path.replace('^object_type^', type_name)
    

    if location_path.find('^collection^'):
        
        collection_name = ''
        if collection != None:
            collection_name = collection.name
        else:
            if targets[0].users_collection[0]:
                collection_name = targets[0].users_collection[0].name
            else:
                collection_name = "Unknown Collection"
        
        if replace_invalid_chars is True:
            collection_name = ReplaceSystemChar(collection_name)
                
        location_path = location_path.replace('^collection^', collection_name)

    
    if location_path.find('^blend_file_name^'):

        blend_name = bpy.path.basename(bpy.context.blend_data.filepath)
        blend_name = blend_name.replace(".blend", "")

        if replace_invalid_chars is True:
            blend_name = ReplaceSystemChar(blend_name)

        location_path = location_path.replace('^blend_file_name^', blend_name)
    
    return location_path    

    
def ReplaceSystemChar(path):
  # Replaces invalid directory characters in names

  print("Checking Directory...", path)
  result = path
  if platform.system() == 'Windows':
      invalid_characters = ["/", "*", "?", "\"", "<", ">", "|", ":"]
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