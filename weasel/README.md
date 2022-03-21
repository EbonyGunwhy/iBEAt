<h2 align="center"><img src="documents/uni-sheffield-logo.png" height="128"></h2>

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
![Software](https://img.shields.io/badge/Software-DICOM%20Viewer-green)
![Status](https://img.shields.io/badge/Status-Prototype-orange)

# Weasel

Weasel is a Python environment for developing and deploying quantitative medical imaging applications.

It aims to simplify the process of testing prototype image processing pipelines on clinical data, by avoiding the need for dedicated graphical interface development and removing the overhead involved in interfacing with DICOM databases.

This will speed up the translation of new methods into early stage clinical studies, bringing forward the point where prototypes can be stress-tested under real world conditions.

# Installation

**Git** is required to download this repository, unless you choose to download the `.zip` file. In order for Weasel to run successfully, it is required to have **Python (>=3.7)** installed.

Download URLs:

[Git](https://git-scm.com/downloads)

[Python](https://www.python.org/downloads/)

If the images you wish to work with are Enhanced/Multiframe DICOM, then it is required to have **Java JDK** installed so that `dcm4che` can work correctly. If you're using an old OS, it is recommended that you scroll down when navigating the link below and choose an older version of **Java JDK** to install.

[Java JDK](https://www.oracle.com/java/technologies/downloads/)

There are 2 options downloading and installing Weasel requirements:

#### Option 1
Download and install everything in one go by opening a Terminal (MacOS and Linux) or a CMD (Windows) and type in the following command:

`pip install -e git+https://github.com/QIB-Sheffield/WEASEL#egg=WEASEL --src <download_path>`

After the installation is finished, it's recommended that you go to the directory where Weasel was installed

`cd <download_path>/weasel`

and run the command

`python setup.py clean` 

to clean the installation files that are not needed anymore.

#### Option 2
First, download the repository via `git clone` or by downloading the `.zip` file and extracting its contents.
Then open a Terminal (MacOS and Linux) or a CMD (Windows), navigate to the downloaded Weasel folder

`cd <Weasel_folder_path>`

and run the command 

`pip install -e .` 

to install all Weasel dependencies. Finally, run the command

`python setup.py clean` 

to clean the installation files that are not needed anymore.

#### For users that are more familiar with Python (Developers)
Running `pip install -e .` will read the `setup.py` file and install the required Python packages to run Weasel successfully. If there are any other Python packages you wish to be installed with Weasel, you can edit the `setup.py` file and add packages to the variable `extra_requirements`.

The core Python modules used in Weasel are in requirements.txt so alternatively you may choose to run `pip install -r requirements.txt` and then any other Python packages of your choice can be installed separately in your machine or in your virtual environment.

# Start Weasel Graphical User Interface
Open a Terminal (MacOS and Linux) or a CMD (Windows), navigate to the downloaded Weasel folder

`cd <Weasel_folder_path>`

and start Weasel by running the command

`python Weasel.py`

If you're a developer, you may start Weasel by opening an IDE (Sublime Text, VS Code, Visual Studio, etc.) and run the Weasel.py script.

# Start Weasel Command-Line Mode
Open a Terminal (MacOS and Linux) or a CMD (Windows), navigate to the downloaded Weasel folder

`cd <Weasel_folder_path>`

and start Weasel by running the command

`python Weasel.py -c -d "path/to/xml/dicom.xml" -s "path/to/analyis/script.py`

This alternative of Weasel is recommended if you're processing a large number of DICOM files at the same time or if you're running a time-consuming script.

# Generate the Executable

There is a Github Action Workflow in place that automatically builds the Weasel executable for Windows, MacOS and Linux and uploads the output files to a Weekly Release every Friday at midday.

If you wish to create your own bundle, you can compile the Python project into an executable of the operative system you're using by using the `pyinstaller` package.

First, you have to navigate to your Weasel folder

`cd <Weasel_folder_path>`

and run the following python command:

`python create_weasel_executable.py`

You may use your IDE instead of the terminal during this process. The generated executable can be found in the `Weasel` folder.

**For MacOS:** If the command above doesn't work, you might need to run `python3` instead and/or use `sudo` before the command. Eg. `sudo python3 create_weasel_executable.py`.

Any extra files you wish to add to your bundle, you can do so by writing the files/folders path in the `--collect-datas` and `--add-data` flags in the `create_weasel_executable.py` file.

## Other Info

Weasel runs the command `emf2sf` of [dcm4che](https://www.dcm4che.org/) on Enhanced/Multiframe DICOM. Elastix for Python can be used via ITK-Elastix.
