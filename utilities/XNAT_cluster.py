import xnat

def XNAT_download(username,password,path):
    url = "https://qib.shef.ac.uk"

    with xnat.connect(url, user=username, password=password) as session:
        xnatProjects = [project.secondary_id for project in session.projects.values()]
        for x in range(len(xnatProjects)):
            print (str(x) +": " + xnatProjects[x])
        print("Select the project:")
        projectSelected = int(input())
        projectID = xnatProjects[projectSelected]
        
        projectName = [project.name for project in session.projects.values() if project.secondary_id == projectID][0]
        if projectName:
            xnatSubjects = [subject.label for subject in session.projects[projectName].subjects.values()]
            for x_2 in range(len(xnatSubjects)):
                print (str(x_2) +": " + xnatSubjects[x_2])
            print("Select the project:")
            xnatSubjectsSelected = int(input())

            subjectName = xnatSubjects[xnatSubjectsSelected]
            dataset = session.projects[projectName]

            xnatExperiments = [experiment.label for experiment in session.projects[projectName].subjects[subjectName].experiments.values()]
            for x_3 in range(len(xnatExperiments)):
                print (str(x_3) +": " + xnatExperiments[x_3])
            print("Select the project:")
            xnatExperimentsSelected = int(input())
            experimentName = xnatExperiments[xnatExperimentsSelected]
            dataset = session.projects[projectName].subjects[subjectName].experiments[experimentName]
            dataset.download_dir(path)
            return experimentName

def main(username, password, path):

    experimentName = XNAT_download(username,password,path)

    return experimentName

    

