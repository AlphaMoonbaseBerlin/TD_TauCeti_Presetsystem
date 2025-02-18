"""Info Header Start
Name : extTauCetiManager
Author : Wieland@AMB-ZEPH15
Saveorigin : TauCetiV4.toe
Saveversion : 2023.11880
Info Header End"""
TDFunctions = op.TDModules.mod.TDFunctions
import uuid
from extParStack import InvalidOperator
from typing import Literal, Union

def snakeCaseToCamelcase(classObject):
    pass

class PresetDoesNotExist(Exception):
    pass

class extTauCetiManager:

    def __init__(self, ownerComp):
        self.ownerComp = ownerComp
        self.stack = self.ownerComp.op('stack')
        self.tweener = self.ownerComp.op('remote_dependency').GetGlobalComponent()
        self.modeler = self.ownerComp.op('modeler')
        self.preview = self.ownerComp.op('previews')
        self.logger = self.ownerComp.op('logger')
        self.prefab = self.ownerComp.op('presetPrefab')
        self.Record_Preset = self.Store_Preset
        self.PresetDoesNotExist = PresetDoesNotExist
        pass

    @property
    def preset_folder(self):
        pass

    def Find_Presets(self, name: str='', tag: str='') -> list[str]:
        """
			Returns a list IDs of presets given the defined parameters.
		"""
        pass

    def Export_Presets(self, path: str):
        """
			Save the preset as a TOX for the given path.
		"""
        pass

    def Import_Presets(self, path: str):
        """
			Load a TOX as the external presets.
		"""
        pass

    def store_prev(self, prefab):
        pass

    def Get_Preset_Comp(self, id) -> COMP:
        """
			Returns the COMP defining the presets given the ID.
		"""
        pass

    def Get_Preset_Name(self, id: str) -> str:
        """
			Return the Name of a Preset by ID.
		"""
        pass

    def Get_Preview(self, id: str) -> TOP:
        """
			Return the TOP showing the preview of the Presets.
		"""
        pass

    def Store_Preset(self, name: str, tag='', id='') -> str:
        """
			Store the Preset unter the given name. 
			If id is not not supplied the ID will be generated based on Parameters.
		"""
        pass

    def Remove_Preset(self, id: str):
        pass

    def Remove_All_Presets(self):
        pass

    def Preset_To_Stack(self, id: str):
        pass

    def Recall_Preset(self, id: str, time: float, curve='s', load_stack=False):
        pass

    def Rename(self, id: str, new_name: str):
        pass

    def Push_Stack_To_Presets(self, mode: Literal['keep', 'overwrite']='keep', _stackelements: Union[str, list, tuple]='*', _presets: Union[str, list, tuple]='*'):
        """
			Pushes all the parameters of the current stack to all presets.
			When using "overwrite" mode all parameters will b overwritten. CAUTION!
		"""
        pass

    def Import_V3_Presets(self, path=''):
        """
			Import the export of an older V3 TauCeti project.
		"""
        pass

    @property
    def PresetParMenuObject(self):
        pass