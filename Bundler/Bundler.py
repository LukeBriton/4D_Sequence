import logging
import os
from pathlib import Path

import slicer
from slicer.ScriptedLoadableModule import *


#
# Bundler
#

class Bundler(ScriptedLoadableModule):
    """Uses ScriptedLoadableModule base class, available at:
    https://github.com/Slicer/Slicer/blob/main/Base/Python/slicer/ScriptedLoadableModule.py
    """

    def __init__(self, parent):
        ScriptedLoadableModule.__init__(self, parent)
        self.parent.title = "Bundler"  # make this more human readable by adding spaces
        self.parent.categories = ["Sequences"]  # set categories (folders where the module shows up in the module selector)
        self.parent.dependencies = []  # add here list of module names that this module requires
        self.parent.contributors = ["Lu Haocheng (BNUAI)", "Gao Yanzipeng (BNUAI)", "Chen Jiankang (BNUAI)"]  # replace with "Firstname Lastname (Organization)"
        # update with short description of the module and a link to online module documentation
        self.parent.helpText = """
A scripted loadable module, which bundles 3D volumes into a 4D sequence
"""
        # replace with organization, grant and thanks
        self.parent.acknowledgementText = """
This file was originally developed by Lu Haocheng, BNUAI, Gao Yanzipeng, BNUAI,
and Chen Jiankang, BNUAI.
"""




#
# BundlerWidget
#

class BundlerWidget(ScriptedLoadableModuleWidget):
    """Uses ScriptedLoadableModuleWidget base class, available at:
    https://github.com/Slicer/Slicer/blob/main/Base/Python/slicer/ScriptedLoadableModule.py
    """

    def __init__(self, parent=None):
        """
        Called when the user opens the module the first time and the widget is initialized.
        """
        ScriptedLoadableModuleWidget.__init__(self, parent)
        self.logic = None

    def setup(self):
        """
        Called when the user opens the module the first time and the widget is initialized.
        """
        ScriptedLoadableModuleWidget.setup(self)

        # Load widget from .ui file (created by Qt Designer).
        # Additional widgets can be instantiated manually and added to self.layout.
        uiWidget = slicer.util.loadUI(self.resourcePath('UI/Bundler.ui'))
        self.layout.addWidget(uiWidget)
        self.ui = slicer.util.childWidgetVariables(uiWidget)

        # Initialize widgets
        self.ui.inputDirectory.directory = str(Path.home())
        self.ui.inputDirectory.setToolTip('Select Directory with volume files')
        self.ui.outputDirectory.directory = str(Path.home())
        self.ui.outputFileName.plainText = 'filename'

        # Set scene in MRML widgets. Make sure that in Qt designer the top-level qMRMLWidget's
        # "mrmlSceneChanged(vtkMRMLScene*)" signal in is connected to each MRML widget's.
        # "setMRMLScene(vtkMRMLScene*)" slot.
        uiWidget.setMRMLScene(slicer.mrmlScene)
    
        # Create logic class. Logic implements all computations that should be possible to run
        # in batch mode, without a graphical user interface.
        self.logic = BundlerLogic()

        # Connections
        self.ui.inputDirectory.connect('validInputChanged(bool)', self.onSelectInput)

        # Buttons
        self.ui.applyButton.connect('clicked(bool)', self.onApplyButton)

        self.onSelectInput()


    def cleanup(self):
        """
        Called when the application closes and the module widget is destroyed.
        """

    def enter(self):
        """
        Called each time the user opens this module.
        """

    def exit(self):
        """
        Called each time the user opens a different module.
        """


    def onApplyButton(self):
        """
        Run processing when user clicks "Apply" button.
        """
        self.logic.process(self.ui.inputDirectory.directory, self.ui.outputDirectory.directory, self.ui.outputFileName.plainText)


    def onSelectInput(self):
        # Ensure that the directory isn't null
        self.ui.applyButton.enabled = bool(self.ui.inputDirectory.directory)

#
# BundlerLogic
#

class BundlerLogic(ScriptedLoadableModuleLogic):
    """This class should implement all the actual
    computation done by your module.  The interface
    should be such that other python code can import
    this class and make use of the functionality without
    requiring an instance of the Widget.
    Uses ScriptedLoadableModuleLogic base class, available at:
    https://github.com/Slicer/Slicer/blob/main/Base/Python/slicer/ScriptedLoadableModule.py
    """

    def __init__(self):
        """
        Called when the logic class is instantiated. Can be used for initializing member variables.
        """
        ScriptedLoadableModuleLogic.__init__(self)


    def process(self, inputPath, outputPath, outputName):
        """
        Run the processing algorithm.
        Can be used without GUI widget.
        :param inputPath: directory holds the volumes
        :param outputPath: directory to hold the sequence file
        :param outputName: the name sequence saved as
        """

        if not inputPath or not outputPath:
            raise ValueError("Input or output path is invalid")

        import time
        startTime = time.time()
        logging.info('Processing started')

        # Define the path to the folder containing the input volumes
        # fileFolderPath = r"D:\Files\Temp\input\gt"
        fileFolderPath = inputPath
        
        # Load the input volumes into Slicer
        volumeNodes = []
        for fileName in os.listdir(fileFolderPath):
            filePath = os.path.join(fileFolderPath, fileName)
            volumeNode = slicer.util.loadVolume(filePath)
            volumeNodes.append(volumeNode)

        # Create a new sequence node in Slicer and add the loaded volumes to it
        sequenceNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLSequenceNode")
        for i, volumeNode in enumerate(volumeNodes):
            sequenceNode.SetDataNodeAtValue(volumeNode, str(i))

        # Save the sequence node as an nrrd file
        # nrrdFilePath = os.path.join(r"D:\Files\Temp", "out.seq.nrrd")
        # mrbFilePath = os.path.join(r"D:\Files\Temp", "out.mrb")
        nrrdFilePath = os.path.join(outputPath, outputName+".seq.nrrd")
        mrbFilePath = os.path.join(outputPath, outputName+".mrb")

        # Create the volume rendering for the sequence browser node
        vrLogic = slicer.modules.volumerendering.logic()
        sequenceBrowserNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLSequenceBrowserNode")
        sequenceBrowserNode.AddSynchronizedSequenceNode(sequenceNode)
        proxyVolumeNode = sequenceBrowserNode.GetProxyNode(sequenceNode)
        vrLogic.CreateDefaultVolumeRenderingNodes(proxyVolumeNode)
        vrDisplayNode = slicer.mrmlScene.GetFirstNodeByClass("vtkMRMLVolumeRenderingDisplayNode")
        volumePropertyNode = vrDisplayNode.GetVolumePropertyNode()
        volumePropertyNode.Copy(vrLogic.GetPresetByName('CT-Cardiac'))

        # Set the volume rendering node to synchronize with volume display node
        vrDisplayNode.SetFollowVolumeDisplayNode(True)
        vrDisplayNode.SetVisibility(True)

        # Remove the loaded volumes from Slicer
        for volumeNode in volumeNodes:
          slicer.mrmlScene.RemoveNode(volumeNode)

        # Set the output file path for the sequence browser node and start playback
        sequenceBrowserNode.SetSelectedItemNumber(0)
        # sequenceBrowserNode.SetRecordingFilePath(niftiFilePath)
        sequenceBrowserNode.SetPlaybackActive(True)
        slicer.util.saveNode(sequenceNode, nrrdFilePath)
        slicer.util.saveScene(mrbFilePath)

        stopTime = time.time()
        logging.info(f'Processing completed in {stopTime-startTime:.2f} seconds')

