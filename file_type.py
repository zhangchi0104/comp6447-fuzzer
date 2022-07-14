import json
import file_code

def get_type(sampleInput):
  if checkJSON(sampleInput):
    return file_code.JSON
  else:
    return file_code.CSV

# Given the sample input file, determines if it has the same format as a JSON file.
def checkJSON(sampleInput):
    if sampleInput[0] != '{' and sampleInput[-1] != '}':
      return False
      
    try:
        json.loads(sampleInput)
    # If an exception is raised, then it is not valid json format.
    except:
        print("Not a JSON file...")
        return False

    return True
    
def checkCSV(sampleInput):
    return True