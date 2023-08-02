'''Info Header Start
Name : ParStack
Author : Wieland@AMB-ZEPH15
Version : 0
Build : 2
Savetimestamp : 2023-07-26T10:59:54.368480
Saveorigin : TauCetiV4.toe
Saveversion : 2022.32660
Info Header End'''

import parse_par

class ParStack:
	"""
	extParStack description
	"""
	def __init__(self, ownerComp):
		# The component to which this extension is attached
		self.ownerComp = ownerComp


		self.fadeable = ['Float', 'Int', 'XYZ', 'RGB', 'XY', 'RGBA', 'UV', 'UVW']
		self.fade_types = ["fade", "startsnap", "endsnap"]
		self.stack_table = self.ownerComp.op('stack_table')

		self.get_par = self.get_par_dict
		try:
			self.ownerComp.par['x']
		except:
			self.get_par = self.get_par_attr
	@property 
	def relation(self):
		return self.ownerComp.par.Pathrelation.eval()

	def get_par_attr(self, op_path, par_name):
		return getattr( self.get_op_from_path(op_path).par, par_name)
	
	def get_par_dict(self, op_path, par_name):
		return self.get_op_from_path(op_path).par[par_name]

	def get_path(self, operator):
	
		if self.relation == "Relative":
			return self.ownerComp.relativePath( operator )
		return operator.path

	def get_fade_type(self, par):
		if par.style in self.fadeable: return 'fade'
		return  'startsnap'

	def get_op_from_path(self, path):
		self.ownerComp.par.Oppath = path
		return self.ownerComp.par.Oppath.eval()

	def Get_Parameter(self, op_path, parameter_name):
		return self.get_par( op_path, parameter_name)
		
	def Add_Comp(self, comp, page_scope = "*"):
		custom_page_dict = { page.name : page for page in comp.customPages }
		matched_pages = tdu.match( page_scope, list( custom_page_dict.keys() ) )

		for page_key in matched_pages:
			for parameter in custom_page_dict[ page_key ]:
				self.Add_Par( parameter )

	
	def Add_Par(self, parameter, id_function = lambda parameter: f"{parameter.owner.path}_{parameter.name}", preload = False, fade_type = ""):
		id = id_function( parameter )
		if self.stack_table.row( id ): return

		path = self.get_path( parameter.owner )
		parameter_name = parameter.name
		preload = False
		fade_type = fade_type if fade_type else self.get_fade_type( parameter )
		self.stack_table.appendRow( 
			[ 	id,
			 	path,
			 	parameter_name,
				preload,
				fade_type ]
		)
	
	def Get_Stack_Element_Dict(self, index):
		row = self.stack_table.row( index )

		if not row: return None
		parameter = self.get_par( row[1].val, row[2].val)
		if parameter is None: return self.Remove_Row_From_Stack( index )
		return {
			"id"		: row[0].val,
			"type" 		: row[4].val,
			"preload" 	: row[3].val,
			"par" 		: parameter,
			"val" 		: parse_par.parse( parameter ) if (parameter.mode != ParMode.EXPRESSION) else 0,
			"parName" 	: parameter.name,
			"parOwner"	: row[1].val,
			"mode"		: parameter.mode.name,
			"expression": parameter.expr if (parameter.mode == ParMode.EXPRESSION) else None,
			"relation"	: self.relation,
		}
	def Refresh_Stack(self):
		temp_list = self.Get_Stack_Dict_List()
		self.Clear_Stack()
		for element in temp_list:
			if element["par"]: self.Add_Par( element["par"] )
		return

	def Get_Stack_Dict_List(self):
		return [ self.Get_Stack_Element_Dict(index) for index in range(1, self.stack_table.numRows)]

	def Remove_Row_From_Stack(self, index):
		self.stack_table.deleteRow( index )

	def Clear_Stack(self):
		self.stack_table.clear( keepFirstRow = True)
	
	def Change_Preload(self, index):
		self.stack_table[index, 3].val = not eval( self.stack_table[index, 3].val )

	def Change_Fadetype(self, index):
		fade_list = self.fade_types.copy()

		parameter = self.get_par( self.stack_table[index, 1].val, 
								  self.stack_table[index, 2].val)
		if not parameter.style in self.fadeable: fade_list.remove( "fade" )
		type_index = fade_list.index( self.stack_table[index, 4].val )
		type_index += 1
		type_index %= len( fade_list )
		self.stack_table[index, 4].val = fade_list[ type_index ] 