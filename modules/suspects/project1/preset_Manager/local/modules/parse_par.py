'''Info Header Start
Name : parse_par
Author : Wieland@AMB-ZEPH15
Version : 0
Build : 3
Savetimestamp : 2023-08-03T10:13:11.598178
Saveorigin : TauCetiV4.toe
Saveversion : 2022.32660
Info Header End'''

	  		
def bool_parse( parameter ):
	return int( null_parse(parameter))

def null_parse( parameter ):
	return parameter.eval()

def val_parse( parameter ):
	return parameter.val

parser = { 		"Toggle" : bool_parse,
	  		"Momentary" : bool_parse,
			"OP"		: val_parse,
			"COMP"		: val_parse,
			"TOP"		: val_parse,
			"DAT"		: val_parse,
			"CHOP"		: val_parse,
			"MAT"		: val_parse,
			"SOP"		: val_parse
			 }
	
def parse( parameter ):
	return parser.get( parameter.style, null_parse )( parameter )
