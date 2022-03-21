

#**************************************************************************
# Tutorial showing the use of user_input()
# Runs the user input window in various configurations
#***************************************************************************

def main(weasel):

    filters = ["Gaussian", "Uniform", "Median", "Maximum", "Wiener"]
    flavours = ["Chocolate", "Vanilla", "Strawberry"]

    cancel, input = weasel.user_input(
        {"label":"Which filter?", "type":"listview", "list": filters},
        {"label":"Which filter?", "type":"dropdownlist", "list": filters, "value": 2},
        {"label":"Which flavour?", "type":"dropdownlist", "list": flavours},
        {"label":"Filter size in pixels", "type":"float"},
        {"label":"Type a string", "type":"string","value":"hello world!"},
        {"label":"Which flavour?", "type":"listview", "list":flavours},
        {"label":"An integer between 0 and 1000", "type":"integer", "value":20, "minimum": 0, "maximum": 1000}, 
        {"label":"An integer larger than -100", "type":"float", "value":20, "minimum": -100}, 
        {"label":"An integer less than 1000", "type":"integer", "value":30, "maximum": 1000},
        {"label":"Any integer", "type":"integer", "value":40},
        {"label":"Any integer", "type":"integer"},
        {"label":"Type a string", "type":"string","value":"hello world!"},
        title = "Can we have some input?")
    if cancel: return

    for field in input:
        print(field["label"])
        print(field["value"])
