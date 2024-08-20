

'''Info Header Start
Name : extCuelist
Author : Wieland@AMB-ZEPH15
Saveorigin : TauCetiV4.toe
Saveversion : 2022.35320
Info Header End'''
class extCuelist:
	"""
	extCuelist description
	"""
	def __init__(self, ownerComp):
		# The component to which this extension is attached
		self.ownerComp = ownerComp
		self.data = self.ownerComp.op("dictParser")
		#self.cue_table = self.ownerComp.op('cuelist')
		
		# if self.ownerComp.par.Manager.eval() is not None: self.Recall_Cue( "", time = 0 )
	
	@property
	def selected_cue(self):
		return self.ownerComp.par.Selectedcue.eval()
		
	@property
	def loop(self):
		return self.ownerComp.par.Loop.eval()

	def get_engine(self):
		return self.ownerComp.par.Manager.eval()



	def Reorder(self, sourceIndex, targetIndex):
		if sourceIndex > targetIndex:
			nextIndex = targetIndex
			prevIndex = targetIndex - 1
		else :
			nextIndex = targetIndex + 1
			prevIndex = targetIndex

		sourceItem = self.data.GetItem( 
			sourceIndex,
			rows = "id"
	    )
		nextItem = self.data.GetItem( 
			min( nextIndex , self.data.NumItems ),
			rows = "id"
	    )

		prevItem = self.data.GetItem( 
			max(1, prevIndex  ),
			rows = "id"
		)
		
		prev_index = float(prevItem["id"]) * bool(prevItem["_tableIndex"] != 1)
		next_index = float(nextItem["id"]) + 2* ( nextItem["_tableIndex"] >= self.data.NumItems )

		debug( nextItem["_tableIndex"], self.data.NumItems )
		new_id = f"{(next_index + prev_index) / 2:.2f}"

		self.data.UpdateItem(sourceIndex, {
			**self.data.GetItem(sourceIndex),
			"id" : new_id}
		)
		self._sort()
		
		return 

	def _sort(self):
		self.data.SortTable( key = lambda row: float(row[0]))
		self.Select_Next_Cue()

	def Append_Cue(self, preset, time = 5):
		self.data.AddItem({
			"id" : math.floor( float(self.data.GetItem(-1)["id"]))+1,
			"preset" : preset,
			"time" : time
		})
		self._sort()


	def Record_Cue(self, preset, time = 5):
		self.Append_Cue( 
			self.get_engine().Store_Preset( preset ), 
			time=time
		)

	def Delete_Cue(self, id):
		self.data.DeleteItem( id )
		self.Select_Next_Cue()
	
	def Select_Cue(self, id):
		self.ownerComp.par.Selectedcue.val = id
		return

	def Select_Next_Cue(self):
		nextCueIndex = self.ownerComp.par.Activecue.menuIndex + 1
		if self.loop: nextCueIndex %= len( self.ownerComp.par.Selectedcue.menuNames )
		self.Select_Cue( 
			self.ownerComp.par.Selectedcue.menuNames[ nextCueIndex ]
		)
	

	def Recall_Cue(self, cue_id, time = None):
		cueData = self.data.GetItem( cue_id )
		
		self.get_engine().Recall_Preset(cueData["preset"], time or cueData["time"])

		self.ownerComp.par.Activecue.val = cueData["id"]
		self.Select_Next_Cue()

		self.ownerComp.op("callbackManager").Do_Callback(
			"onGo",
			cue_id,
			self.selected_cue,
			cueData["preset"],
			self.get_engine().Get_Preset_Name(cueData["preset"]),
			cueData["time"]
		)
	
		eventId = self.ownerComp.op("event1").createEvent(
			attackTime = cueData["time"]
		)
		self.ownerComp.op("recalled_cues").appendRow(
			[eventId, cue_id]
		)

	def _finalize_cue(self, eventId):
		cueId = self.ownerComp.op("recalled_cues")[eventId, "cueId"].val
		cueData = self.data.GetItem(cueId)
		presetId = cueData["preset"]
		presetName = self.get_engine().Get_Preset_Name(presetId)

		self.ownerComp.op("callbackManager").Do_Callback(
			"onDone",
			cueId,
			presetId,
			presetName
		)

	def Update_Cue(self, id, dataset:dict):
		self.data.UpdateItem(id, {
			**self.data.GetItem(id),
			**dataset}
		)

	def Assign_Preset(self, id, preset):
		self.Update_Cue(id, {"preset" : preset})

	def Assign_Time(self, id, time):
		self.Update_Cue(id, {"time" : time})

	def Assign_Id(self, id, newId):
		self.Update_Cue(id, {"id" : newId})
		self.data.SortTable( key = lambda row: float(row[0]))
		self.Select_Next_Cue()

	def Go(self):
		self.Recall_Cue(self.selected_cue)
		
		