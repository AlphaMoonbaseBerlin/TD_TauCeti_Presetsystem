
'''Info Header Start
Name : extCuelist
Author : Wieland@AMB-ZEPH15
Saveorigin : TauCetiV4.toe
Saveversion : 2022.32660
Info Header End'''
class extCuelist:
	"""
	extCuelist description
	"""
	def __init__(self, ownerComp):
		# The component to which this extension is attached
		self.ownerComp = ownerComp
		#self.cue_table = self.ownerComp.op('cuelist')
		self.selected_cue = ''
		self.active_cue = ''
		self.update_states()
		if self.ownerComp.par.Manager.eval() is not None: self.Recall_Cue( self.active_cue, time = 0 )
	@property
	def cue_table(self):
		return self.Data
	
	@property
	def Data(self):
		return self.ownerComp.op("repo_maker").Repo
	
	def update_states(self):
		for row in self.cue_table.rows()[1:]:
			if row[1].val: self.selected_cue = row[0].val
			if row[2].val: self.active_cue   = row[0].val


	def get_engine(self):
		return self.ownerComp.par.Manager.eval()

	def Reordered(self, destination):
		
		next_index_cell = self.cue_table[destination +  1, "id"]
		prev_index_cell = self.cue_table[destination -  1, "id"]
		
		prev_index = 0 if prev_index_cell.val == "id" else float( prev_index_cell.val )
		next_index = float( prev_index ) + 2  if next_index_cell is None else float( next_index_cell.val )
		new_id = f"{(next_index + prev_index) / 2:.2f}"
		return new_id

	def Append_Cue(self, preset, time = 5):
		self.cue_table.appendRow( ["recalculate", "","", preset, time])

	def Record_Cue(self, preset, time = 5):
		self.Append_Cue( self.get_engine().Store_Preset( preset ))

	def Delete_Cue(self, id):
		self.cue_table.deleteRow( id )
		self.update_states()

	def id_to_rowindex(self, id):
		return self.cue_table[id, 0].row if self.cue_table[id, 0] else ''

	def Select_Cue(self, id):
		if (id == "id"): raise Exception( "id is an invalid CueID. Just use anything else except id, as a word. It destroys everything....")
		if self.cue_table[ str(id), 0] is None: return
		if self.cue_table[ self.selected_cue, "id"]: self.cue_table[ self.selected_cue, "selected"].val = self.cue_table[ self.selected_cue, 1].val.replace( "s", '')

		self.selected_cue = str(id)

		self.cue_table[self.selected_cue, "selected"].val += "s"
		return
	
	@property
	def loop(self):
		return self.ownerComp.par.Loop.eval()

	def Select_Next_Cue(self):
		next_row_index 	= self.id_to_rowindex( self.selected_cue ) + 1 or 1
		if self.loop: next_row_index %= self.cue_table.numRows
		#we have to make sure to never use row 0!
		next_cue 		= self.cue_table[ next_row_index or 1, "id"]
		if next_cue: self.Select_Cue( next_cue.val )
	

	def Recall_Cue(self, cue_id, time = None):
		row = self.cue_table.row( cue_id )
		if not row: return
		preset_id = row[3].val
		cue_time = time if time is not None else float( row[4])
		if preset_id: self.get_engine().Recall_Preset( preset_id, cue_time )

		if self.cue_table[ self.active_cue, "active"] : self.cue_table[ self.active_cue, "active"].val = ""
		self.active_cue = cue_id
		self.cue_table[ self.active_cue, "active"].val = "a"
		self.Select_Cue( cue_id )
		self.Select_Next_Cue()

		self.ownerComp.op("callbackManager").Do_Callback(
			"onGo",
			cue_id,
			self.selected_cue,
			preset_id,
			self.get_engine().Get_Preset_Name(preset_id),
			cue_time
		)
	
		eventId = self.ownerComp.op("event1").createEvent(
			attackTime = cue_time
		)
		self.ownerComp.op("recalled_cues").appendRow(
			[eventId, cue_id]
		)

	def _finalize_cue(self, eventId):
		cueIdCell = self.ownerComp.op("recalled_cues")[str(int(eventId)), 1]
		if cueIdCell is None: return
		cueId = cueIdCell.val
		self.ownerComp.op("recalled_cues").deleteRow( str(int(eventId)) )
		presetIdCell = self.Data[cueId, "preset" ]
		if presetIdCell is None: return
		presetId = presetIdCell.val
		presetName = self.get_engine().Get_Preset_Name(presetId)
		self.ownerComp.op("callbackManager").Do_Callback(
			"onDone",
			cueId,
			presetId,
			presetName
		)

	def Assign_Preset(self, id, preset):
		self.cue_table[ id, "preset"].val = preset

	def Go(self):
		self.Recall_Cue(self.selected_cue)
		#self.Select_Next_Cue()
		