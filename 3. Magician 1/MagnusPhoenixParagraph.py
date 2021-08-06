from MagnusBurd import *
"""
Todo List:
xParagraph Interaction Objects
xParagraph continuation nodes
-Interaction parsing static data storage node (paragraph count, breif paragraph structure, title, length, format, quotes and aligning citations, thesis, writing type, etc)
-Interaction dependent node processing of data to be fed to paragraph continuation nodes
-Paragraph summariser
-Iterative Nucleic responses until all parsing is found.
"""
class ParagraphObject(InteractionObject):
	def __init__(self,text="",*details):
		"""The base interaction object"""
		self.text=text
		self.details=colapseMap(details)
	def __eq__(self,other):
		"""method for comparison for interaction objects"""
		if self.text==other.text and self.details==other.details:
			return(True)
		return(False)
	def __repr__(self):
		return(f"[{identifier(self)} (len {len(self.text)}) at {hex(id(self))}]")
	def __list__(self):
		return([self.text,*self.details])
	def toString(self):
		"""Returns a string of the interaction"""
		details="\n".join(self.details)
		if details!="":
			details=f"Information:\n{details}"
		return(f"=Paragraph=\n{details}\n\nText:\n{self.text}".strip())
	@classmethod
	def fromList(cls,List):
		"""Turns an apropriate list to an interaction"""
		return(cls(*List))

class ParagraphContinuationNode(BaseResponseNode):
	def __init__(self,basis,*args,**kwargs):
		super().__init__(*args,**kwargs)
		self.basis=basis

	def add(self,interaction,nucleus):
		self.interactions.append(interaction)

	def pProcess(self,interaction,nucleus,previousPickups):
		return(["This is a paragraph describer\n\n"+"\n\n###\n\n".join(map(lambda x:x.toString(),self.basis))+f"\n\n###\n\n{interaction.toString()}"])

	def process(self,*args,**kwargs):
		return(self.pProcess(*args,**kwargs))

	def unprocess(self,interaction,nucleus):
		if interaction in self.interactions:
			self.interactions.remove(interaction)
		else:
			self.interactions=self.interactions[:-1]
	
	def postprocess(self,newinteraction,nucleus):
		self.add(newinteraction,nucleus)

	def save(self):
		return([interaction.__list__() for interaction in self.interactions])

	def toWriting(self,split="\n\n"):
		return(split.join([inter.text for inter in self.interactions]))

	@classmethod
	def load(cls,data,objectTo=InteractionObject):
		return(cls(*[objectTo.fromList(datapoint) for datapoint in data]))

if __name__=="__main__":
	basis=[ParagraphObject("While tardigrades may look mundane, they have quite the knack for survival. They are found nearly everywhere! With its ability to survive a volcano, the artic, and space, these small creatures are really hard to get rid of. Instead of having super tough skin, \"Tardigrades actually turn themselves into a type of glass by losing water\"(Kahn) says Daniel Kahn, a devoted microbiologist studying the process of dehydration that the creatures undergo. This is never unprompted though, there has to be an extreme condition to make them dehydrate. Even through this dehydration can easily be reanimated with some water!","Summary - This talks about how a tardigrade can survive in extremes because it can undergo, dehydration in extremes (such as the artic, a volcano, and space), there is mention of rehydration with water, and a quote from kahn, a microbiologist studying tardigrade dehydration.","Quotes - \"Tardigrades actually turn themselves into a type of glass by losing water\"(stated by daniel kahn)","Type - Body paragraph #1","Sentences - 6"),ParagraphObject("Bamboo is quite a scene setter. A little greenery can settle the backdrop and bamboo shoots always look well in a picture. First off, why is this? Besides its versatility, becoming anything from a pen to a piece of textile, bamboo can provide a beautiful view. The sun beams passing in-between the bamboo leaves and its texture account for some of the reasons scholars call bamboo the centerpiece of a Japanese background.","Summary - This talks on how bamboo is the centerpeice of a Japanese background. even though bamboo can be almost anything including a pen and textiles, bamboo provides a beautiful view by having sun beams pass through it and the texture of the bamboo itself.","Quotes - None","Type - Introduction paragraph","Sentences - 5")]
	paragraphNode=ParagraphContinuationNode(basis)
	paragraphDetails=[("Summary - This is a paragraph describing the background of the case of Carpenter v. United States. This paragraph has no bias. The background for the case was that on April 2011, 4 men convicted of a series of armed robberies (Including Carpenter) had their cellphone information obtained by the government. This information included the time of calls and the location of calls. With this, Timothy Carpenter was charged. Afterwards, Timothy Carpenter claimed that seizing cellular information witout a warent was in violation of the 4th amendment and ","Quotes - None","Type - Disclosing Paragraph","Sentences - 21")]
	nuk=Nucleus([paragraphNode],stop=[".\n","\n#","!\n","?\n"])
	for data in paragraphDetails:
		nuk.process(ParagraphObject("",*data))[0].text
	print(paragraphNode.toWriting())#in notepad, remove and fix later.