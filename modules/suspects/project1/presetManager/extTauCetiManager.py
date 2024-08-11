'''Info Header Start
Name : extTauCetiManager
Author : Wieland@AMB-ZEPH15
Saveorigin : TauCetiV4.toe
Saveversion : 2022.35320
Info Header End'''

TDFunctions = op.TDModules.mod.TDFunctions
import uuid
from extParStack import InvalidOperator

def snakeCaseToCamelcase( classObject ):
	import inspect
	from optparse import OptionParser
	for methodName, methodObject in inspect.getmembers(OptionParser, predicate=inspect.isfunction) :
		if methodName[0].isupper():
			setattr( 
				classObject, 
				"".join( word.capitalize() for word in methodName.split("_")),
				methodObject
			)


class PresetDoesNotExist(Exception):
	pass

class extTauCetiManager:

	def __init__(self, ownerComp):
		# The component to which this extension is attached
		self.ownerComp 		= ownerComp
		self.stack     		= self.ownerComp.op('stack')
		# self.tweener   		= self.ownerComp.op('olib_dependancy').Get_Component()
		self.tweener 		= self.ownerComp.op("remote_dependency").GetGlobalComponent()
		self.modeler 		= self.ownerComp.op('modeler')
		self.preview 		= self.ownerComp.op("previews")
		self.logger 		= self.ownerComp.op("logger")
		self.prefab 		= self.ownerComp.op("presetPrefab")
		self.Record_Preset	= self.Store_Preset
		self.PresetDoesNotExist = PresetDoesNotExist
		snakeCaseToCamelcase( self )

	@property
	def preset_folder(self):
		return self.ownerComp.op("repo_maker").Repo

	def Find_Presets(self, name="", tag=""):
		return_values = []
		for child in self.preset_folder.findChildren(depth = 1):
			if name and child.par.Name.eval() != name: continue
			if tag and child.par.Tag.eval() != name: continue
			return_values.append( child.name )
		return return_values

	def Export_Presets(self, path):
		self.preset_folder.save( path, createFolders = True )

	def Import_Presets(self, path):
		self.preset_folder.par.externaltox = path
		self.preset_folder.par.reinitnet.pulse()

	def store_prev(self, prefab):
		prefab.op("preview").par.top = self.ownerComp.op("preview")			
		prefab.op("preview").bypass = False
		prefab.op("preview").lock = False
		prefab.op("preview").bypass = not self.ownerComp.par.Storepreviews.eval()
		prefab.op("preview").lock = self.ownerComp.par.Storepreviews.eval()
		prefab.op("preview").par.top = ""

	def Get_Preset_Comp(self, id) :
		return self.preset_folder.op(id) or self.ownerComp.op("emptyPreset")

	def Get_Preset_Name(self, id):
		return self.Get_Preset_Comp(id).par.Name.eval()

	def Get_Preview(self, id):
		return self.Get_Preset_Comp(id).op("preview")

	def Store_Preset(self, name, tag = '', id = ""):
		
		#creating new id if no ID given.
		if self.ownerComp.par.Idmode.eval() == "Name":
			name = tdu.legalName( name )
			id = name
		
		preset_id = id or tdu.legalName( str( uuid.uuid4() ) )

		#checking for existing preset
		existing_preset 	= self.preset_folder.op( preset_id ) 
		if existing_preset:
			handle_override = self.ownerComp.par.Handleoverride.eval()
			if handle_override == "Request":
				if not ui.messageBox(
					"Override Preset",
					f"You are about to override the preset with the name {name} and id {preset_id}. Are you sure?",
					buttons = ["Cancel", "Ok"]
				): return
			if handle_override == "Exception":
				raise Exception(f"Preset {preset_id} {name} already exists!")
		#calling update or create, depending on if a preset already exists. 
		preset_comp 		= (self._update_preset if existing_preset else self._create_preset)(name, tag, preset_id)

		#storing the preview
		self.store_prev( preset_comp )
		
		#aranging the node
		TDFunctions.arrangeNode( preset_comp )

		#writing stack to preset-table
		self.modeler.List_To_Table( preset_comp.op("values"), 
									self.stack.Get_Stack_Dict_List() )
		return preset_id

	def _create_preset(self, name, tag, id):
		new_preset = self.preset_folder.copy( self.prefab, name = id)
		new_preset.par.Tag 	= tag or self.ownerComp.par.Tag.eval()
		new_preset.par.Name = name
		self.ownerComp.op("callbackManager").Do_Callback(	"onPresetRecord", 
															new_preset.par.Name.eval(), 
															new_preset.par.Tag.eval(), 
															new_preset.name)
		return new_preset

	def _update_preset(self, name, tag, id):
		preset_comp = self.preset_folder.op(id)
		self.ownerComp.op("callbackManager").Do_Callback(	"onPresetUpdate", 
															preset_comp.par.Name.eval(), 
															preset_comp.par.Tag.eval(), 
															preset_comp.name)
		return preset_comp

	def Remove_Preset(self, id ):
		try:
			self.preset_folder.op( id ).destroy()
		except :
			pass
	
	def Remove_All_Presets(self):
		for preset_comp in self.preset_folder.findChildren( depth = 1):
			preset_comp.destroy()

	def Preset_To_Stack(self, id):
		preset_comp = self.preset_folder.op( id )
		if not preset_comp: return
		self.stack.Clear_Stack()

		for target_dict in self.modeler.Table_To_List( preset_comp.op("values") ):
			try:
				self.stack.Add_Par( self.stack.Get_Parameter( target_dict["parOwner"], target_dict["parName"] ), 
								fade_type = target_dict["type"] )
			except AttributeError:
				continue

	def Recall_Preset(self, id, time, curve = "s", load_stack = False):
		preset_comp = self.preset_folder.op( id )

		if not preset_comp: 
			if self.ownerComp.par.Raiseexceptiononnopreset.eval(): raise self.PresetDoesNotExist()
			return False
		
		self.ownerComp.op("callbackManager").Do_Callback(
			"onPresetRecall", 
			preset_comp.par.Name.eval(), 
			preset_comp.par.Tag.eval(), 
			preset_comp.name
		)

		if load_stack: self.Preset_To_Stack( id )

		for target_dict in self.modeler.Table_To_List( preset_comp.op("values") ):
			try:
				parameter = self.stack.Get_Parameter( 	target_dict["parOwner"], 
														target_dict["parName"] )
			except InvalidOperator as e:
				invalidHandleMode = self.ownerComp.par.Handleinvalidoperator.eval()
				if invalidHandleMode == "Remove":
					preset_comp.op("values").deleteRow( target_dict["id"] )
				elif invalidHandleMode == "Raise Exception":
					raise e
				continue

			if parameter is None: 
				self.logger.Log(
					"Could not find Parameter stored in Preset", 
					id, 
					target_dict["parOwner"],
					target_dict["parName"]
				)
				continue
			self.tweener.CreateTween(	parameter, 
										target_dict["val"], 
										time, 
										type 	= target_dict["type"], 
										curve 	= curve, 
										id 		= preset_comp, 
										mode 	= target_dict["mode"], 
										expression = target_dict["expression"] )
		return True
	
	def Rename(self, id, new_name ):
		preset_comp = self.preset_folder.op( id )
		if not preset_comp: return
		preset_comp.par.Name = new_name
		return preset_comp


	def Import_V3_Presets(self, path = ""):
		filepath = path or ui.chooseFile( fileTypes = [".tox"] )
		if not filepath: return
		loaded_presets = op("/sys/quiet").loadTox( filepath )
		for old_preset in loaded_presets.findChildren(depth = 1, type = tableDAT ):
			name_parts = old_preset.name.split("_")
			tag = ""
			if len( name_parts ) > 1: tag = name_parts.pop(0)
			name = " ".join(name_parts)

			new_preset_id = self.Store_Preset( name, tag = tag )
	
			new_preset_comp = self.preset_folder.op( new_preset_id )
			new_preset_comp.op("values").copy( old_preset )
			for row in new_preset_comp.op("values").rows():			
				row[5].val = row[5].val.replace("../../", "../")
			self.Preset_To_Stack( new_preset_id )
			self.Recall_Preset( new_preset_id, 0 )
			self.Store_Preset( name, tag = tag, id = new_preset_id )

	@property
	def PresetParMenuObject(self):
		return tdu.TableMenu(
			self.ownerComp.op("id_to_name"), labelCol = "name"
		)