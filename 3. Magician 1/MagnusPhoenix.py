"""
The Magnus Phoenix chatbot module, the community built node based AGI
Created by S Rumbaugh
GPT-3 api provided by OpenAI
"""
"""
Implementation List:
label with annotations
Micro-Nuclei
Node Chains (Might function the same so do or don't implement)
More Extension modules such as for wikimedia pulling, search engine return, large text creation/comprehension, and image return.
"""
class _Im:
	"""A class for the imports required for module functionality"""
	import openai
	import os
	import datetime
	import warnings
	import dill as pickle
	openai.api_key=os.environ.get("OPENAI_API_KEY")
	if openai.api_key==None:
		raise(KeyError("No API key in \"OPENAI_API_KEY\" os environment variable"))
class M:
	"""A class for static methods that are not fundemental to the module"""
	def abreviate(text)->str:
		"""Abreviates text"""
		text=str(text)
		if " " in text.strip():
			return("".join(map(lambda x:x[0].upper(),text.split(" "))))
		return(text)
	def characterReplace(text:str,placeholder:str,replace:str)->str:
		"""Replaces text next to a placeholder"""
		return(text.replace(placeholder+replace,placeholder).replace(placeholder,""))
	def timezone()->str:
		"""Gets timezone"""
		return(M.abreviate(_Im.datetime.datetime.now(_Im.datetime.timezone(_Im.datetime.timedelta(0))).astimezone().tzinfo))
	def time()->str:
		"""Gets time in a well formated string"""
		return(M.characterReplace(_Im.datetime.datetime.today().strftime('X%I:%M:%S %p '),"X","0")+M.timezone())
	def date()->str:
		"""Gets date in a well formated string"""
		return(M.characterReplace(_Im.datetime.datetime.today().strftime('%b X%d, %Y'),"X","0"))
class Encryption:
	"""A class for basic encryption"""
	from hashlib import sha256
	from base64 import urlsafe_b64decode,urlsafe_b64encode
	from random import randint
	from cryptography import fernet
	class LengthException(Exception):pass
	class KeyError(Exception):pass
	def key():
		"""creates a randomised key"""
		return(Encryption.fernet.Fernet.generate_key())
	def makeKey(string):
		"""Turns a string or byteString into a key as long as it is below 32 characters"""
		if type(string)!=bytes:
			string=bytes(string,"utf8")
		if len(string)>32:
			raise(Encryption.LengthException("Length too long"))
		string+=bytes("\u0000"*(32-len(string)),"utf8")
		return(Encryption.urlsafe_b64encode(string))
	def encrypt(byteString,key):
		"""Encrypts bytes with a key"""
		return(Encryption.urlsafe_b64decode(Encryption.fernet.Fernet(key).encrypt(byteString)))
	def decrypt(byteString,key):
		"""Decrypts bytes with a key"""
		try:
			return(Encryption.fernet.Fernet(key).decrypt(Encryption.urlsafe_b64encode(byteString)))
		except Encryption.fernet.InvalidToken:
			raise(Encryption.KeyError(f"Key \"{key}\" is invalid"))
	def salt():
		"""salt"""
		return("".join(map(lambda n:hex(n).split("x")[-1],[Encryption.randint(0,15) for _ in range(32)])))
	def hash(string):
		"""hashes with salt"""
		if type(string)!=bytes:
			string=string.encode("utf8")
		sal=Encryption.salt()
		return(Encryption.sha256(sal.encode()+string).hexdigest()+":"+sal)
	def confirmHash(has,string):
		"""Checks if a hash is a string"""
		if type(string)!=bytes:
			string=string.encode("utf8")
		hashNew,sal=has.split(":")
		return(Encryption.sha256(sal.encode()+string).hexdigest()==hashNew)
APICompletion=lambda prompt,**kwargs:_Im.openai.Completion.create(prompt=prompt,**kwargs).choices[0]["text"]
APISearch=lambda selector,documents,**kwargs: _Im.openai.Engine(kwargs["engine"]).search(documents=documents,query=selector,**kwargs)
colapse=lambda var:str({True:var,False:lambda:var}[callable(var)]())
colapseMap=lambda iterable:list(map(colapse,iterable))
identifier=lambda obj:((lambda:obj.__identifier__) if hasattr(obj,"__identifier__") else (lambda:obj.__class__.__name__))()
interactionDefaultParameters=[M.date,M.time]
MutableNodeDictionary={}
_LOGGER=lambda *args,**kwargs:None
Log=lambda argument,varname=None,maxlength=10:{False:lambda:_LOGGER((identifier(argument) if varname==None else varname)+f": {repr(argument)[:maxlength]}"),True:lambda:argument}[type(argument)==str]()
def toNode(dataKwargs,saved,className):
	"""Converts a name, saved data, and a class name to a node that has been registered in the Mutable Node Dictionary"""
	if className not in MutableNodeDictionary:
		newClass=MutableNodeDictionary["UnknownNode"].load(className,save)
		newClass.__dict__.update(dataKwargs)
		return(newClass)
	newClass=MutableNodeDictionary[className].load(saved)
	newClass.__dict__.update(dataKwargs)
	return(newClass)
def loadCellChanges(loadName,classRef):
	MutableNodeDictionary[loadName]=classRef
def _objectSaveAttributes(obj,attributes):
	return({attr:getattr(obj,attr) for attr in attributes})
class APICallError(Exception):
	"""class for API calling errors"""
class NodeError(Exception):
	"""Class for node related errors"""
	class NodeNotFound(Exception):
		"""Node is not found"""
	class TypeNotNode(Exception):
		"""Type used is not of type BaseNode"""
class InteractionObject:
	InteractionIdentifier=0
	def __init__(self,name,text="",identifier=None,*details,override=True):
		"""The base interaction object"""
		if identifier==None:
			self.id="0x{0:03x}".format(self.InteractionIdentifier)
			type(self).InteractionIdentifier+=1
		else:
			self.id=identifier
		self.name=name
		self.text=text
		if len(details)==0 and override:
			details=interactionDefaultParameters
		self.details=colapseMap(details)
	def __eq__(self,other):
		"""method for comparison for interaction objects"""
		if type(other)==type(self):
			if self.id==other.id:
				return(True)
			return(False)
		return(False)
	def __repr__(self):
		return(f"[{identifier(self)} (\"{self.name}\" len {len(self.text)}, Interaction ID {self.id}) at {hex(id(self))}]")
	def __list__(self):
		return([self.name,self.text,self.id,*self.details])
	def toString(self):
		"""Returns a string of the interaction"""
		details=" | ".join(self.details)
		if details!="":
			details=f" [{details}]"
		return(f"={self.name}{details}=\n{self.text}".strip())
	def copy(self):
		"""creates a copy"""
		return(self.fromList(list(self)))
	@classmethod
	def fromList(cls,List):
		"""Turns an apropriate list to an interaction"""
		return(cls(*List,override=False))
class BaseMeta(type):
	"""Base node meta class, logs new node classes to the MutableNodeDictionary"""
	def __new__(cls,name,bases,dct):
		obj=super().__new__(cls,name,bases,dct)
		MutableNodeDictionary[name]=obj
		obj.__identifier__=name
		return(obj)
class BaseNode(metaclass=BaseMeta):
	def __init__(self,_defaultHeader="#BaseNode#",header=None,headerWrap="{header}\n{content}\n\n"):
		"""The base object for a Node object"""
		self.name=identifier(self)
		self.header=(_defaultHeader if header==None else header)
		self.headerWrap=headerWrap
		self._attributes=("name","header","headerWrap")
	def __repr__(self):
		return(f"[Node \"{self.name}\" (Header \"{self.header}\") at {hex(id(self))}]")
	def init(self,nucleus):
		"""The initialisation function ran when passed to a Nucleus object"""
	def add(self,interaction,nucleus):
		"""The function to add an interaction"""
	def process(self,interaction,nucleus,previousPickups):
		"""The function that runs to generate upon creating the prompt, there must be a list return type"""
		return(["SampleText"])
	def processwrap(self,result):
		"""The wrapper function used in the nucleus to format the data from the class's process"""
		if result==None:
			return("")
		return(self.headerWrap.format(header=self.header,content=result))
	def postprocess(self,newinteraction,nucleus):
		"""What the node does with the resulting interaction object"""
	def unprocess(self,interaction,nucleus):
		"""The function that runs when a nucleus unprocesses an interaction"""
	def save(self):
		"""The function that tuns when a nucleus saves"""
		return()
	@classmethod
	def load(cls,data):
		"""The function that runs when a nucleus loads"""
		return(cls(*data))
class UnknownNode(BaseNode):
	def __init__(self,name,data,*args,**kwargs):
		"""a class used to store data that has been saved to a class unidentified.
		Add apropriate node name and corresponding class to MutableNodeDictionary and reload."""
		super().__init__(f"!==Unknown cell type \"{name}\" in Nucleus==!",*args,**kwargs)
		self.data=data
		self.name=name
		self.__identifier__=name
	def process(self,*args,**kwargs):
		"""Returns error message"""
		return([""])
	def save(self):
		"""Returns data that the unknown cell"""
		return(self.data)
	@classmethod
	def load(cls,name,data):
		"""takes in data from the unknown cell"""
		return(cls(name,data))
class BaseInteractionsNode(BaseNode):
	def __init__(self,_defaultHeader="#BaseInteractionsNode#",*interactions,args=tuple(),**kwargs):
		"""The base response node, returns no warnings as a baseNode"""
		kwargs.setdefault("headerWrap","{header}\n{content}")
		super().__init__(_defaultHeader,*args,**kwargs)
		self.interactions=list(interactions)
class OutputNode(BaseNode):
	def __init__(self,debug=False,*args,**kwargs):
		"""The default output node that would act the same as the previous nuclei core"""
		super().__init__("!OutputNode!",*args,**kwargs)
		self.debug=debug
	def process(self,nuclei,results,interaction,divider=""):
		#not the same process method, different outputs and inputs
		"""A node that processes the outputs of the previous nodes independently"""
		resultsString=divider.join(results)
		returnedtext=nuclei.APIPrompt(resultsString,stop=nuclei.stop)
		interaction.text+=returnedtext
		if self.debug:
			return(interaction,resultsString)
		return(interaction)
class NodeFrontalWrapper(metaclass=BaseMeta):
	def __new__(cls,node):
		"""Wrapps the node given"""
		if not isinstance(node,BaseNode):
			raise(NodeError.TypeNotNode(f"Object \"{node}\" not from type BaseNode"))
		for method in [met for met in dir(cls) if (not met.startswith("__")) and callable(getattr(cls,met)) and hasattr(node,met)]:
			if getattr(cls,method)!=getattr(node,method):
				cmeth=getattr(cls,method)
				nmeth=getattr(node,method)
				def WrappedMethod(self,*args,**kwargs):
					"""A method overridden by a wrapper class"""
					vargs,vkwargs=cmeth(self,*args,**kwargs)
					return(nmeth(self,*vargs,**vkwargs))
				setattr(node,method,WrappedMethod)
				node.__identifier__=cls.__name__
				node.save=cls.saveWrapper(node.save)
		return(node)
	def save():
		"""save data for the wrapper class"""
	@classmethod
	def saveWrapper(cls,prevSave):
		def save(self):
			return([cls.save(),prevSave()])
		return(save)
	@classmethod
	def load(cls,data):
		"""loads the wrapper class"""
class NodeVentralWrapper(metaclass=BaseMeta):
	def __new__(cls,node):
		"""Wrapps the node given"""
		if not isinstance(node,BaseNode):
			raise(NodeError.TypeNotNode(f"Object \"{node}\" not from type BaseNode"))
		for method in [met for met in dir(cls) if (not met.startswith("__")) and callable(getattr(cls,met)) and hasattr(node,met)]:
			if getattr(cls,method)!=getattr(node,method):
				cmeth=getattr(cls,method)
				nmeth=getattr(node,method)
				def WrappedMethod(self,*args,**kwargs):
					"""A method overridden by a wrapper class"""
					data=nmeth(self,*args,**kwargs)
					return(cmeth(self,data))
				setattr(node,method,WrappedMethod)
				node.__identifier__=cls.__name__
				node.save=cls.saveWrapper(node.save)
		return(node)
	def save():
		"""save data for the wrapper class"""
	@classmethod
	def saveWrapper(cls,prevSave):
		def save(self):
			return([cls.save(),prevSave()])
		return(save)
	@classmethod
	def load(cls,data):
		"""loads the wrapper class"""
class Nucleus:
	def __init__(self,Nodes,outputNodes=[OutputNode()],processinit=True,addNodeOrder=None,nodeUndoOrder=None,nodeOrder=None,postNodeOrder=None,stop=["\n=","\n#"],returnFunction=lambda *args,**kwargs:True,continuationKwargs=dict(engine="davinci",temperature=0.75,max_tokens=500,frequency_penalty=0.75,presence_penalty=0.75,top_p=1)):
		"""A Node processor that compiles the nodes to one central entity"""
		for node in Nodes:
			if not isinstance(node,BaseNode):
				raise(NodeError.TypeNotNode(f"Object \"{node}\" not from type BaseNode"))
		self.Nodes={name:value for name,value in map(lambda var:(var.name,var),Nodes)}
		self.outputNodes=outputNodes
		self.orderKey=[node.name for node in Nodes]
		self.nodeOrder=self.orderKey
		self.postNodeOrder=self.orderKey
		self.addNodeOrder=self.orderKey
		self.nodeUndoOrder=self.orderKey[::-1]
		self.returnFunction=returnFunction
		self.continuationKwargs=continuationKwargs
		self.stop=stop
		self._attributes=("nodeOrder","postNodeOrder","addNodeOrder","nodeUndoOrder","returnFunction","continuationKwargs","stop")
		if nodeOrder!=None:
			if "__iter__" in dir(nodeOrder):
				self.nodeOrder=nodeOrder
			else:
				raise(TypeError(f"Type \"{identifier(nodeOrder)}\" is not iterable"))
		if addNodeOrder!=None:
			if "__iter__" in dir(addNodeOrder):
				self.addNodeOrder=addNodeOrder
			else:
				raise(TypeError(f"Type \"{identifier(addNodeOrder)}\" is not iterable"))
		if nodeUndoOrder!=None:
			if "__iter__" in dir(nodeUndoOrder):
				self.nodeUndoOrder=nodeUndoOrder
			else:
				raise(TypeError(f"Type \"{identifier(nodeUndoOrder)}\" is not iterable"))
		if postNodeOrder!=None:
			if "__iter__" in dir(postNodeOrder):
				self.postNodeOrder=postNodeOrder
			else:
				raise(TypeError(f"Type \"{identifier(postNodeOrder)}\" is not iterable"))
		if not isinstance(self.Nodes[self.nodeOrder[-1]],BaseInteractionsNode):
			_Im.warnings.warn("Type not BaseResponseNode, results from continuation may not be in desired order.")
		for outputNode in self.outputNodes:
			if not isinstance(outputNode,OutputNode):
				raise(TypeError("Type not OutputNode in outputNodes, use node that is instance of OutputNode"))
		if processinit:
			for name in self.orderKey:
				self.Nodes[name].init(self)
	def __repr__(self):
		return(f"[Nucleus {{{', '.join(self.Nodes.keys())}}} at {hex(id(self))}]")
	def __getitem__(self,item):
		return(self.Nodes[item])
	def __call__(self,*args,**kwargs):
		return(self.process(*args,**kwargs))
	def APIPrompt(self,prompt,**kwargs):
		"""Prompts the ai to continue what is fed in"""
		for name in self.continuationKwargs:
			kwargs.setdefault(name,self.continuationKwargs[name])
		try:
			return(APICompletion(prompt,**kwargs).strip())
		except Exception as err:
			raise(APICallError(f"API Error: {str(err)}"))
	def add(self,interaction):
		"""adds an interaction to the nucleus"""
		for name in self.addNodeOrder:
			self.Nodes[name].add(interaction,self)
	def process(self,interaction,divider=""):
		"""The function processes an interaction"""
		if not isinstance(interaction,InteractionObject):
			raise(NodeError("Cannot use non interaction object as an interaction"))
		resultsKey={}
		pickups={}
		for name in self.orderKey:
			resultsKey[name],*pickups[name]=(lambda l:[self.Nodes[name].processwrap(l[0])]+l)(self.Nodes[name].process(interaction,self,pickups))
		results=[resultsKey[name] for name in self.nodeOrder]
		response=self.returnFunction(self,pickups)
		if type(response)!=bool:
			return(response)
		if response:
			returns=[]
			for node in self.outputNodes:
				result=node.process(self,results,interaction,divider=divider)
				if result!=None:
					returns.append(result)
			for name in self.postNodeOrder:
				self.Nodes[name].postprocess(interaction,self)
			if len(returns)==0:
				returns=None
			if len(returns)==1:
				returns=returns[0]
			return(returns,pickups)
		return(None)
	def unprocess(self,interaction):
		"""The function that unprocesses an interaction"""
		for name in self.nodeUndoOrder:
				self.Nodes[name].unprocess(interaction,self)
	def saveNodes(self,source):
		"""savesNodes"""
		return({obj.name:[_objectSaveAttributes(obj,obj._attributes),obj.save(),identifier(obj)] for obj in source})
	def save(self,filename=None):
		"""Saves the nucleus to a byte string, DO NOT ACCEPT UNKNOWN SOURCES"""
		data=[self.saveNodes([val for key,val in self.Nodes.items()]),self.saveNodes(self.outputNodes),_objectSaveAttributes(self,self._attributes)]
		fixedData=_Im.pickle.dumps(data,protocol=-1)
		if filename!=None:
			with open(filename,"wb") as file:
				file.write(fixedData)
		return(fixedData)
	def saveEncrypted(self,key,filename=None):
		"""Saves the pickle file to an encrypted file that can be unlocked by a user"""
		try:
			assert len(key)==44
			Encryption.urlsafe_b64decode(key)
		except:
			raise(TypeError("The key is not in a valid key format (byte type object 32 length of urlsafe base 64, use Encryption.key or Encryption.makeKey)"))
		fixedData=self.save()
		fixedData=Encryption.encrypt(fixedData,key)
		if filename!=None:
			with open(filename,"wb") as file:
				file.write(fixedData)
		return(fixedData)
	@classmethod
	def load(cls,dumpedData,file=False):
		"""Loads the byte string, DO NOT LOAD FROM UNTRUSTED SOURCES"""
		if file:
			with open(dumpedData,"rb") as fl:
				dumpedData=fl.read()
		loadedData=_Im.pickle.loads(dumpedData)
		nodes=[toNode(*nameData) for name,nameData in loadedData[0].items()]
		outputnodes=[toNode(*nameData) for name,nameData in loadedData[1].items()]
		newNucleus=cls(nodes,outputNodes=outputnodes,processinit=False,**loadedData[2])
		return(newNucleus)
	@classmethod
	def loadEncrypted(cls,dumpedData,key,file=False):
		"""Loads the pickle file from an encrypted file that can be unlocked by a user"""
		try:
			assert len(key)==44
			Encryption.urlsafe_b64decode(key)
		except:
			raise(TypeError("The key is not in a valid key format (byte type object 32 length of urlsafe base 64, use Encryption.key or Encryption.makeKey)"))
		if file:
			with open(dumpedData,"rb") as fl:
				dumpedData=fl.read()
		dumpedData=Encryption.decrypt(dumpedData,key)
		return(cls.load(dumpedData))