from abaqusGui import *
from abaqusConstants import ALL
import osutils, os


###########################################################################
# Class definition
###########################################################################

class Influence_Cofficient_Matrix_Builder_V5_plugin(AFXForm):

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def __init__(self, owner):
        
        # Construct the base class.
        #
        AFXForm.__init__(self, owner)
        self.radioButtonGroups = {}

        self.cmd = AFXGuiCommand(mode=self, method='main_f',
            objectName='Displacement_Matrix_Builder_kernelV5', registerQuery=False)
        pickedDefault = ''
        self.modelNameKw = AFXStringKeyword(self.cmd, 'modelName', True)
        self.currentStepNameKw = AFXStringKeyword(self.cmd, 'currentStepName', True)
        self.modelName2Kw = AFXStringKeyword(self.cmd, 'modelName2', True)
        self.partNameKw = AFXStringKeyword(self.cmd, 'partName', True)
        self.modelName3Kw = AFXStringKeyword(self.cmd, 'modelName3', True)
        self.boundaryNameKw = AFXStringKeyword(self.cmd, 'boundaryName', True)
        self.cpuNumKw = AFXIntKeyword(self.cmd, 'cpuNum', True, 8)
        self.loadMagnitudeKw = AFXFloatKeyword(self.cmd, 'loadMagnitude', True, 0.05)
        self.nodeInputKw = AFXStringKeyword(self.cmd, 'nodeInput', True, '')
        self.submitKw = AFXBoolKeyword(self.cmd, 'submit', AFXBoolKeyword.TRUE_FALSE, True, True)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def getFirstDialog(self):

        import influence_Cofficient_Matrix_Builder_V5DB
        return influence_Cofficient_Matrix_Builder_V5DB.Influence_Cofficient_Matrix_Builder_V5DB(self)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def doCustomChecks(self):

        # Try to set the appropriate radio button on. If the user did
        # not specify any buttons to be on, do nothing.
        #
        for kw1,kw2,d in self.radioButtonGroups.values():
            try:
                value = d[ kw1.getValue() ]
                kw2.setValue(value)
            except:
                pass
        return True

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def okToCancel(self):

        # No need to close the dialog when a file operation (such
        # as New or Open) or model change is executed.
        #
        return False

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Register the plug-in
#
thisPath = os.path.abspath(__file__)
thisDir = os.path.dirname(thisPath)

toolset = getAFXApp().getAFXMainWindow().getPluginToolset()
toolset.registerGuiMenuButton(
    buttonText='Influence Cofficient Matrix Builder V5.0', 
    object=Influence_Cofficient_Matrix_Builder_V5_plugin(toolset),
    messageId=AFXMode.ID_ACTIVATE,
    icon=None,
    kernelInitString='import Displacement_Matrix_Builder_kernelV5',
    applicableModules=ALL,
    version='N/A',
    author='N/A',
    description='N/A',
    helpUrl='N/A'
)
