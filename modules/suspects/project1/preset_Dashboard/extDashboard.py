
'''Info Header Start
Name : extDashboard
Author : Wieland@AMB-ZEPH15
Saveorigin : TauCetiV4.toe
Saveversion : 2022.35320
Info Header End'''
import uuid

class extDashboard:

	def __init__(self, ownerComp):
		# The component to which this extension is attached
		self.ownerComp = ownerComp
		self.selected_cell = (-1, -1)
		self.selected_preset = ''
		self.engine = self.ownerComp.par.Manager.eval
		self.ownerComp.par.Selectedbank = self.bank_comp
	
	@property
	def Banks(self):
		return self.ownerComp.op("repo_maker").Repo

	@property
	def bankParDefinition(self):
		return tdu.ParMenu(
			[child for child in self.Banks.findChildren(depth = 1, type = COMP)],
			[child.name for child in self.Banks.findChildren(depth = 1, type = COMP)]
		)

	@property
	def bank_comp(self):
		return op(self.ownerComp.par.Selectedbank.eval()) or self.Banks.findChildren(depth=1)[0]

	@property
	def map_table(self):
		return self.bank_comp.op("data")
	
	def New_Bank(self):
		new_bank = self.Banks.copy( self.ownerComp.op("prefab_bank") )
		new_bank.op("data").par.cols = self.ownerComp.par.Defaultbanksize1.eval()
		new_bank.op("data").par.rows = self.ownerComp.par.Defaultbanksize2.eval()
		return new_bank

	def Get_Engine(self):
		return self.ownerComp.par.Manager.eval()
		
	def Recall_Preset( self, preset, time ):
		self.Get_Engine().Recall_Preset( preset, time)

	def Delete_Preset(self, preset):
		self.Get_Engine().Remove_Preset( preset )
		self.map_table.text = self.map_table.text.replace(preset, "")
	
	def Start_Map(self, row, col):
		self.selected_cell = (row, col)
		selector = self.ownerComp.op('selector')
		selector.par.display = True
		selector.par.Page = 0
		selector.par.Searchterm = ""

	def Do_Map(self, value):
		self.map_table[ self.selected_cell ].val = value
		self.ownerComp.op('selector').par.display = False
		return


	def Record(self, row, col):
		index = str( uuid.uuid1() ).split('-')[0]
		tag = self.ownerComp.par.Tag.eval()
		self.map_table[row, col].val = self.Get_Engine().Store_Preset( index, tag = tag, id = self.map_table[row, col].val)
		return

	def Start_Rename(self, preset, row, col):
		if not preset: return
		self.ownerComp.op("prompt_overlay").par.display = True
		self.selected_cell = (row, col)
		self.selected_preset = preset
	
	def Do_Rename(self, new_name):
		new_name = self.Get_Engine().Rename(self.selected_preset, new_name)
		self.ownerComp.op("prompt_overlay").par.display = False
	
	def Rename( self, preset_id, value):
		new_name = self.Get_Engine().Rename(preset_id, value)

	def check_bank(self):
		if self.ownerComp.par.Selectedbank.eval(): return
		repo = self.ownerComp.op("repository_comp").Get_Repository()
		children = repo.findChildren( depth = 1, type = COMP)
		if children: 
			self.ownerComp.par.Selectedbank = children[0]
			return
		self.ownerComp.par.Selectedbank = self.New_Bank().path
