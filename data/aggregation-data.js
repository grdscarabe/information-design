// Map payments to year and region
var mapPaymentsToYearAndRegion = function() {
	var mapSchemes = {
		"FR6": "Livestock",
		"FR5": "Crop", 
		"FR4": "Paiements prêts bonifiés (Feader)",
		"FR3": "European Agricultural Fund for Rural Development",
		"FR2": "Autres paiements du Feaga",
		"FR1": "Paiements directs aux agriculteurs au titre du Feaga"
	};
	for(var i=0 ; i<this.payments.length ; i++) {
		var p = this.payments[i];
		var sk = mapSchemes[p.globalSchemeId];
		output = {}
		if( sk !== undefined ) {
				output[sk] = p.amountEuro;
		} else {
				output["unknown"] = p.amountEuro;
		}
		emit({"region": this.geo1, "year": p.year}, output);
	}
};

// Map payments to year and department
var mapPaymentsToYearAndDepartment = function() {
	var mapSchemes = {
		"FR6": "Livestock",
		"FR5": "Crop", 
		"FR4": "Paiements prêts bonifiés (Feader)",
		"FR3": "European Agricultural Fund for Rural Development",
		"FR2": "Autres paiements du Feaga",
		"FR1": "Paiements directs aux agriculteurs au titre du Feaga"
	};
	for(var i=0 ; i<this.payments.length ; i++) {
		var p = this.payments[i];
		var sk = mapSchemes[p.globalSchemeId];
		output = {}
		if( sk !== undefined ) {
				output[sk] = p.amountEuro;
		} else {
				output["unknown"] = p.amountEuro;
		}
		emit({"department": this.geo2, "year": p.year}, output);
	}
};

// Map payments to year and town
var mapPaymentsToYearAndTown = function() {
	var mapSchemes = {
		"FR6": "Livestock",
		"FR5": "Crop", 
		"FR4": "Paiements prêts bonifiés (Feader)",
		"FR3": "European Agricultural Fund for Rural Development",
		"FR2": "Autres paiements du Feaga",
		"FR1": "Paiements directs aux agriculteurs au titre du Feaga"
	};
	for(var i=0 ; i<this.payments.length ; i++) {
		var p = this.payments[i];
		var sk = mapSchemes[p.globalSchemeId];
		output = {}
		if( sk !== undefined ) {
				output[sk] = p.amountEuro;
		} else {
				output["unknown"] = p.amountEuro;
		}
		emit({"town": this.insee_code, "year": p.year}, output);
	}
};

// Reduce payments by summing them by scheme
var reducePaymentsByScheme = function(key, values) {
	var reduced = {
		"Crop": 0, "Livestock": 0, 
		"European Agricultural Fund for Rural Development": 0,
		"Paiements prêts bonifiés (Feader)": 0,
		"Autres paiements du Feaga": 0,
		"Paiements directs aux agriculteurs au titre du Feaga": 0,
	};
	values.forEach(function(p) {
		for(var scheme in p) {
			if(! isNaN(p[scheme]-0) && (p[scheme] != null)) {
				reduced[scheme] += p[scheme];
			}
		}
	});
	return reduced;
};

// finalize for the totalvalue
var finalizeSumAll = function (key, reducedVal) {
	var total = 0;
	for(var prop in reducedVal) {
		var v = reducedVal[prop];
		if(! isNaN(v) && (v != null)) {
			total += v;
		}
	}
	reducedVal["total"] = total;
	return reducedVal;
};

// Launch map and reduce !
db.recipients.mapReduce(
	mapPaymentsToYearAndRegion, reducePaymentsByScheme,
	{ out: "payments_per_region_year", query: {payments: {$exists: true}}, finalize: finalizeSumAll })
db.recipients.mapReduce(
	mapPaymentsToYearAndDepartment, reducePaymentsByScheme,
	{ out: "payments_per_department_year", query: {payments: {$exists: true}, geo2: {$exists: true}}, finalize: finalizeSumAll })
db.recipients.mapReduce(
	mapPaymentsToYearAndTown, reducePaymentsByScheme,
	{ out: "payments_per_town_year", query: {payments: {$exists: true}, insee_code: {$exists: true}}, finalize: finalizeSumAll })

