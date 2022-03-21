from weasel.core import Action

def menu(parent):

    parent.action(Copy)
    parent.action(Delete)
    parent.action(Merge)
    parent.action(Group)


class Copy(Action):

    def enable(self, app):

        if not hasattr(app, 'folder'):
            return False
        data = app.folder.data()
        if data.empty: 
            return False
        return data.checked.any()

    def run(self, app):

        app.status.cursorToHourglass()
        app.status.message("Copying.. ")
        self.copy_checked_offspring(app.folder, app.status)
        app.status.cursorToNormal()
        app.refresh()

    def copy_checked_offspring(self, obj, status):

        for child in obj.children():
            if child.is_checked():
                status.message("copying " + child.label())
                child.copy()
            else:
                self.copy_checked_offspring(child, status)


class Delete(Action):

    def enable(self, app):

        if not hasattr(app, 'folder'):
            return False
        data = app.folder.data()
        if data.empty: 
            return False
        return data.checked.any()

    def run(self, app):

        instances = app.folder.instances(checked=True)        
        app.status.message("Deleting..")
        for i, instance in enumerate(instances):   
            app.status.progress(i+1, len(instances))
            instance.remove()               
        app.status.hide()
        app.refresh()


class Merge(Action):

    def enable(self, app):

        if not hasattr(app, 'folder'):
            return False
        data = app.folder.data()
        if data.empty: return False
        return data.checked.any()

    def run(self, app):

        app.status.message('Merging..')
        unchecked = [app.folder]
        
        unchecked = self.merge_children(unchecked)
        if unchecked == []: return
        unchecked = self.merge_children(unchecked)
        if unchecked == []: return
        unchecked = self.merge_children(unchecked)
        if unchecked == []: return

        app.refresh()

    def merge_children(self, objects):

        checked, unchecked = self.split_children(objects)
        if len(checked) == 1:
            unchecked.extend(checked)
        else: 
            self.merge(checked)
        return unchecked

    def split_children(self, objects):

        checked = []
        unchecked = []
        for obj in objects:
            checked.extend(obj.children(checked=True))
            unchecked.extend(obj.children(checked=False))   
        return checked, unchecked

    def merge(self, objects):

        if len(objects) >= 2:
            sibling = self.new_sibling(objects)
            for obj in objects:
                for child in obj.children():
                    child.copy_to(sibling)

    def new_sibling(self, objects):

        parent_list = self.parents(objects)
        if len(parent_list) == 1:
            parent = parent_list[0]
        else:
            parent = self.new_sibling(parent_list)
        return parent.new_child()

    def parents(self, objects):

        parents = []
        for obj in objects:
            parent = obj.parent
            if parent not in parents:
                parents.append(parent)
        return parents


class Group(Action):

    def enable(self, app):

        if not hasattr(app, 'folder'):
            return False
        data = app.folder.data()
        if data.empty: 
            return False
        return data.checked.any()

    def run(self, app):

        app.status.cursorToHourglass()
        app.status.message('Grouping..')
        unchecked = app.folder.patients()
        
        unchecked = self.group_children(unchecked)
        if unchecked == []: return
        unchecked = self.group_children(unchecked)
        if unchecked == []: return
        unchecked = self.group_children(unchecked)
        if unchecked == []: return

        app.refresh()
        app.status.cursorToNormal()

    def group_children(self, objects):

        checked, unchecked = self.split_children(objects) 
        self.group(checked)
        return unchecked

    def split_children(self, objects):

        checked = []
        unchecked = []
        for obj in objects:
            checked.extend(obj.children(checked=True))
            unchecked.extend(obj.children(checked=False))   
        return checked, unchecked

    def group(self, objects):

        if len(objects) >= 1:
            parent = self.new_parent(objects)
            for obj in objects:
                obj.copy_to(parent)

    def new_parent(self, objects):

        parent = self.ancestor(objects)
        if parent.generation == objects[0].generation - 1:
            return parent.parent.new_child()
        if parent.generation == objects[0].generation - 2:
            return parent.new_child()
        if parent.generation == objects[0].generation - 3:
            return parent.new_child().new_child()
        if parent.generation == objects[0].generation - 4:
            return parent.new_child().new_child().new_child()
        
    def ancestor(self, objects):

        objects = self.parents(objects)
        if len(objects) == 1:
            return objects[0]
        else:
            return self.ancestor(objects)

    def parents(self, objects):

        parents = []
        for obj in objects:
            parent = obj.parent
            if parent not in parents:
                parents.append(parent)
        return parents