from MagnusPhoenix import *

def pseudoNodeCreate(string):
	pass

def composeInteraction(string):
	return()

def NucleusConstructor(string,split=",",interactionName="interaction"):
	nodeStrings=[n.trim() for n in string.split(split)]

class MemoryNode(BaseNode):
	def __init__(self,*args,memoryLimit=5,memorySplit="\n",responseNodeName="ResponseNode",**kwargs):
		"""A Node derived from the MemoryHandler class from the previous module"""
		super().__init__("#Memory#",*args,**kwargs)
		self.memory={}
		self.memoryLimit=memoryLimit
		self.memorySplit=memorySplit
		self.responseNodeName=responseNodeName
		self.memoryCategoriseKwargs=dict(engine="babbage",temperature=0,max_tokens=25,top_p=1,stop=["\n"])
		self.memoryCategorisePrompt="""Text: i ate some steak for lunch.
		Topics: Steak, Lunch
		###
		Text: Why would anybody do that?
		Topics: none
		###
		Text: not an embodiment of death, but what does it mean to die?
		Topics: Die, Death
		###
		Text: I have a degree in physics, and an english minor.
		Topics: Degree, Minor, Physics, English
		###
		Text: {}
		Topics:"""

	def setMemory(self,topic,name,text,details,identifier):
		topic=topic.lower()
		phoInteraction=[text,[name,identifier]+details]
		if topic not in self.memory:
			self.memory[topic]=[]
		if phoInteraction not in self.memory[topic]:
			self.memory[topic].append(phoInteraction)

	def getTopic(self,topic):
		if topic in self.memory:
			return(self.memory[topic])
		return([])

	def topicSorter(self,topics,btext):
		"""sorts topics"""
		if len(topics)==0:
			return([])
		endTopics=[]
		limitCount=0
		#made by me in the first version
		lisTopics=list(map(lambda x:self.getTopic(x)[::-1],topics))#gets the stuff
		lisLenMax=max(list(map(lambda x:len(x),lisTopics)))#gets the max of the stuff
		lisTopics=list(map(lambda x:x+[None for _ in range(lisLenMax-len(x))],lisTopics))#adds stuff to make stuff fit the maximum
		lisTopics=[i for l in list(zip(*lisTopics)) for i in l]#zips and mish mashes
		lisTopics=[i for i in lisTopics if i!=None]#removes the sweet nothings
		for gottenTopic in lisTopics:
			if gottenTopic not in endTopics and limitCount<=self.memoryLimit and gottenTopic[0].replace(self.memorySplit,"") not in btext:
				endTopics.append(gottenTopic)
				limitCount+=1;
		return(endTopics)

	def processInteraction(self,interaction,save=True):
		"""Process interaction in a memory useable format"""
		text=interaction.text
		name=interaction.name
		details=interaction.details
		endTopics=[]
		while self.memorySplit*2 in text:
			text.replace(self.memorySplit*2,self.memorySplit)
		text=text.split(self.memorySplit)
		for segment in text:
			response=APICompletion(self.memoryCategorisePrompt.format(segment),**self.memoryCategoriseKwargs).strip().replace(" ","")
			if response not in ["","none"]:
				for topic in response.lower().split(","):
					if save:
						self.setMemory(topic,name,segment,details,interaction.id)
					endTopics.append(topic)
		return(endTopics)

	def process(self,interaction,nucleus,previousPickups):
		memoryProcessedTopics=self.processInteraction(interaction,save=False)
		topicsResponse=self.topicSorter(memoryProcessedTopics,previousPickups[self.responseNodeName][0])
		if len(topicsResponse)==0:
			return([None])
		toString=lambda resolved:"\"{0}\" ({1})".format(resolved[0]," | ".join(resolved[1]))
		returnString="\n".join(map(toString,topicsResponse))
		return([returnString])

	def init(self,nucleus):
		for interaction in nucleus.Nodes[self.responseNodeName].interactions:
			self.processInteraction(interaction)

	def add(self,interaction,nucleus):
		self.processInteraction(interaction)
	
	def postprocess(self,newinteraction,nucleus):
		self.processInteraction(newinteraction)

	def unprocess(self,interaction,nucleus):
		for topic in self.memory:
			for memorylist in self.memory[topic]:
				if memorylist[0] in interaction.text and [interaction.name,interaction.id]+interaction.details==memorylist[1]:
					self.memory[topic].remove(memorylist)
			if self.memory[topic]==[]:
				self.memory.pop()

	def save(self):
		return({"memory":self.memory,"limit":self.memoryLimit,"split":self.memorySplit,"respName":self.responseNodeName})

	@classmethod
	def load(cls,data):
		obj=cls(memoryLimit=data["limit"],memorySplit=data["split"],responseNodeName=data["respName"])
		obj.memory=data["memory"]
		return(obj)

class DescribingNode(BaseNode):
	def __init__(self,details,*args,kwdetails={},**kwargs):
		super().__init__("#Details#",*args,**kwargs)
		self.details=list(details)+[lambda:f"{colapse(k)}: {colapse(kw)}" for k,kw in kwdetails.items()]

	def process(self,interaction,nucleus,previousPickups):
		return(["\n".join(colapseMap(self.details))])

	def save(self):
		return(self.details)

	@classmethod
	def load(cls,data):
		return(cls(data))

class ResponseNode(BaseInteractionsNode):
	def __init__(self,*interactions,interactionLimit=5,**kwargs):
		super().__init__("#Conversation#",*interactions,**kwargs)
		self.interactionLimit=interactionLimit

	def add(self,interaction,nucleus):
		self.interactions.append(interaction)

	def process(self,interaction,nucleus,previousPickups):
		return(["\n".join([x.toString() for x in self.interactions[-self.interactionLimit:]+[interaction]])])

	def unprocess(self,interaction,nucleus):
		if interaction in self.interactions:
			self.interactions.remove(interaction)
		else:
			self.interactions=self.interactions[:-1]
	
	def postprocess(self,newinteraction,nucleus):
		self.add(newinteraction,nucleus)

	def save(self):
		return([interaction.__list__() for interaction in self.interactions])

	@classmethod
	def load(cls,data,objectTo=InteractionObject):
		return(cls(*[objectTo.fromList(datapoint) for datapoint in data]))

"""class SummaryMemoryNode(BaseNode):
	def __init__(self,*args,timesteps=5,**kwargs):
		super().__init__("#Previous Memory Summary#",*args,**kwargs)
		self.tempMem=[]
		self.time=1
		self.timesteps=timesteps
		self.format="{new}{summary}\nUse the information above to generate a new summary\n\n-"
		self.formatKwargs=dict(engine="babbage",temperature=0,max_tokens=25,top_p=1,stop=["\n"])
		self.sep="\n- "
		self.summary=""
		self.summaryCache=[]

	def summarize(self):
		pass

	def add(self,interaction,nucleus):
		self.tempMem.append(interaction)

	def process(self,interaction,nucleus,previousPickups):
		if time%self.timesteps!=0:
			self.time+=1
			return(f"{self.header}\n"+self.summary)
		self.time=1"""

class ContinuityNode(BaseNode):
	pass
	#have node based caches including time and extrenious node information. Have accessability questioner (fknowing what changes happened and what the AI can access)

class StaticInteractionsNode(BaseInteractionsNode):
	def __init__(self,*interactions,message=None,**kwargs):
		kwargs.setdefault("headerWrap","{header}\n{content}\n\n")
		super().__init__("#Example Conversation#",*interactions,**kwargs)
		self.message=message

	def addInteraction(self,interaction):
		self.interactions.append(interaction)

	def setInteractions(self,*interactions):
		self.interactions=interactions

	def process(self,interaction,nucleus,previousPickups):
		return([("" if self.message==None else f"{self.message}\n")+"\n".join([x.toString() for x in self.interactions])])

	def unprocess(self,interaction,nucleus):
		if interaction in self.interactions:
			self.interactions.remove(interaction)
		else:
			self.interactions=self.interactions[:-1]

	def save(self):
		return([interaction.__list__() for interaction in self.interactions])

	@classmethod
	def load(cls,data,objectTo=InteractionObject):
		return(cls(*[objectTo.fromList(datapoint) for datapoint in data]))