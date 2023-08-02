'''Info Header Start
Name : parse_par
Author : Wieland@AMB-ZEPH15
Version : 0
Build : 2
Savetimestamp : 2023-07-26T10:59:55.612727
Saveorigin : TauCetiV4.toe
Saveversion : 2022.32660
Info Header End'''

	  		
def bool_parse( parameter ):
	return int( null_parse(parameter))

def null_parse( parameter ):
	return parameter.eval()

parser = { 		"Toggle" : bool_parse,
	  		"Momentary" : bool_parse }
	
def parse( parameter ):
	return parser.get( parameter.style, null_parse )( parameter )
