import re
from requests import get as GET
from wikipedia import page as PageContent
from MagnusBurd import *

class WikipediaLookupNode(BaseNode):
	def __init__(self,*args,**kwargs):
		super().__init__(*args,**kwargs)
		self.hexify=lambda x:"%"+str(hex(ord(x))).split("x")[-1].upper()
		self.pageIDAPI="https://en.wikipedia.org//w/api.php?action=query&format=json&list=search&srsearch={}&srwhat=text&srprop=timestamp"
		self.disambiguationAPI="https://en.wikipedia.org/w/api.php?action=query&format=json&prop=pageprops&pageids={}&ppprop=disambiguation"
		self.pageAPI="https://en.wikipedia.org/w/api.php?action=query&prop=info&pageids={}&inprop=url&format=json"
		self.remove=["External links","References","Notes","See also","Further reading"]
		#make a new set of prompts that would find what not to get and return none if that is.
		self.DefinePrompt="""Text: what is 2+6?
		Search: none
		###
		Text: What is the scientific name for an orangutan?
		Search: Orangutan:Orangutan Scientific Name
		###
		Text: Hello! So great to see you!
		Search: none
		###
		Text: I love Germany, what are some traditions they have there?
		Search: Germany:Traditions in Germany
		###
		Text: What is the liquid in the ocean?
		Search: none
		###
		Text: what is the price of Etherium?
		Search: none
		###
		Text: How do I make blood pudding?
		Search: Blood Pudding:How blood pudding is made
		###
		Text: what does derivation in Machine learning do?
		Search: Machine Learning:How Derivation is used
		###
		Text: what is the price of a share in Tesla?
		Search: none
		###
		Text: what presidents died in office?
		Search: Presidents:Died in Office
		###
		Text: {}
		Search:"""
		self.AnswerPrompt="""
		Answer the question using the text. Make sure it is very short but include as much as possible. If unsure, answer with "unsure".

		Text:
		{0}
		###
		Question:
		{1}
		###
		Response:"""
		self.DefineKwargs=dict(engine="curie",temperature=0.15,max_tokens=64,top_p=1,stop=["\n"])
		self.AnswerKwargs=dict(engine="curie-instruct-beta",temperature=0.7,max_tokens=300,top_p=1,frequency_penalty=0.15,presence_penalty=0.35,stop=["\n\n\n","###"])

	def urlEncode(self,text):
		keep="qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM1234567890 "
		return("".join([self.hexify(c) if c not in keep else c for c in re.sub(r"\s+"," ",text)]).replace(" ","+"))

	def disimbiguation(self,pageID):
		return("pageprops" in eval(GET(self.disambiguationAPI.format(pageID)).text)["query"]["pages"][pageID].keys())

	def getPageURL(self,pageID):
		return(eval(GET(self.pageAPI.format(pageID)).text)["query"]["pages"][pageID]["fullurl"])

	def getPages(self,query):
		ids=[c["pageid"] for c in eval(GET(self.pageIDAPI.format(self.urlEncode(query))).text)["query"]["search"]]
		return(ids,[self.getPageURL(str(i)) for i in ids if not self.disimbiguation(str(i))])

	def getBestFit(self,match,docs,*args,**kwargs):
		scoredDocs=[x["score"] for x in APISearch(match,docs,*args,**kwargs)["data"]]
		scores=dict(zip(scoredDocs,docs))
		highestMatch=scores[max(scoredDocs)]
		return(highestMatch,max(scoredDocs))

	def getPageContent(self,page):
		headerLambda=lambda x:f"[{page}] {x}"
		#page=page.split("/")[-1].replace(" ","_")
		content=PageContent(page+".").content
		headers=["Key Details (dates, names, definitions)"]+re.findall(r"\s*== (.*) ==\s*",content)
		headers=list(map(headerLambda,headers))
		splate=re.sub(r"\s*==.+==\s*","\n==\n",content)
		splate=list(map(lambda x:re.sub(r"(\s\s)\s+",r"\1",x.strip()),splate.split("\n==\n")))
		zippedDict=dict(zip(headers,splate))
		for header in self.remove:
			head=headerLambda(header)
			if head in zippedDict:
				zippedDict.pop(head)
		for key in list(zippedDict.keys()):
			if zippedDict[key]=="":
				zippedDict.pop(key)
		return(zippedDict)

	def getShortResponse(self,text,question):
		return(APICompletion(self.AnswerPrompt.format(text,question),**self.AnswerKwargs).strip())

	def process(self,interaction,nucleus,previousPickups):
		question=interaction.text
		processed=APICompletion(self.DefinePrompt.format(re.sub(r"\s+"," ",question)),**self.DefineKwargs).strip()
		print(processed)
		if processed=="none":
			return(["",None])
		ids,pages=self.getPages(processed)
		print(pages)
		pageNames=[p.split("/")[-1].replace("_"," ") for p in pages]
		if len(pageNames)==0:
			return(["",None])
		highestMatchPage,ran=self.getBestFit(processed,pageNames,engine="curie")
		if ran<0:
			return(["",None])
		print(highestMatchPage)
		content=self.getPageContent(highestMatchPage)
		bestSection,ran=self.getBestFit(processed,list(content),engine="curie")
		if ran<0:
			return(["",None])
		print(list(content))
		print("\n"+"-"*16+"\n")
		print(bestSection)
		print("\n"+"-"*16+"\n")
		paragraphs=content[bestSection].split("\n\n")
		print(paragraphs)
		print("\n"+"-"*16+"\n")
		if len(paragraphs)==1:
			bestParagraph=paragraphs[0]
		else:
			bestParagraph,ran=self.getBestFit(processed,paragraphs,engine="babbage")
			if ran<0:
				return(["",None])
		print(bestParagraph)
		print("\n"+"-"*16+"\n")
		answer=self.getShortResponse(bestParagraph,question)
		print(answer)
		return(answer)

if __name__=="__main__":
	WikipediaLookupNode().process(InteractionObject("h","most common baby names"),None,None)