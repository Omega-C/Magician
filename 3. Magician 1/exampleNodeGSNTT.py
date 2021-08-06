from MagnusBurd import *

#create genric cell class? Could be used in other applications like memories

class Cell():#make cell metaclass to append to a list LATER
    pass

class GoalCell:#no inheritance for now
    def __init__(self,keyWord,mentionString="ask about {}",mentionConstant=1,rewritable=True,process=True,*args,**kwargs):
        """A keyword searching structure designed for use in the GoalNode as a means of getting a goal"""
        super().__init__(*args,**kwargs)
        self.processString=""""""
        self.processKwargs={}
        self.keyWord=keyWord
        self.mentionString
        self.mentionConstant=mentionConstant#have function as a scale from 0 to 2 where 0 is never, 1 is until completed, and 2 is always. Above 2 will raise error
        self.rewritable=rewritable
        self.process=process#make this the top boolean for the processing aspect. Have some exterior processing function maybe even. No, that uis not needed and can be made in a variant if anything 
    
    def processSource(self,sourceText):
        pass