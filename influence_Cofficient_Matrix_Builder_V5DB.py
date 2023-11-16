from abaqusConstants import *
from abaqusGui import *
from kernelAccess import mdb, session
import os

thisPath = os.path.abspath(__file__)
thisDir = os.path.dirname(thisPath)


###########################################################################
# Class definition
###########################################################################

class Influence_Cofficient_Matrix_Builder_V5DB(AFXDataDialog):

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def __init__(self, form):

        # Construct the base class.
        #

        AFXDataDialog.__init__(self, form, 'Influence Coefficient Matrix Builder V5.0',
            self.OK|self.APPLY|self.CANCEL, DIALOG_ACTIONS_SEPARATOR)
            

        okBtn = self.getActionButton(self.ID_CLICKED_OK)
        okBtn.setText('OK')
            

        applyBtn = self.getActionButton(self.ID_CLICKED_APPLY)
        applyBtn.setText('Apply')
            
        frame = FXHorizontalFrame(self, 0, 0,0,0,0, 0,0,0,0)

        # Model combo
        # Since all forms will be canceled if the  model changes,
        # we do not need to register a query on the model.
        #
        self.RootComboBox_1 = AFXComboBox(p=frame, ncols=0, nvis=1, text='Model:', tgt=form.modelNameKw, sel=0)
        self.RootComboBox_1.setMaxVisible(10)

        names = mdb.models.keys()
        names.sort()
        for name in names:
            self.RootComboBox_1.appendItem(name)
        if not form.modelNameKw.getValue() in names:
            form.modelNameKw.setValue( names[0] )
        msgCount = 299
        form.modelNameKw.setTarget(self)
        form.modelNameKw.setSelector(AFXDataDialog.ID_LAST+msgCount)
        msgHandler = str(self.__class__).split('.')[-1] + '.onComboBox_1StepsChanged'
        exec('FXMAPFUNC(self, SEL_COMMAND, AFXDataDialog.ID_LAST+%d, %s)' % (msgCount, msgHandler) )

        # Steps combo
        #
        self.ComboBox_1 = AFXComboBox(p=frame, ncols=0, nvis=1, text='CurrentStep: ', tgt=form.currentStepNameKw, sel=0)
        self.ComboBox_1.setMaxVisible(10)

        self.form = form
        frame = FXHorizontalFrame(self, 0, 0,0,0,0, 0,0,0,0)

        # Model combo
        # Since all forms will be canceled if the  model changes,
        # we do not need to register a query on the model.
        #
        self.RootComboBox_2 = AFXComboBox(p=frame, ncols=0, nvis=1, text='Model:', tgt=form.modelName2Kw, sel=0)
        self.RootComboBox_2.setMaxVisible(10)

        names = mdb.models.keys()
        names.sort()
        for name in names:
            self.RootComboBox_2.appendItem(name)
        if not form.modelName2Kw.getValue() in names:
            form.modelName2Kw.setValue( names[0] )
        msgCount = 300
        form.modelName2Kw.setTarget(self)
        form.modelName2Kw.setSelector(AFXDataDialog.ID_LAST+msgCount)
        msgHandler = str(self.__class__).split('.')[-1] + '.onComboBox_2PartsChanged'
        exec('FXMAPFUNC(self, SEL_COMMAND, AFXDataDialog.ID_LAST+%d, %s)' % (msgCount, msgHandler) )

        # Parts combo
        #
        self.ComboBox_2 = AFXComboBox(p=frame, ncols=0, nvis=1, text='Part:', tgt=form.partNameKw, sel=0)
        self.ComboBox_2.setMaxVisible(10)

        self.form = form
        frame = FXHorizontalFrame(self, 0, 0,0,0,0, 0,0,0,0)

        # Model combo
        # Since all forms will be canceled if the  model changes,
        # we do not need to register a query on the model.
        #
        self.RootComboBox_3 = AFXComboBox(p=frame, ncols=0, nvis=1, text='Model:', tgt=form.modelName3Kw, sel=0)
        self.RootComboBox_3.setMaxVisible(10)

        names = mdb.models.keys()
        names.sort()
        for name in names:
            self.RootComboBox_3.appendItem(name)
        if not form.modelName3Kw.getValue() in names:
            form.modelName3Kw.setValue( names[0] )
        msgCount = 301
        form.modelName3Kw.setTarget(self)
        form.modelName3Kw.setSelector(AFXDataDialog.ID_LAST+msgCount)
        msgHandler = str(self.__class__).split('.')[-1] + '.onComboBox_3BoundaryconditionsChanged'
        exec('FXMAPFUNC(self, SEL_COMMAND, AFXDataDialog.ID_LAST+%d, %s)' % (msgCount, msgHandler) )

        # Boundaryconditions combo
        #
        self.ComboBox_3 = AFXComboBox(p=frame, ncols=0, nvis=1, text='Boundary condition:', tgt=form.boundaryNameKw, sel=0)
        self.ComboBox_3.setMaxVisible(10)

        self.form = form
        HFrame_1 = FXHorizontalFrame(p=self, opts=0, x=0, y=0, w=0, h=0,
            pl=0, pr=0, pt=0, pb=0)
        spinner = AFXSpinner(HFrame_1, 2, 'CPU Number : ', form.cpuNumKw, 0)
        spinner.setRange(1, 16)
        spinner.setIncrement(1)
        AFXTextField(p=HFrame_1, ncols=6, labelText='Load Magnitude : ', tgt=form.loadMagnitudeKw, sel=0)
        AFXTextField(p=self, ncols=30, labelText='Node Labels :', tgt=form.nodeInputKw, sel=0)
        FXCheckButton(p=self, text='Start Calculating', tgt=form.submitKw, sel=0)
        l = FXLabel(p=self, text='Influence Coefficient Matrix Builder V5.0    by ZF', opts=JUSTIFY_LEFT)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def show(self):

        AFXDataDialog.show(self)

        # Register a query on steps
        #
        self.currentModelName = getCurrentContext()['modelName']
        self.form.modelNameKw.setValue(self.currentModelName)
        mdb.models[self.currentModelName].steps.registerQuery(self.updateComboBox_1Steps)

        # Register a query on parts
        #
        self.currentModelName = getCurrentContext()['modelName']
        self.form.modelName2Kw.setValue(self.currentModelName)
        mdb.models[self.currentModelName].parts.registerQuery(self.updateComboBox_2Parts)

        # Register a query on boundaryConditions
        #
        self.currentModelName = getCurrentContext()['modelName']
        self.form.modelName3Kw.setValue(self.currentModelName)
        mdb.models[self.currentModelName].boundaryConditions.registerQuery(self.updateComboBox_3Boundaryconditions)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def hide(self):

        AFXDataDialog.hide(self)

        mdb.models[self.currentModelName].steps.unregisterQuery(self.updateComboBox_1Steps)

        mdb.models[self.currentModelName].parts.unregisterQuery(self.updateComboBox_2Parts)

        mdb.models[self.currentModelName].boundaryConditions.unregisterQuery(self.updateComboBox_3Boundaryconditions)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def onComboBox_1StepsChanged(self, sender, sel, ptr):

        self.updateComboBox_1Steps()
        return 1

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def updateComboBox_1Steps(self):

        modelName = self.form.modelNameKw.getValue()

        # Update the names in the Steps combo
        #
        self.ComboBox_1.clearItems()
        names = mdb.models[modelName].steps.keys()
        for name in names:
            self.ComboBox_1.appendItem(name)
        if names:
            if not self.form.currentStepNameKw.getValue() in names:
                self.form.currentStepNameKw.setValue( names[0] )
        else:
            self.form.currentStepNameKw.setValue('')

        self.resize( self.getDefaultWidth(), self.getDefaultHeight() )

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def onComboBox_2PartsChanged(self, sender, sel, ptr):

        self.updateComboBox_2Parts()
        return 1

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def updateComboBox_2Parts(self):

        modelName = self.form.modelName2Kw.getValue()

        # Update the names in the Parts combo
        #
        self.ComboBox_2.clearItems()
        names = mdb.models[modelName].parts.keys()
        names.sort()
        for name in names:
            self.ComboBox_2.appendItem(name)
        if names:
            if not self.form.partNameKw.getValue() in names:
                self.form.partNameKw.setValue( names[0] )
        else:
            self.form.partNameKw.setValue('')

        self.resize( self.getDefaultWidth(), self.getDefaultHeight() )

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def onComboBox_3BoundaryconditionsChanged(self, sender, sel, ptr):

        self.updateComboBox_3Boundaryconditions()
        return 1

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def updateComboBox_3Boundaryconditions(self):

        modelName = self.form.modelName3Kw.getValue()

        # Update the names in the Boundaryconditions combo
        #
        self.ComboBox_3.clearItems()
        names = mdb.models[modelName].boundaryConditions.keys()
        names.sort()
        for name in names:
            self.ComboBox_3.appendItem(name)
        if names:
            if not self.form.boundaryNameKw.getValue() in names:
                self.form.boundaryNameKw.setValue( names[0] )
        else:
            self.form.boundaryNameKw.setValue('')

        self.resize( self.getDefaultWidth(), self.getDefaultHeight() )

