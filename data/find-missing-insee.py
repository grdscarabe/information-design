#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Handle cases where we were not able to retrieve the INSEE code.
"""

import pymongo
import csv
import jellyfish
import re

########################## INSEE DATA

insee_headers = ["Commune", "Codepos", "Departement", "INSEE"]

post2insee = {}
town2insee = {}

problematicPost = set()
problematicTown = set()

reg_cedex = re.compile("\s+cedex(\s+\d+)?", re.I)

with open("codepostal-codeinsee.csv", "r") as fh_insee:
	reader = csv.DictReader(fh_insee, delimiter=";", fieldnames=insee_headers)
	reader.next()
	for row in reader:
		# postcode to insee
		if not post2insee.has_key( row["Codepos"] ):
			post2insee[ row["Codepos"] ] = {}
		post2insee[ row["Codepos"] ][ row["Commune"] ] = row["INSEE"]
		# town to insee
		if not town2insee.has_key( row["Commune"] ):
			town2insee[ row["Commune"] ] = {}
		town2insee[ row["Commune"] ][ row["Codepos"] ] = row["INSEE"]

def get_insee(postcode, name, distmax=5):
	"""
	Convert a postcode to an insee code.
	If no exact match, choose best candidate but record it as problematic.
	"""
	global problematicTown
	global problematicPost
	
	# Handle cedex stuff
	if reg_cedex.search(name):
		name = reg_cedex.sub("", name)

	if not post2insee.has_key(postcode):
		# No match on postcode...
		problematicPost.add(postcode)
		return None
	elif post2insee[postcode].has_key(name.upper()):
		# Perfect match!
		return (name.upper(), post2insee[postcode][name.upper()])
	else:
		# No perfect match, look for best candidate
		best = None
		best_score = None
		for candidate in post2insee[postcode].keys():
			score = jellyfish.levenshtein_distance(name.upper(), candidate)
			if (best_score is None) or (score<best_score):
				best_score = score
				best = candidate
		problematicTown.add( name.upper() )
		if (not best is None) and (best_score<distmax):
			return (best, post2insee[postcode][best])
		else:
			return None

################### MATCHING

conn = pymongo.Connection()
coll = conn["pac"]["recipients"]

q = {"insee_code": {"$exists": False}, "postalcode": {"$exists": True}, "town": {"$exists": True}, "countryRecipient": "FR"}

ng = nb = 0

for obj in coll.find(q):
	found = False
	# Skip unresolvables
	if not (obj.has_key("postalcode") and obj.has_key("town")):
		break
	# Compute values
	name = obj["town"].upper()
	if reg_cedex.search(name):
		name = reg_cedex.sub("", name)
	postalcode = obj["postalcode"]
	# Look using postalcode
	code1 = obj["postalcode"]
	code2 = "%05d"%(10*(int(code1)/10))
	code3 = "%05d"%(100*(int(code1)/100))
	code4 = "%05d"%(1000*(int(code1)/1000))
	for code in [code1, code2, code3, code4]:
		if post2insee.has_key(code):
			insee = get_insee(code, obj["town"], 4)
			if not insee is None:
				inseec,inseen = insee
				found = True
				ng += 1
				obj["insee_code"] = inseec
				coll.save(obj)
				break
	if found: continue
	# Look using name
	if town2insee.has_key(obj["town"]):
		best = None
		best_score = None
		for k in town2insee[ obj["town"] ].keys():
			score = int(obj["postalcode"]) - int(k)
			if (best is None) or (best_score>score):
				best = (obj["town"], k)
				best_score = score
		if best_score < 1000:
			found = True
			ng += 1
			obj["insee_code"] = town2insee[best[0]][best[1]]
			print "Matched %s/%s with %s/%s"% (obj["postalcode"], obj["town"], best[1], best[0])
			coll.save(obj)
	if found: continue
	# Look closest name
	best_name = None
	best_postal = None
	best_score = None
	for townC in town2insee.keys():
		score = jellyfish.levenshtein_distance(name, townC)
		if (best_score is None) or (score<best_score):
			best_score = score
			best_name = townC
	if best_score < 4:
		print "Maybe found %s for %s" % (best_name, name)
		best_postal = None
		for postalC in town2insee[best_name].keys():
			if postalcode == postalC:
				print "\t%s/%s matches %s/%s with score %d/0" % (postalC, best_name, postalcode, name, best_score)
				found = True
				ng += 1
				obj["insee_code"] = town2insee[best_name][postalC]
				coll.save(obj)
				break
			elif (best_postal is None) or (abs(int(postalcode)-int(postalC))<abs(int(postalcode)-int(best_postal))):
				best_postal = postalC
		if (not found) and (abs(int(postalcode)-int(best_postal))/100 <= 9):
			print "\tmaybe %s/%s matches %s/%s with score %d/%d" % (best_postal, best_name, postalcode, name, best_score, abs(int(postalcode)-int(best_postal)))
			found = True
			ng += 1
			obj["insee_code"] = town2insee[best_name][best_postal]
			coll.save(obj)
	if found: continue
	# Don't know :(
	if not found:
		print "Not found %s/%s" % (obj["postalcode"], obj["town"])
		nb +=1

print "%d found, %d not found" % (ng, nb)
		

