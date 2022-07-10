import json

# Given the sample input file, determines if it has the same format as a JSON file.
def checkJSON(sampleInput):
    sampleInput.seek(0)
    try:
        # First we need to read the file and store its contents in a variable.
        fileContents = sampleInput.read().strip()

        # Then, the loads function attempts to decode the file's contents as
        # json format.
        json.loads(fileContents)

    # If an exception is raised, then it is not valid json format.
    except:
        print("Not a JSON file...")
        return False

    return True