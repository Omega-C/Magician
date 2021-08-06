if(sessionStorage.getItem("bearer")===null) {
	window.location.replace(`/login?redirect=${window.location.pathname}`);
}
else{
	fetch("/api/tokenauthentication",{
		method:"POST",
		body:JSON.stringify({bearerToken:sessionStorage.getItem("bearer")})
	}).then(resp=>resp.json()).then(resp=>{
		if(resp.status!="OK"){
			sessionStorage.removeItem("bearer");
			window.location.replace(`/login?redirect=${window.location.pathname}`);
		}
	});
}
