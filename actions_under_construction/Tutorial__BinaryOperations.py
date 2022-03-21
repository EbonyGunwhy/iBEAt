
    
#**************************************************************************
# Template part of a tutorial 
# Performs a binary operation on two images and saves them in a new series, 
# image by image and showing a progress bar. 
#**************************************************************************

def main(weasel):
    images = weasel.images()
    list_operations = ["A * B", "A / B", "A + B", "A - B"]
    cancel, fields = weasel.user_input(
        {"type":"dropdownlist", "label":"Image A", "list":images.label, "default":0},
        {"type":"dropdownlist", "label":"Image B", "list":images.label, "default":0},
        {"type":"dropdownlist", "label":"Operation", "list":list_operations, "default":0},
        title="Settings for binary operation")
    if cancel: return

    imageA = images[fields[0]['value']]
    imageB = images[fields[1]['value']]
    operation = list_operations[fields[2]['value']]
    # fields[X]['value'] is the index of the chosen value in the input list that it refers to.

    if operation == "A * B":
        result = imageA.copy(suffix="_Multiplication_" + imageA.label + "_" + imageB.label)
        result.write(imageA.array() * imageB.array())
    elif operation == "A / B":
        result = imageA.copy(suffix="_Division_" + imageA.label + "_" + imageB.label)
        result.write(imageA.array() / imageB.array())
    elif operation == "A + B":
        result = imageA.copy(suffix="_Sum_" + imageA.label + "_" + imageB.label)
        result.write(imageA.array() + imageB.array())
    elif operation == "A - B":
        result = imageA.copy(suffix="_Subtraction" + imageA.label + "_" + imageB.label)
        result.write(imageA.array() - imageB.array())
        
    result.display()
    weasel.refresh()