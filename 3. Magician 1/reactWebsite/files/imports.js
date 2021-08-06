class Utilities {
	setURL(url) {
		window.location.replace(url)
	}
}

class API {
	fetch(path,body) {
		return(fetch(path,{
			method:"POST",
			headers:JSON.stringify({"Content-Type":"application/json","Accept":"application/json","Authorization":"Bearer "+sessionStorage.getItem("bearer")})
			body:body
		}).then(resp=>resp.json()));
	}
	tokenCreation() {
		return(this.fetch("/api/tokencreation").then(resp=>{
			if (resp.status=="Valid") {
				sessionStorage.setItem("bearer",resp.token);
				return(true);
			}
			return(false);
		}));
	}
}

class User {
	constructor(name,identification,magic=false,active=true,pfp="/images/default.jpeg") {//might not stay later, just a class for user information that would be ported to by the api
		this.name=name;
		this.id=identification;
		this.magic=magic;
		this.pfp=pfp;
		this.active=active;
		this.status="inactive"
		if (this.magic) {this.status="AIStatus"}
		if (this.active) {this.status="active"}
	}
	returnType() {
		if (Session.SelectedUser.id==this.id) {return("textSent")}
		if (this.magic) {return("textAI")}
		return("textUser")
	}
	verify() {}
	static load() {}
	static getById() {}
}

function metaAdd(property,content) {
	elem=document.createElement("meta");
	elem.property=property;
	elem.content=content;
	document.getElementsByTagName("head")[0].appendChild(elem);
}

function metaDefaults() {
	metaAdd("og:title","Magician AGI Technologies")
	metaAdd("og:type","website")
	metaAdd("og:url",window.location.hostname)
	metaAdd("og:image",window.location.origin+"/hatBack.png")
	metaAdd("og:description","Magician AGI Technologies, a company on the forefront of AI technologies. We're here to deliver the singularity to you on a silver platter.")
	metaAdd("theme-color","#320082")
	metaAdd("twitter:card","summary_large_image")
}

//main

metaDefaults()
