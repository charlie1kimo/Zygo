README.txt

This file is intended to document how this aligning module/package works.

========
INSTALL
========
1. Copy the ENTIRE "aligning" folder to any path you desire.
2. Start a command line window.
3. Navigate through command line to the path where you saved "aligning" module.
4. Start the program by command:
	$> python -m aligning.gui.newfocus8081_align [controller_1_name] [controller_2_name]

	i.e.:
		[controller_1_name] and [controller_2_name] are the hostnames for NewFocus Picomotor Controller.
		For the two controllers I tested. They are "8742-10514" & "8742-10516"
		The hostname convention is [model number]-[serial number] on a NewFocus Picomotor Controller.
		The argument order passed is IMPORTANT. 
		First controller should connect to "px1", "py", and "px2" motors
		Second controller should connect to "pz1" and "pz2" motors.

	example command to run:
		$> python -m aligning.gui.newfocus8081_align 8742-10514 8742-10516

5. Bring up the GUI and start using:
	Example Screenshot in "gui_ex.png"

===============
GUI Components
===============
Please refer to "gui_ex.png" for picture representation.

1. In the "Displays" section, it shows the both current cartesian coordinate positions and motor step positions.
2. In the "Change By" section, you can select either "SI units" or "motor steps" to change by, and the corresponding
   input field should be able to edit. Other input fields are greyed out.
3. In the "Change Values" section, you can enter the amounts you would like to change.
4. Press "Move" to perform the moves.
5. "Stop" to stop ANY movements.
6. "Save Position" saves current positions (in motor steps) so you can choose it later.
   I figure this would be useful for setting up reference coordinates. You can always go back to a saved (aligned)
   coordinates if you saved them.
7. "Select Positions" brings up a dialog box for you to choose what saved positions you would like to go to. Once
   a position selected, the move amounts are prefilled in the entry boxes. You can simply press "Move" to go to
   the saved positions.
8. "Zero All Changes" zeros all the amounts entered in the "Change Values" section.

=======================
Implementation Details
=======================
Currently I assumed there's a linear relationship between motor steps and cartesian distances. I've manually 
collected the data and perform regression analysis to figure out this linear correlation. You can find the 
collected data in "./Aligning_module_docs/8081_stage_measurements.xlsx"

However, the correlation is only an approximation for the mapping between motor steps and cartesian distances.
I found it really hard to reach a certain precision (because I was measuring by hands). It is recommended that
using "SI Units Moves" for large movement and then switch "motor steps Moves" for fine tuning in alignment process.

=====================================
Python Package / Modules Explanation
=====================================
(This section is for developer)

This package contains 1 sub-package -- "gui" and 2 other modules "picomotor" and "stage"
1. "picomotor":
	This is a low level picomotor controller module that utilizes the HTTP protocol to communicate to the 
	picomotor controller. By sending different control commands through HTTP protocol, this module can control
	/ move / read the motors attached to the controller.

2. "stage":
	This is a wrapper class for defining a NewFocus 8081 Stage Platform.
	It implements all the NewFocus 8081 Stage features definition defined in powerpoints under "./Alingn_module_docs/".
	For example, the class defines how to translate a x-coordinate movement to combinations of motor movements.
	Furthermore, this class also defines the measured correlations from "Implementation Details" Sections.

3. "gui":
	This is the sub-package containing wxPython GUI codes.
	ths only module is called "newfocus8081_align", which layouts the user interface and connects all the control to the UI.

