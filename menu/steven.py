import wezel


def dummy_menu(parent): 

    parent.action(Dummy, text="Dummy")


class Dummy(wezel.gui.Action):
    pass