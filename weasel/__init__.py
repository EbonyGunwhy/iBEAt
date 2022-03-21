"""

`weasel` is a Python environment for prototyping and deploying 
quantitative medical imaging applications. 

# How to use `weasel`?

Standard versions of `weasel` are distributed as [source code](here) 
or [executables](here). These are mainly provided to demonstrated the 
basic features and functionality. 

The intended use of `weasel` is for developers of new methods 
to create customized project-specific versions, 
and then destribute those custom versions in source code or as 
executables to enable indepent analysis and reproduction of the results.

## Visualing and analysing images

If you are using `weasel` to visualise or analyse medical images, 
you can download the demo version [here](insert link). 
The demo version has basic features for visualising 
DICOM images and performing basic image processing and segmentation tasks. 

If you need to perform a specific analysis for a specific project, 
you should request an executable `weasel` version from the 
developer of the project.

## Customizing `weasel`: menus and apps

To run `weasel` in a script, import the package, 
launch a new application and show it to the user:

```ruby
import weasel

wsl = weasel.app()      # launch an application
wsl.show()              # show the application
```

This will launch the demo version of `weasel`. 

The easiest way to customize `weasel` is by replacing the menubar 
at the top of the display with a custom made one. To illustrate this how this works, 
the `weasel` distribution includes a tutorial that 
comes with a few customized menubars. One of these is the Hello World menu. 
To run it (or any other menu), just set a new menu before showing `weasel` to the 
user:

```ruby
import weasel
from weasel.tutorial.menu import hello_world

wsl = weasel.app()          # launch an application
wsl.set_menu(hello_world)   # set a custom menu
wsl.show()                  # show the application
```

Of course in practice you will be running your own menus, which you 
are developing and testing in a separate folder outside the `weasel` 
distribution:

```ruby
import weasel
import mystuff

wsl = weasel.app()                  # launch an application
wsl.set_menu(mystuff.mymenu)        # set a custom menu
wsl.show()                          # show the application
```

In some cases the default displays are not sufficient for your purposes 
and so you may also want to change the way the graphical 
interface works. In that case you need to replace the default `weasel' 
application, a viewer for DICOM databases, and run your own. To see how this 
works, the tutorial package provides a viewer for multi-dimensional 
numpy arrays:

```ruby
import weasel
from weasel.tutorial.apps import numpyseries

wsl = weasel.app()           # launch an application
wsl.set_app(numpyseries)     # set a custom app
wsl.show()                   # show the application
```

When launched in this way a window will pop up allowing the 
user the select a dataset from disk. You can also set data programmatically.
Try this out by visualising and empty a 4-dimensional array:

```ruby
import numpy as np
import weasel
from weasel.tutorial.apps import numpyseries

wsl = weasel.app()           # launch an application
wsl.set_app(numpyseries)     # set a custom app
wsl.set_data(np.empty((10, 20, 5, 12)))
wsl.show()                   # show the application
array = wsl.get_data()
```

When calling `show()` the program halts until the user closes the 
window. Typically the user will have manipulated the array using the app. 
As shown in the example, the result can be retrieved with `get_data()`.

The tutorial contains a few other simple applications, 
but of course you may have written your own:

```ruby
import weasel
import mystuff

wsl = weasel.app()                # launch an application
wsl.set_app(mystuff.myapp)        # set a custom app
wsl.show()                        # show the application
```

See below for some examples of how apps can be defined.

## Writing custom `weasel` menus

A menu on the `weasel` menu bar is effectibely a list of menu buttons, 
or "actions" as they are called. Formally it is defined as a function 
which takes a parent menu or the menubar itself as argument. For 
instance, the Hello World menu inserted in the example above is defined as follows:

```ruby
def hello_world(parent):
    hello = parent.menu('Hello')
    hello.action(HelloWorld, text="Hello World")
```

As the example shows, a submenu of any parent menu can be created
by calling `parent.menu(label)`, where `label` is the text on the menu button. 

Then an action can be created in any menu by calling `parent.action()` where the 
first argument defines the action (see below) and the (optional) `text` argument defines the 
text that will be shown on the button.  

More complicated menus including submenus can be created in the same way. 
For instance the following adds a second `HelloWorld` action and 
a submenu which has two other `HelloWorld` actions:

```ruby
def hello_world_sub(parent):
    hello = parent.menu('Hello')
    hello.action(HelloWorld, text="Hello World")
    hello.action(HelloWorld, text="Hello World (again)")
    subMenu = hello.menu('Submenu')
    subMenu.action(HelloWorld, text="Hello World (And again)")
    subMenu.action(HelloWorld, text="Hello World (And again!)")
```

You can try running this to see how it looks:

```ruby
import weasel

wsl = weasel.app()              # launch an application
wsl.set_menu(hello_world_sub)   # set a custom menu
wsl.show()                      # show the application
```

## Writing `weasel` actions

`HelloWorld` as used above is an example of an action. When the user clicks on it,
a window pops up carrying a title 'My first action!' and saying "Hello World!". 
The program is paused until the user closes the pop-up. 
The `HelloWorld` action is defied as follows:

```ruby
from weasel.core import Action

class HelloWorld(Action):

    def run(self, app):
        app.dialog.information("Hello World!", title='My first action!')
```

As the example shows, all actions in `weasel` must be defined by 
subclassing the `Action` class from the `weasel.core` module. There are no 
other compulsory arguments, so the following creates a functional 
action which does absolutely nothing when clicked:

```ruby
from weasel.core import Action

class DoNothing(Action):
    pass
```

If the `run()` function is specified, it is executed when the user clickes the 
menu button corresponding to the action. Apart from `self`, `run()` has a compulsory argument 
`app` which gives access to other relevant functionality. In the case of `HelloWorld` this is 
the dialog class which has some options for launching pop-up windows. 

## Creating `weasel` executables

`weasel` applications mean nothing without a simple way of distributing them 
as an executable, which can be run without the need for other installations
by a simply mouse click. `weasel` has some built-in functionality for creating 
executables. As an example, imagine you have created the hello world script above:

```ruby
import weasel
import mystuff

wsl = weasel.app()                # launch an application
wsl.set_app(mystuff.myapp)        # set a custom app
wsl.show()                        # show the application
```

In order to generate an executable, save the script in a separate file, 
for instance "myproject.py". You can generate an executable by calling 
the `build` function of `weasel`:

```ruby
import weasel
weasel.build('myproject')
```

This must be executed from the same folder as myproject.py - as a script 
or interactively. After completion you will find a single file `weasel.exe` 
which you can distribute to the users if your applications. They will not 
need to install anything else - just double-click and run. 

If your project contains dependencies on other external packages, then 
these must be detailed in a text file "requirements.txt" as is customary for 
Python projects. The build function will install these along with 
`weasel`'s own dependencies. The requirements.txt file must be located 
in the same folder as pyproject.py.

If your project contains additional data such as images, icons or 
other types of files, the folders that contain these data must be provided
as an additional argument to `build()`, as a list of one or more paths:

```ruby
impor os
import weasel

weasel.build('myproject', 
    data_folders = ['myimages', os.path.join('mytables','parameters')],
    )
```

By default the build function generates a single .exe file. As `weasel` is a 
graphical interface application this will not launch a terminal when the .exe file 
is opened. These settings are most practical for external users but for debugging 
purposes the terminal and a multi-file build can be more convenient. These 
can be created by setting the `onefile` and `terminal` keywords to `False` and `True`, 
respectively:

```ruby
import weasel
weasel.build('myproject', 
    data_folders = ['myimages', os.path.join('mytables','parameters')],
    terminal = True, 
    onefile = False,
    )
```

(...) Support for hidden imports and collect data


## Creating `weasel` apps

The graphical user interface of `weasel` is built on PyQt's 
[QMainWindow](https://doc.qt.io/qt-5/qmainwindow.html#details), 
and always has a menu bar (top), a status bar (bottom), and a central widget. 
Applications may also use toolbars and dockwidgets if appropriate.

A `weasel` app is a class that manages the content of these different components, 
coordinates between them and holds the data currently managed by `weasel`. 
In addition any `weasel` app has access to some convenience classes, such as the 
dialog class and progress bar which provides a convenient programming
interface for common interactions with the user.

An example of a very simple (and not very useful!) `weasel` app is the 
`WeaselAbout` app which can be found in the `welcome` module of the default 
`weasel.apps`:

```ruby
from weasel.core import App
from weasel.wewidgets import ImageLabel
from weasel.actions.about import menu

class WeaselAbout(App):             # Required: subclass core.App
    def __init__(self, weasel):     # Required: initialize core.App                       
        super().__init__(weasel)    #    with instance of `Weasel`

        self.set_central(ImageLabel())          # set the central widget
        self.set_menu(menu)                     # set the menu
        self.set_status("Welcome to Weasel!")   # display message in status bar
```




# About `weasel`

`weasel` is a Python environment for prototyping and deploying 
quantitative medical imaging (qMRI) applications. 

Method development in qMRI is hampered by a gap between scientists 
who work with scripts or in command-line mode, 
and end-users who rely on graphical user interfaces. 
`weasel` aims to bridge that gap by providing an easy way 
to integrate pipeline scripts in an existing graphical interface 
environment that interfaces with DICOM databases 
and can be passed on to clinical users. 

The aim is to enable a rapid feedback loop between development 
and application under real-world conditions, 
and streamline the deployment of novel methods into clinical trials. 

## Background

Efficient, integrated product development involves an iterative 
process of building prototypes to test the basic ideas under 
real-world conditions as early as possible in the product development lifecycle, 
subsequently revising the concepts and ideas on the basis of 
this experience, and producing improved prototypes that can 
be tested under the same conditions again. This creates a 
rapid feedback loop between development and application that 
allows to intercept design flaws at an early stage and avoids 
expensive and late-stage failures of novel concepts. 

Applied sciences such as quantitative MRI can benefit from 
an integrated product development approach, as a way of 
steering the basic research and method development in the 
direction most likely to produce functional real-world 
applications. In practice this is often difficult due to 
the significant overhead required in moving from a set of 
command-line tools operating on computantionally convenient 
image dataformats (nifty, numpy), to a tool that can be applied 
by clinical end users on clinical (DICOM) data in a clinical 
environment. 

Highly successful open source software tools such 
as 3D Slicer or MITK are going a long way towards bridging this 
gap, but integrating simple scripts with novel image processing 
pipelines into these environments still presents a daunting task 
to basic scientists without the necessary computer science background.

`weasel` aims to reduce the gap between development and 
application of novel qMRI methods by significantly reducing the 
overhead required to integrate novel pipelines into a software 
environment suitable for clinical users working on clinical data. 
It is envisioned that this will speed up the translation of new 
methods into clinical research, and increase the value of clinical 
research by facilitating the integration of novel imaging biomarkers 
as secondary endpoints.

## Description

`weasel` is freely available via www.weasel.pro, is designed for 
open science and therefore entirely written in Python 3 and 
released under an open Apache 2.0 license. 

Since clinical data always ultimately arrive to the developer 
and the clinical end user alike in the form of DICOM images, 
`weasel` includes a DICOM read/write programming interface. 
The idea of this interface is to hide the complexity and inaccessible 
bureaucracy of the DICOM format from the scientist writing in Python, 
instead providing DICOM read and write access using more intuitive 
concepts such as folder structures, array slicing operations and 
class attributes. This allows the developer to prototype their new 
methods straight into DICOM, entirely removing a feared barrier to 
deployment of novel image processing pipelines in clinical studies: 
the need to convert pipelines interfacing with scientific data formats 
into pipelines interfacing with DICOM. 

The second important barrier to clinical translation is the need to 
interface command-line scripts with graphical user interfaces 
allowing user intervention such as drawing or editing regions 
of interest, or performing visual quality control of medical images. 
Graphical interfaces follow an event-drive logic that is often 
unfamiliar the basic scientist and involves a steep learning 
curve that is often prohibitive, resulting in prototypes that 
are difficult to access by clinical users and do not imitate 
the conditions under which these tools will ultimately be deployed. 

Weasel aims to address this challenge by providing a number 
of prepackaged graphical user interfaces with clear programming 
interfaces that enable the integration of user-defined image 
processing pipelines with a simple and intuitive commands similar 
to the print or display commands typically accessed in command-line. 
Using this approach, developers can easily configure Weasel by 
creating customized menus and compiling those to create 
applications that can be distributed to clinical collaborators 
as independent Weasel apps. 

An expanding library of graphical user 
interface elements (widgets) for setting and accessing DICOM objects 
is also available to support the development of customised GUIs.
Weasel deployment will be supported by well-documented code base and 
a series of user-friendly tutorials for clinical users.

## Applications of `weasel`

`weasel` development is jointly supported by the TRISTAN project 
funded by the Innovative Medicines Initiative (https://www.imi-tristan.eu/) 
and the UKRIN-MAPS project funded by the UK's Medical Research Council 
(https://www.nottingham.ac.uk/research/groups/spmic/research/uk-renal-imaging-network/ukrin-maps.aspx).

### TRISTAN

The TRISTAN project aims to develop imaging biomarkers for drug toxicity. 
Weasel is developed by the TRISTAN work package 2 on imaging 
biomarkers for drug toxicity, and will form the vehicle to 
distribute an imaging biomarker assay for predicting drug-drug 
interactions and liver toxicity. 

The food and drug administration 
(FDA) has accepted a biomarker qualification letter of intent 
describing the assay (https://www.fda.gov/media/149415/download) 
and evidence is currently being collected to support a full 
application for biomarker qualification. While a commercial 
assay will be taken forward by a collaborating company, Weasel 
will be offered as a free service along with supporting data 
and SOPs for those interested to replicate the assay locally. 

### UKRIN-MAPS and AFiRM

The UKRIN-MAPS project provides the technical underpinnings for 
a standardised multi-vendor approach to quantitative renal MRI. 
It is a collaborative UK-based project led by Nottingham 
University with support from 3 main MRI vendors. A set of 
standardised quantitative MRI protocols has been developed 
and is currently being validated in travelling volunteer studies. 
Basic analysis algorithms are available via an open access 
library (https://github.com/UKRIN-MAPS/ukat) and these are 
currently being wrapped up into Weasel for deployment into 
clinical trials. 

One clinical trial, the AFiRM study, will use 
these methods and has started recruiting in 2021. AFiRM will 
ultimately recruit 500 patients with Chronic Kidney Disease 
who will have 2 multi-parametric protocols 2- years apart. 
Analysis and QC of all data will be performed in Weasel and 
functional pipelines have already been tested on the first datasets. 

## Current `weasel` version

Weasel is currently at version 0.2 - a prototype version 
supporting all basic functionality that has however not been
tried and tested under the defined context of use. 
First applications in 4 multi-centre renal and liver projects 
are currently under construction. Until these applications have 
progressed to their first endpoints, Weasel is considered and 
early prototype still subject to substantial change in the code 
base and documenting material. A Weasel version 0.3 with a revised 
programming interface and simplified code base will be released shortly.

"""

from weasel.main import *
from weasel.core import *