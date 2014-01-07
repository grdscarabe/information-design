#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Load in db data from http://data.farmsubsidy.org/ and INSEE

Files used: 
	=> http://data.farmsubsidy.org/FR.tar.bz2
	http://www.insee.fr/fr/methodes/nomenclatures/cog/telechargement/2013/txt/comsimp2013.zip
	(cf. http://www.insee.fr/fr/methodes/nomenclatures/cog/)
	=> http://www.galichon.com/codesgeo/data/insee.zip
"""

import pymongo
import csv
import jellyfish

########################## TOOLS

def normalizeTown(town):
	town2 = town.upper().replace("-", " ")
	words = town2.split(" ")
	if words[0] in ["LE", "LA", "LES"]:
		words = words[1:]
	for i in range(len(words)):
		if words[i] in ["ST", "STE", "SAINTE"]:
			words[i] = "SAINT"
	return "-".join(words)

########################## INSEE DATA

insee_headers = ["Commune", "Codepos", "Departement", "INSEE"]

post2insee = {}

problematicPost = set()
problematicTown = set()

with open("codepostal-codeinsee.csv", "r") as fh_insee:
	reader = csv.DictReader(fh_insee, delimiter=";", fieldnames=insee_headers)
	reader.next()
	for row in reader:
		if not post2insee.has_key( row["Codepos"] ):
			post2insee[ row["Codepos"] ] = {}
		post2insee[ row["Codepos"] ][ row["Commune"] ] = row["INSEE"]

def get_insee(postcode, name):
	"""
	Convert a postcode to an insee code.
	If no exact match, choose best candidate but record it as problematic.
	"""
	global problematicTown
	global problematicPost
	
	if not post2insee.has_key(postcode):
		# No match on postcode...
		problematicPost.add(postcode)
		return None
	elif post2insee[postcode].has_key(name.upper()):
		# Perfect match!
		return post2insee[postcode][name.upper()]
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
		if not best is None:
			return post2insee[postcode][best]
		else:
			return None

########################## FARMSUBSIDY DATA

recipient_headers = ["recipientId", "recipientIdx", "globalRecipientId", "globalRecipientIdx", "name", "address1", "address2", "zipcode", "town", "countryRecipient", "countryPayment", "geo1", "geo2", "geo3", "geo4", "geo1NationalLanguage", "geo2NationalLanguage", "geo3NationalLanguage", "geo4NationalLanguage", "lat", "lng"]
payment_headers = ["paymentId", "globalPaymentId", "globalRecipientId", "globalRecipientIdx", "globalSchemeId", "amountEuro", "amountNationalCurrency", "year", "countryPayment"]

conn = pymongo.Connection()
coll = conn["pac"]["recipients"]

# Load the recipients related data
with open("FR/recipient.txt", "r") as fh_recipient:
	reader = csv.DictReader(fh_recipient, delimiter=";", quotechar="\"", fieldnames=recipient_headers)
	reader.next()
	i = 0
	for row in reader:
		# Build document from row
		doc = {"_id": row["globalRecipientId"]}
		for k in recipient_headers:
			if (not row[k] is None) and len(row[k])>0:
				if k in ["lat", "lng"]:
					doc[k] = float(row[k])
				elif k=="zipcode":
					doc["postalcode"] = row["zipcode"].split("-")[-1]
					doc["zipcode"] = row["zipcode"]
				elif not k in ["recipientId", "recipientIdx", "globalRecipientId", "globalRecipientIdx"]:
					doc[k] = row[k]
		# Add insee id
		if doc.has_key("postalcode") and doc.has_key("town"):
			inseecode = get_insee(doc["postalcode"], doc["town"])
			if not inseecode is None:
				doc["insee_code"] = inseecode
		# Insert in database
		if (i % 1000) == 0:
			print "REC -> %d inserted / %d-%d problems with INSEE code" % (i, len(problematicPost), len(problematicTown))
		coll.insert(doc)
		i+=1

# Load the payments related data
with open("FR/payment.txt", "r") as fh_payment:
	reader = csv.DictReader(fh_payment, delimiter=";", quotechar="\"", fieldnames=payment_headers)
	reader.next()
	i = 0
	for row in reader:
		# Build subdocument from row
		recipient_id = row["globalRecipientId"]
		sdoc = {}
		for k in payment_headers:
			if (not row[k] is None) and len(row[k])>0:
				if k=="amountEuro":
					sdoc[k] = float(row[k])
				elif not k in ["globalRecipientId", "globalRecipientIdx"]:
					sdoc[k] = row[k]
		# Insert in database
		obj = coll.find_one({"_id": recipient_id})
		if not obj.has_key("payments"):
			obj["payments"] = []
		obj["payments"].append(sdoc)
		coll.save(obj)
		i+=1
		if (i % 1000) == 0:
			print "PAY -> %d inserted"%i

