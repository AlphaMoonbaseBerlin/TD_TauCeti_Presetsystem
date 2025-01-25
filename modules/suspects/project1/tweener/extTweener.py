


'''Info Header Start
Name : extTweener
Author : Wieland@AMB-ZEPH15
Saveorigin : TauCetiV4.toe
Saveversion : 2023.11880
Info Header End'''

import fade
import tween_value
import tweener_exceptions

from asyncio import sleep as asyncSleep

from typing import Callable, Union, Hashable, Dict, List, Literal
from argparse import Namespace
def _emptyCallback( value ):
	pass

_type = type

class extTweener:

	def __init__(self, ownerComp):
		# The component to which this extension is attached
		self.ownerComp 						= ownerComp
		self.Tweens:Dict[int, fade._tween] 	= {}

		self.Modules = Namespace(
			Exceptions 	= tweener_exceptions
		)
		self.Constructor = Namespace(
			Expression 	= tween_value.expressionValue,
			Static 		= tween_value.staticValue,
			FromPar		= tween_value.tweenValueFromParameter
		)
		self.callback 	= self.ownerComp.op('callbackManager')

	def getFadeId(self, parameter:Par):
		return hash(parameter)

	def FadeStep(self, step_in_ms = None):
		fadesCopy = self.Tweens.copy()
		for fade_id, tween_object in fadesCopy.items():
			tween_object.Step(step_in_ms)
			if tween_object.done: del self.Tweens[ fade_id ]
		

	def AbsoluteTweens(self, 
					list_of_tweens:List[fade._tween], 
					curve = "s", 
					time=1):
		for tween in list_of_tweens:
			self.AbsoluteTween(
				tween["par"],
				tween["end"],
				tween.get("time", time),
				curve 		= tween.get("curve", curve),
				delay 		= tween.get("delay", 0),
				callback	= tween.get( "callaback", _emptyCallback)
			)

	def RelativeTweens(self, 
					list_of_tweens : List[fade._tween], 
					curve = "s", 
					time=1):
		for tween in list_of_tweens:
			self.RelativeTween(
				tween["par"],
				tween["end"],
				tween.get("time", time),
				curve 		= tween.get("curve", curve),
				delay 		= tween.get("delay", 0),
				callback	= tween.get( "callaback", _emptyCallback)
			)
	
	def AbsoluteTween(self, 
				   parameter:Par, 
				   end:any, 
				   time:float, 
				   curve:Literal["Linear", "s"] = 's', 
				   delay:float = 0, 
				   callback: Callable = _emptyCallback):
		self.CreateTween(parameter, end, time, curve = curve, delay = delay, callback = callback)
		return

	def RelativeTween(self, 
				   parameter:Par, 
				   end:any, 
				   speed:float, 
				   curve:Literal["Linear", "s"] = 's', 
				   delay:float = 0, 
				   callback: Callable = _emptyCallback):
		difference = abs(end - parameter.eval())
		time = difference / speed
		self.CreateTween(parameter, end, time, curve = curve, delay = delay, callback = callback)
		return
	
	async def CreateTween_Async(self,parameter, 
					end		:float, 
					time	:float, 
					type	:str				= 'fade', 
					curve	:str				= 's', 
					mode	:Union[str, ParMode]= 'CONSTANT', 
					expression	:str			= None, 
					delay		:float			= 0.0,
					callback	:Callable		= _emptyCallback,
					id		:Hashable			= '',  ):
		tweenObject = self.CreateTween( parameter, end, time, type, curve, mode, expression, delay, callback, id)
		while not tweenObject.done:
			await asyncSleep(0)
		return tweenObject
		
	def CreateTween(self,parameter, 
					end		:float, 
					time	:float, 
					type	:str				= 'fade', 
					curve	:str				= 's', 
					mode	:Union[str, ParMode]= 'CONSTANT', 
					expression	:str			= None, 
					delay		:float			= 0.0,
					callback	:Callable		= _emptyCallback,
					id		:Hashable			= '',  ):
		if not isinstance( parameter, Par):
			raise self.Exceptions.TargetIsNotParameter(f"Invalid Parameterobject {parameter}")
		
		targetValue	:tween_value._tweenValue 	= tween_value.tweenValueFromArguments( parameter, mode, expression, end )
		startValue	:tween_value._tweenValue 	= tween_value.tweenValueFromParameter( parameter )

		fadeClass:fade.fade  	= getattr( fade, type, fade.startsnap )
		fadeObject 				= fadeClass( parameter, time, startValue, targetValue, interpolation = curve, id = id, _callback = callback) 
		fadeObject.Delay( delay )
		#self.Tweens[id or self.getFadeId( parameter )] = fadeObject
		self.Tweens[self.getFadeId( parameter )] = fadeObject
		fadeObject.Step( stepsize = 0 )
		return fadeObject
		

	def StopFade(self,par):
		del self.Tweens[self.getFadeId(par)]

	def StopAllFades(self):
		self.Tweens = {}

	def ClearFades(self):
		self.Tweens.clear()

	def PrintFades(self):
		print(self.Tweens)