import bpy

def CheckSuffix(string, suffix):
    """
    Attempts to find the given suffix in a string.
    """
    strLength = len(string)
    suffixLength = len(suffix)
    diff = strLength - suffixLength
    index = string.rfind(suffix)

    #print("String Length...", strLength)
    #print("Suffix Length...", suffixLength)
    #print("Diff............", diff)
    #print("Index...........", index)

    if index == diff and index != -1:
        #print("Suffix is True")
        return True

    else:
        #print("Suffix is False")
        return False

def CheckPrefix(string, prefix):
    """
    Attempts to find the given prefix in a string.
    """
    strLength = len(string)
    prefixLength = len(prefix)
    index = string.find(prefix)

    print("String..........", string)
    print("Prefix..........", prefix)
    print("String Length...", strLength)
    print("Prefix Length...", prefixLength)
    print("Index...........", index)

    if index == 0:
        print("Suffix is True")
        return True

    else:
        print("Suffix is False")
        return False