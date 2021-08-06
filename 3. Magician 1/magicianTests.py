from MagnusBurd import *

def _philosopherEx():
	memnode=MemoryNode()
	examplenode=StaticInteractionsNode(InteractionObject("Human","What does it mean to love somebody?",override=False),
		InteractionObject("AI","To love is to care for, to cherish and hold dear. There is no greater thing than love.",override=False),
		InteractionObject("Human","What are your thoughts on homosexual individuals?",override=False),
		InteractionObject("AI","Thats their choice and society shouldn't judge them on it. There have been multiple false studies and religious interpretations that have unfortunatly poised the public idea against these individuals. Its their choice and we know now that there aren't adverse side effects so we should let them do what they want.",override=False),
		InteractionObject("Human","Can you tell me what death is?",override=False),
		InteractionObject("AI","Death is the loss of life, the absence of the ability to be. It has been true through history that people don't want to die.",override=False),message="these aren't real conversations, just example responses.")
	respnode=ResponseNode(InteractionObject("Human","What is god?"))
	desc=DescribingNode(["This is an AI made to respond to philisophical questions."])
	nuk=Nucleus([respnode,examplenode,desc],nodeOrder=[desc.name,examplenode.name,respnode.name])
	nuk=Nucleus.load(nuk.save())
	print(nuk.process(InteractionObject("AI"))[0].toString())

def _fatherEx():
	dadName="Angus"
	question="how do I tie a tie?"
	userName="Mark"
	examplenode=StaticInteractionsNode(InteractionObject("Person","what are your views on transgendered individuals?",override=False),
		InteractionObject(dadName,"Well, I don't completly understand it, but I support it.",override=False),
		InteractionObject("Person","thoughts on acab?",override=False),
		InteractionObject(dadName,"I don't know much about that kind of stuff to be honest.",override=False),
		InteractionObject("Person","thoughts on socialism?",override=False),
		InteractionObject(dadName,"I really don't know. I'm not a political guy and I think obessing politics cause hate.",override=False),
		InteractionObject("Person","what do you think of people that are homophobic?",override=False),
		InteractionObject(dadName,"I don't like homophobia, its gross.",override=False),
		InteractionObject("Person","whats your philosophy?",override=False),
		InteractionObject(dadName,"My philosophy is acceptance and optimism. Just don't accept the intolerant and things will get better.",override=False),message=f"these are messages that might happen.")
	respnode=ResponseNode(InteractionObject(userName,question))
	desc=DescribingNode([f"{dadName} is a single, very accepting southern man with a deep voice.\n{dadName} is open to all ideologies beside hate based ones like nazism, racism, homophobia, etc in which he opposed them.\n{dadName} isn't political.\n{dadName} is christian but doesn't push it on people."])
	nuk=Nucleus([respnode,examplenode,desc],nodeOrder=[desc.name,examplenode.name,respnode.name])
	print(nuk.process(InteractionObject(dadName))[0].toString())

if __name__=="__main__":
	try:
		_philosopherEx()
	except Exception as e:
		print(str(e))