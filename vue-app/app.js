import Vue from "vue"
import App from "./App.vue"

function init(){
	new Vue({
		el: "#app",
		components: { App },
		template: "<App/>"
	})
}

document.readyState === "loading" ? document.addEventListener("DOMContentLoaded", init) : init()