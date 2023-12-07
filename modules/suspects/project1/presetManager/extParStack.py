
'''Info Header Start
Name : extParStack
Author : Wieland@AMB-ZEPH15
Saveorigin : TauCetiV4.toe
Saveversion : 2022.32660
Info Header End'''

import ParUtils

class extParStack:
	"""
	extParStack description
	"""
	def __init__(self, ownerComp):
		# The component to which this extension is attached
		self.ownerComp = ownerComp


		self._fadeables = ['Float', 'Int', 'XYZ', 'RGB', 'XY', 'RGBA', 'UV', 'UVW']
		self._fadeTypes = ["fade", "startsnap", "endsnap"]
		self._stackTable = self.ownerComp.op('stack_table')

		self._getPar = self._get_Par_Dict
		try:
			self.ownerComp.par['x']
		except:
			self._getPar = self._get_Par_Attr
	@property 
	def _relation(self):
		return self.ownerComp.par.Pathrelation.eval()

	def _get_Par_Attr(self, op_path, par_name):
		return getattr( self._get_Op_From_Path(op_path).par, par_name)
	
	def _get_Par_Dict(self, op_path, par_name):
		return self._get_Op_From_Path(op_path).par[par_name]

	def _get_Path(self, operator):
	
		if self._relation == "Relative":
			return self.ownerComp.relativePath( operator )
		return operator.path

	def _get_Fade_Type(self, par):
		if par.style in self._fadeables: return 'fade'
		return  'startsnap'

	def _get_Op_From_Path(self, path):
		self.ownerComp.par.Oppath = path
		return self.ownerComp.par.Oppath.eval()

	def Get_Parameter(self, op_path, parameter_name):
		return self._getPar( op_path, parameter_name)
		
	def Add_Comp(self, comp, page_scope = "*"):
		custom_page_dict = { page.name : page for page in comp.customPages }
		matched_pages = tdu.match( page_scope, list( custom_page_dict.keys() ) )

		for page_key in matched_pages:
			for parameter in custom_page_dict[ page_key ]:
				self.AddPar( parameter )

	
	def Add_Par(self, parameter, id_function = lambda parameter: f"{parameter.owner.path}_{parameter.name}", preload = False, fade_type = ""):
		id = id_function( parameter )
		if self._stackTable.row( id ): return

		path = self._get_Path( parameter.owner )
		parameter_name = parameter.name
		preload = False
		fade_type = fade_type if fade_type else self._get_Fade_Type( parameter )
		self._stackTable.appendRow( 
			[ 	id,
			 	path,
			 	parameter_name,
				preload,
				fade_type ]
		)
	
	def Get_Stack_Element_Dict(self, index):
		row = self._stackTable.row( index )

		if not row: return None
		parameter = self._getPar( row[1].val, row[2].val)
		if parameter is None: return self.Remove_Row_From_Stack( index )
		return {
			"id"		: row[0].val,
			"type" 		: row[4].val,
			"preload" 	: row[3].val,
			"par" 		: parameter,
			"val" 		: ParUtils.parse( parameter ) if (parameter.mode != ParMode.EXPRESSION) else 0,
			"parName" 	: parameter.name,
			"parOwner"	: row[1].val,
			"mode"		: parameter.mode.name,
			"expression": parameter.expr if (parameter.mode == ParMode.EXPRESSION) else None,
			"relation"	: self._relation,
		}
	def Refresh_Stack(self):
		temp_list = self.GetStackDictList()
		self.Clear_Stack()
		for element in temp_list:
			if element["par"]: self.AddPar( element["par"] )
		return

	def Get_Stack_Dict_List(self):
		return [ self.GetStackElementDict(index) for index in range(1, self._stackTable.numRows)]

	def Remove_Row_From_Stack(self, index):
		self._stackTable.deleteRow( index )

	def Clear_Stack(self):
		self._stackTable.clear( keepFirstRow = True)
	
	def Change_Preload(self, index):
		self._stackTable[index, 3].val = not eval( self._stackTable[index, 3].val )

	def Change_Fadetype(self, index):
		fade_list = self._fadeTypes.copy()

		parameter = self._getPar( self._stackTable[index, 1].val, 
								  self._stackTable[index, 2].val)
		if not parameter.style in self._fadeables: fade_list.remove( "fade" )
		type_index = fade_list.index( self._stackTable[index, 4].val )
		type_index += 1
		type_index %= len( fade_list )
		self._stackTable[index, 4].val = fade_list[ type_index ] 