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

    def run(self, app): # temporary - joining series (slow)

        app.status.message('Merging..')

        series_list = app.folder.series(checked=True)
        merged = series_list[0].new_sibling()
        #parent = merged.parent # should not be a property
        nr = str(len(series_list))
        for j, series in enumerate(series_list):
            msg = 'Merging series ' + series.label() + ' (' + str(j+1) + ' of ' + nr + ')'
            #series.copy_to(parent, message=msg, UID=merged.UID[-1])
            series.merge_with(merged, message=msg)
#            children = series.children()
#            for i, child in enumerate(children):
#                app.status.progress(i, len(children), message=msg)
#                child.copy_to(merged)
        app.status.hide()
        app.refresh()

    def run_draft(self, weasel): # Should be faster if not done one-by-one

        df = weasel.folder.data()
        df = df[df['checked']==True]

        id = df.SeriesInstanceUID.unique()
        if len(id) == 1:
            msg = 'The selected images are already merged.'
            msg = '\n Use group to combine them in a new series.'
            weasel.dialog.information(msg)
            return
        series_id = weasel.folder.new_uid()

        id = df.StudyInstanceUID.unique()
        if len(id) == 1:    # series in the same study
            study_id = id[0]
            patient_id = df.iloc[0].PatientID
        else:               # series in different studies
            study_id = weasel.folder.new_uid()
            id = df.PatientID.unique()
            if len(id) == 1:    # different studies of the same patient
                patient_id = id[0]
            else:               # studies in different patients
                patient_id = weasel.folder.new_uid()

        dfmerge = df.copy(deep=True)
        dfmerge['files'] = [weasel.folder.new_file() for _ in range(df.shape[0])]
        dfmerge.set_index('files', inplace=True)
        dfmerge.PatientID = patient_id      # dropped .values[:]
        dfmerge.StudyInstanceUID = study_id
        dfmerge.SeriesInstanceUID = series_id
        dfmerge.SOPInstanceUID = [weasel.folder.new_uid() for _ in range(df.shape[0])]
        dfmerge.checked = True
        dfmerge.removed = False
        dfmerge.created = True

        for i in range(df.shape[0]):
            pass # copy file


    def run_orig(self, app): #More general but needs debugging

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

        parents = [obj.parent for obj in objects]
        return list(set(parents))

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