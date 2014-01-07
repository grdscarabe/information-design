TRAITEMENT DONNÉES PAC
======================

Sources de données utilisées :
------------------------------

- Données collectées par l'initiative FarmSubsidy sur les subventions
de la PAC perçues par les agriculteurs français : 
http://data.farmsubsidy.org/FR.tar.bz2

- Table de correspondance entre les codes postaux et les codes INSEE
pour identifier de manière unique les communes :
http://www.galichon.com/codesgeo/data/insee.zip
Renommé en `codepostal-codeinsee.csv`

Problématique :
---------------

- Comment sont distribuées les subventions de la PAC sur le territoire 
français ?
- Y-a-t-il des inégalités entre les territoires ?
- Quelles sont les structures types qui perçoivent ces subventions ?


Méthodologie :
--------------

1. Import des données `FR/recipients.txt` et `FR/payments.txt` de FarmSubsidy
dans MongoDB avec le script `load-data.py`.
Exemple de document tel qu'inséré :
	{
		"_id" : "FR1113688",
		"town" : "BELGIQUE",
		"name" : "DEBEER POL",
		"geo1" : "Outside France",
		"countryRecipient" : "BE",
		"payments" : [
			{
				"globalPaymentId" : "FR2115439",
				"globalSchemeId" : "FR1",
				"year" : "2010",
				"paymentId" : "2115439",
				"amountEuro" : 6122.13,
				"countryPayment" : "FR"
			}
		],
		"countryPayment" : "FR"
	}

2. Rapprochement des informations sur la commune du récipiendaire avec le
code INSEE de la commune par le biais de la table de correspondance
`codepostal-codeinsee.csv`. 
Par défaut suppression des références aux cedex dans le nom des communes du
jeu de données de FarmSubsidy.

Stratégie de rapprochement dans `load-data.py` :
  - Correspondance exacte entre code postal et nom dans les deux jeux de 
    données
  - Correspondance exacte du code postal et recherche du nom le plus proche
    ayant ce code postal dans `codepostal-codeinsee.csv` en utilisant la
    distance de Levenshtein.

Stratégie de rapprochement dans `find-missing-insee.py` :
  - Recherche d'un code postal approchant en faisant une recherche dans la
    table de correspondance `codepostal-codeinsee.csv` par généralisation 
    successive des chiffres de poids faibles : 36249 > 36240 > 36200 > 36000
    Pas de généralisation au-delà du niveau département.
    Lorsqu'une correspondance est trouvée au niveau du code postal, sélection
    du nom de commune le plus proche à une distance Levenshtein de moins de 
    4 éditions .
  - Recherche d'une correspondance exacte sur le nom et sélection du code 
    postal le plus proche qui se trouve dans le même département.
  - Recherche d'une correspondance approximative entre le nom 
    (distance de Levenshtein < 4) et le code postal (< 900).

À la main en base, identification des codes postaux seuls à l'aide du site
http://www.code-postal-villes.com/ :
  - 97180 = Sainte-Anne, code insee 97128
  - 97140 = Capesterre-de-Marie-Galante, code insee 97108
  - 97134 = Saint-Louis, code insee 97126
  - 97131 = Petit-Canal, code insee 97119
  - 97121 = Anse-Bertrand, code insee 97102
  - 97117 = Port-Louis, code insee 97122
  - 97115 = Sainte-Rose, code insee 97129
  - 97111 = Morne-à-l'Eau, code insee 97116

Correction manuel des cas restants :
	db.recipients.find({"insee_code": {"$exists": false}, "countryRecipient": "FR", "town": {$exists: true}, "postalcode": {$exists: true}}, {town: 1, postalcode: 1}).sort({town: 1, postalcode: 1})
Utilisation du site http://www.code-postal-villes.com/ :
	db.recipients.update({"_id": {"$in": ["FR667181", "FR667276", "FR667277"]}, "insee_code": {"$exists": false}}, {"$set": {"insee_code": "01033"}}, false, true)
	db.recipients.update({"_id": "FR758968", "insee_code": {"$exists": false}}, {"$set": {"insee_code": "04070"}}, false, true)
	db.recipients.update({"_id": "FR689971", "insee_code": {"$exists": false}}, {"$set": {"insee_code": "04033"}}, false, true)
	db.recipients.update({"_id": "FR1113085", "insee_code": {"$exists": false}}, {"$set": {"insee_code": "07324"}}, false, true)
	db.recipients.update({"_id": {"$in": ["FR979234", "FR979235", "FR625044"]}, "insee_code": {"$exists": false}}, {"$set": {"insee_code": "10349"}}, false, true)
	db.recipients.update({"_id": "FR625045", "insee_code": {"$exists": false}}, {"$set": {"insee_code": "10336"}}, false, true)
	db.recipients.update({"_id": "FR1076995", "insee_code": {"$exists": false}}, {"$set": {"insee_code": "10383"}}, false, true)
	db.recipients.update({"_id": "FR1100985", "insee_code": {"$exists": false}}, {"$set": {"insee_code": "12300"}}, false, true)
	db.recipients.update({"_id": "FR1113211", "insee_code": {"$exists": false}}, {"$set": {"insee_code": "13078"}}, false, true)
	db.recipients.update({"_id": {"$in": ["FR1112842", "FR1112843"]}, "insee_code": {"$exists": false}}, {"$set": {"insee_code": "13028"}}, false, true)
	db.recipients.update({"_id": "FR630862", "insee_code": {"$exists": false}}, {"$set": {"insee_code": "13001"}}, false, true)
	db.recipients.update({"_id": {"$in": ["FR1012508", "FR1012510", "FR1012511", "FR1012512", "FR1141659", "FR1149171", "FR1012509", "FR1140457", "FR1122958", "FR1149172", "FR1012514", "FR1140647", "FR1012513", "FR1149173"]}, "insee_code": {"$exists": false}}, {"$set": {"insee_code": "17415"}}, false, true)
	db.recipients.update({"_id": "FR1133643", "insee_code": {"$exists": false}}, {"$set": {"insee_code": "17299"}}, false, true)
	db.recipients.update({"_id": "FR1116827", "insee_code": {"$exists": false}}, {"$set": {"insee_code": "2A004"}}, false, true)
	db.recipients.update({"_id": {"$in": ["FR1123973", "FR1112888", "FR1117995", "FR1131922"]}, "insee_code": {"$exists": false}}, {"$set": {"insee_code": "2A004"}}, false, true)
	db.recipients.update({"_id": {"$in": ["FR659973", "FR1123728", "FR1149812", "FR1149813"]}, "insee_code": {"$exists": false}}, {"$set": {"insee_code": "2B033"}}, false, true)
	db.recipients.update({"_id": {"$in": ["FR556768", "FR628122", "FR628123", "FR628124", "FR628125", "FR628126", "FR628127", "FR628128", "FR628129", "FR628131", "FR628132", "FR628133", "FR628134", "FR628135", "FR628136", "FR628137", "FR628130", "FR1140212", "FR628138"]}, "insee_code": {"$exists": false}}, {"$set": {"insee_code": "97101"}}, false, true)
	db.recipients.update({"_id": "FR628139", "insee_code": {"$exists": false}}, {"$set": {"insee_code": "97101"}}, false, true)
	db.recipients.update({"_id": {"$in": ["FR652651", "FR1116664"]}, "insee_code": {"$exists": false}}, {"$set": {"insee_code": "97361"}}, false, true)
	db.recipients.update({"_id": {"$in": ["FR1159847", "FR669118"]}, "insee_code": {"$exists": false}}, {"$set": {"insee_code": "62108"}}, false, true)
	db.recipients.update({"_id": {"$in": ["FR255568", "FR680863", "FR53886"]}, "insee_code": {"$exists": false}}, {"$set": {"insee_code": "33063"}}, false, true)
	db.recipients.update({"_id": {"$in": ["FR1142421", "FR1153283"]}, "insee_code": {"$exists": false}}, {"$set": {"insee_code": "33069"}}, false, true)
	db.recipients.update({"_id": {"$in": ["FR711922", "FR1165492"]}, "insee_code": {"$exists": false}}, {"$set": {"insee_code": "95127"}}, false, true)
	db.recipients.update({"_id": {"$in": ["FR625655", "FR625657", "FR625658"]}, "insee_code": {"$exists": false}}, {"$set": {"insee_code": "72061"}}, false, true)
	db.recipients.update({"_id": {"$in": ["FR1137209", "FR1143554", "FR1132450", "FR1141230", "FR725771", "FR1164224"]}, "insee_code": {"$exists": false}}, {"$set": {"insee_code": "84037"}}, false, true)
	db.recipients.update({"_id": {"$in": ["FR744968", "FR1137621", "FR1159014", "FR744997"]}, "insee_code": {"$exists": false}}, {"$set": {"insee_code": "58086"}}, false, true)
	db.recipients.update({"_id": "FR636283", "insee_code": {"$exists": false}}, {"$set": {"insee_code": "27016"}}, false, true)
	db.recipients.update({"_id": "FR640490", "insee_code": {"$exists": false}}, {"$set": {"insee_code": "83004"}}, false, true)
	db.recipients.update({"_id": "FR651737", "insee_code": {"$exists": false}}, {"$set": {"insee_code": "59036"}}, false, true)
	db.recipients.update({"_id": "FR659675", "insee_code": {"$exists": false}}, {"$set": {"insee_code": "59051"}}, false, true)
	db.recipients.update({"_id": "FR661755", "insee_code": {"$exists": false}}, {"$set": {"insee_code": "72024"}}, false, true)
	db.recipients.update({"_id": "FR665941", "insee_code": {"$exists": false}}, {"$set": {"insee_code": "17038"}}, false, true)
	db.recipients.update({"_id": "FR682112", "insee_code": {"$exists": false}}, {"$set": {"insee_code": "74045"}}, false, true)
	db.recipients.update({"_id": "FR1136116", "insee_code": {"$exists": false}}, {"$set": {"insee_code": "97302"}}, false, true)
	db.recipients.update({"_id": "FR712896", "insee_code": {"$exists": false}}, {"$set": {"insee_code": "77067"}}, false, true)
	db.recipients.update({"_id": "FR722032", "insee_code": {"$exists": false}}, {"$set": {"insee_code": "44035"}}, false, true)
	db.recipients.update({"_id": "FR742009", "insee_code": {"$exists": false}}, {"$set": {"insee_code": "78172"}}, false, true)
	db.recipients.update({"_id": "FR1151151", "insee_code": {"$exists": false}}, {"$set": {"insee_code": "25248"}}, false, true)
	db.recipients.update({"_id": "FR789694", "insee_code": {"$exists": false}}, {"$set": {"insee_code": "80368"}}, false, true)
	db.recipients.update({"_id": "FR792049", "insee_code": {"$exists": false}}, {"$set": {"insee_code": "83063"}}, false, true)
	db.recipients.update({"_id": "FR1143306", "insee_code": {"$exists": false}}, {"$set": {"insee_code": "97113"}}, false, true)
	db.recipients.update({"_id": {"$in": ["FR811277", "FR811313"]}, "insee_code": {"$exists": false}}, {"$set": {"insee_code": "76351"}}, false, true)
	db.recipients.update({"_id": {"$in": ["FR811314", "FR811315", "FR811316", "FR811317", "FR811318", "FR1162720"]}, "insee_code": {"$exists": false}}, {"$set": {"insee_code": "7
6351"}}, false, true)
	db.recipients.update({"_id": {"$in": ["FR812700", "FR1164554", "FR1134406", "FR812701", "FR812702", "FR812703", "FR1164555", "FR1132110", "FR1164556"]}, "insee_code": {"$exists": false}}, {"$set": {"insee_code": "85109"}}, false, true)
	db.recipients.update({"_id": "FR1135226", "insee_code": {"$exists": false}}, {"$set": {"insee_code": "67218"}}, false, true)
	db.recipients.update({"_id": "FR854197", "insee_code": {"$exists": false}}, {"$set": {"insee_code": "72172"}}, false, true)
	db.recipients.update({"_id": "FR1117458", "insee_code": {"$exists": false}}, {"$set": {"insee_code": "69382"}}, false, true)
	db.recipients.update({"_id": "FR858049", "insee_code": {"$exists": false}}, {"$set": {"insee_code": "59368"}}, false, true)
	db.recipients.update({"_id": "FR868372", "insee_code": {"$exists": false}}, {"$set": {"insee_code": "29144"}}, false, true)
	db.recipients.update({"_id": "FR881472", "insee_code": {"$exists": false}}, {"$set": {"insee_code": "54370"}}, false, true)
	db.recipients.update({"_id": "FR625814", "insee_code": {"$exists": false}}, {"$set": {"insee_code": "97313"}}, false, true)
	db.recipients.update({"_id": {"$in": ["FR897793", "FR897792", "FR897794"]}, "insee_code": {"$exists": false}}, {"$set": {"insee_code": " 97313"}}, false, true)
	db.recipients.update({"_id": {"$in": ["FR1120235", "FR1163056"]}, "insee_code": {"$exists": false}}, {"$set": {"insee_code": "78440"}}, false, true)
	db.recipients.update({"_id": "FR913484", "insee_code": {"$exists": false}}, {"$set": {"insee_code": "23144"}}, false, true)
	db.recipients.update({"_id": {"$in": ["FR924654", "FR1162709", "FR924655"]}, "insee_code": {"$exists": false}}, {"$set": {"insee_code": "75107"}}, false, true)
	db.recipients.update({"_id": "FR117800", "insee_code": {"$exists": false}}, {"$set": {"insee_code": "75112"}}, false, true)
	db.recipients.update({"_id": {"$in": ["FR117797", "FR117798", "FR139384", "FR250456", "FR373719", "FR377911", "FR385716", "FR408584", "FR440877", "FR503527", "FR567006"]}, "insee_code": {"$exists": false}}, {"$set": {"insee_code": "75112"}}, false, true)
	db.recipients.update({"_id": {"$in": ["FR117796", "FR117799"]}, "insee_code": {"$exists": false}}, {"$set": {"insee_code": "75109"}}, false, true)
	db.recipients.update({"_id": {"$in": ["FR625375", "FR625401"]}, "insee_code": {"$exists": false}}, {"$set": {"insee_code": "49242"}}, false, true)
	db.recipients.update({"_id": {"$in": ["FR946558", "FR946559", "FR946560"]}, "insee_code": {"$exists": false}}, {"$set": {"insee_code": "84092"}}, false, true)
	db.recipients.update({"_id": {"$in": ["FR946955", "FR946956", "FR1116414", "FR1143447", "FR1145053"]}, "insee_code": {"$exists": false}}, {"$set": {"insee_code": "49137"}}, false, true)
	db.recipients.update({"_id": {"$in": ["FR1136993", "FR1166009", "FR947309"]}, "insee_code": {"$exists": false}}, {"$set": {"insee_code": "97407"}}, false, true)
	db.recipients.update({"_id": "FR1165440", "insee_code": {"$exists": false}}, {"$set": {"insee_code": "92062"}}, false, true)
	db.recipients.update({"_id": {"$in": ["FR1141754", "FR966237"]}, "insee_code": {"$exists": false}}, {"$set": {"insee_code": "85191"}}, false, true)
	db.recipients.update({"_id": "FR624986", "insee_code": {"$exists": false}}, {"$set": {"insee_code": "95527"}}, false, true)
	db.recipients.update({"_id": "FR968294", "insee_code": {"$exists": false}}, {"$set": {"insee_code": "26281"}}, false, true)
	db.recipients.update({"_id": "FR1129632", "insee_code": {"$exists": false}}, {"$set": {"insee_code": "92063"}}, false, true)
	db.recipients.update({"_id": "FR973688", "insee_code": {"$exists": false}}, {"$set": {"insee_code": "94065"}}, false, true)
	db.recipients.update({"_id": {"$in": ["FR1141711", "FR974081", "FR974083", "FR974082", "FR974084", "FR1164401", "FR974086", "FR974087", "FR974088"]}, "insee_code": {"$exists": false}}, {"$set": {"insee_code": "85194"}}, false, true)
	db.recipients.update({"_id": "FR977855", "insee_code": {"$exists": false}}, {"$set": {"insee_code": "30258"}}, false, true)
	db.recipients.update({"_id": {"$in": ["FR979161", "FR135288", "FR1135285", "FR979165", "FR979166", "FR979168", "FR979170", "FR979171"]}, "insee_code": {"$exists": false}}, {"$set": {"insee_code": "97414"}}, false, true)
	db.recipients.update({"_id": "FR941882", "insee_code": {"$exists": false}}, {"$set": {"insee_code": "62660"}}, false, true)
	db.recipients.update({"_id": {"$in": ["FR979172", "FR979173", "FR979169", "FR979167", "FR979174", "FR979175", "FR1165969", "FR135141", "FR135142"]}, "insee_code": {"$exists": false}}, {"$set": {"insee_code": "97414"}}, false, true)
	db.recipients.update({"_id": {"$in": ["FR625501", "FR625503", "FR625504", "FR625506", "FR625507"]}, "insee_code": {"$exists": false}}, {"$set": {"insee_code": "53211"}}, false, true)
	db.recipients.update({"_id": "FR978982", "insee_code": {"$exists": false}}, {"$set": {"insee_code": "97311"}}, false, true)
	db.recipients.update({"_id": "FR981757", "insee_code": {"$exists": false}}, {"$set": {"insee_code": "85272"}}, false, true)
	db.recipients.update({"_id": "FR51039", "insee_code": {"$exists": false}}, {"$set": {"insee_code": "24367"}}, false, true)
	db.recipients.update({"_id": {"$in": ["FR118498", "FR458776"]}, "insee_code": {"$exists": false}}, {"$set": {"insee_code": "76575"}}, false, true)
	db.recipients.update({"_id": "FR51690", "insee_code": {"$exists": false}}, {"$set": {"insee_code": "31483"}}, false, true)
	db.recipients.update({"_id": {"$in": ["FR135144", "FR135145", "FR135146", "FR135147", "FR135148", "FR135149", "FR135150", "FR135151", "FR135152", "FR135153", "FR135154", "FR135155", "FR135684"]}, "insee_code": {"$exists": false}}, {"$set": {"insee_code": "97414"}}, false, true)
	db.recipients.update({"_id": {"$in": ["FR625422", "FR625424", "FR625430"]}, "insee_code": {"$exists": false}}, {"$set": {"insee_code": "51002"}}, false, true)
	db.recipients.update({"_id": {"$in": ["FR625608", "FR625614", "FR625610"]}, "insee_code": {"$exists": false}}, {"$set": {"insee_code": "66186"}}, false, true)
	db.recipients.update({"_id": "FR76294", "insee_code": {"$exists": false}}, {"$set": {"insee_code": "47233"}}, false, true)
	db.recipients.update({"_id": "FR995422", "insee_code": {"$exists": false}}, {"$set": {"insee_code": "81284"}}, false, true)
	db.recipients.update({"_id": "FR997875", "insee_code": {"$exists": false}}, {"$set": {"insee_code": "83126"}}, false, true)
	db.recipients.update({"_id": "FR1009784", "insee_code": {"$exists": false}}, {"$set": {"insee_code": "49267"}}, false, true)
	db.recipients.update({"_id": {"$in": ["FR1161673", "FR1134230"]}, "insee_code": {"$exists": false}}, {"$set": {"insee_code": "69194"}}, false, true)
	db.recipients.update({"_id": "FR1117900", "insee_code": {"$exists": false}}, {"$set": {"insee_code": "88413"}}, false, true)
	db.recipients.update({"_id": "FR1162891", "insee_code": {"$exists": false}}, {"$set": {"insee_code": "76575"}}, false, true)
	db.recipients.update({"_id": "FR1145390", "insee_code": {"$exists": false}}, {"$set": {"insee_code": "88415"}}, false, true)
	db.recipients.update({"_id": "FR1023496", "insee_code": {"$exists": false}}, {"$set": {"insee_code": "91549"}}, false, true)
	db.recipients.update({"_id": "FR1033823", "insee_code": {"$exists": false}}, {"$set": {"insee_code": "74243"}}, false, true)
	db.recipients.update({"_id": {"$in": ["FR1058327", "FR1058328"]}, "insee_code": {"$exists": false}}, {"$set": {"insee_code": "44190"}}, false, true)
	db.recipients.update({"_id": {"$in": ["FR1066048", "FR1066049", "FR1066047", "FR1066054", "FR1066053", "FR1066046", "FR1066056", "FR1066055"]}, "insee_code": {"$exists": false}}, {"$set": {"insee_code": "97422"}}, false, true)
	db.recipients.update({"_id": {"$in": ["FR1066051", "FR1066050", "FR1066052"]}, "insee_code": {"$exists": false}}, {"$set": {"insee_code": "97422"}}, false, true)
	db.recipients.update({"_id": {"$in": ["FR1128874", "FR1152853"]}, "insee_code": {"$exists": false}}, {"$set": {"insee_code": "33529"}}, false, true)
	db.recipients.update({"_id": "FR1075392", "insee_code": {"$exists": false}}, {"$set": {"insee_code": "56252"}}, false, true)
	db.recipients.update({"_id": {"$in": ["FR1080384", "FR1158879"]}, "insee_code": {"$exists": false}}, {"$set": {"insee_code": "57679"}}, false, true)
	db.recipients.update({"_id": "FR1080562", "insee_code": {"$exists": false}}, {"$set": {"insee_code": "97423"}}, false, true)
	db.recipients.update({"_id": {"$in": ["FR1101016", "FR1161642", "FR1101290", "FR1101291", "FR1143052", "FR135586"]}, "insee_code": {"$exists": false}}, {"$set": {"insee_code": "69264"}}, false, true)
	db.recipients.update({"_id": "FR1081621", "insee_code": {"$exists": false}}, {"$set": {"insee_code": "44211"}}, false, true)
	db.recipients.update({"_id": "FR1085914", "insee_code": {"$exists": false}}, {"$set": {"insee_code": "31567"}}, false, true)
	db.recipients.update({"_id": "FR1086893", "insee_code": {"$exists": false}}, {"$set": {"insee_code": "56260"}}, false, true)
	db.recipients.update({"_id": "FR1102201", "insee_code": {"$exists": false}}, {"$set": {"insee_code": "30351"}}, false, true)
	db.recipients.update({"_id": "FR556040", "insee_code": {"$exists": false}}, {"$set": {"insee_code": "85135"}}, false, true)
	db.recipients.update({"_id": "FR135441", "insee_code": {"$exists": false}}, {"$set": {"insee_code": "75112"}}, false, true)
	db.recipients.update({"_id": "FR633797", "insee_code": {"$exists": false}}, {"$set": {"insee_code": "64017"}}, false, true)
	db.recipients.update({"_id": "FR645735", "insee_code": {"$exists": false}}, {"$set": {"insee_code": "07017"}}, false, true)
	db.recipients.update({"_id": "FR648151", "insee_code": {"$exists": false}}, {"$set": {"insee_code": "18017"}}, false, true)
	db.recipients.update({"_id": "FR648382", "insee_code": {"$exists": false}}, {"$set": {"insee_code": "55015"}}, false, true)
	db.recipients.update({"_id": "FR649908", "insee_code": {"$exists": false}}, {"$set": {"insee_code": "60031"}}, false, true)
	db.recipients.update({"_id": "FR658447", "insee_code": {"$exists": false}}, {"$set": {"insee_code": "54046"}}, false, true)
	db.recipients.update({"_id": "FR661303", "insee_code": {"$exists": false}}, {"$set": {"insee_code": "33036"}}, false, true)
	db.recipients.update({"_id": "FR695918", "insee_code": {"$exists": false}}, {"$set": {"insee_code": "28065"}}, false, true)
	db.recipients.update({"_id": "FR733741", "insee_code": {"$exists": false}}, {"$set": {"insee_code": "52127"}}, false, true)
	db.recipients.update({"_id": "FR734608", "insee_code": {"$exists": false}}, {"$set": {"insee_code": "37076"}}, false, true)
	db.recipients.update({"_id": "FR735145", "insee_code": {"$exists": false}}, {"$set": {"insee_code": "33128"}}, false, true)
	db.recipients.update({"_id": "FR741351", "insee_code": {"$exists": false}}, {"$set": {"insee_code": "19060"}}, false, true)
	db.recipients.update({"_id": "FR745662", "insee_code": {"$exists": false}}, {"$set": {"insee_code": "02217"}}, false, true)
	db.recipients.update({"_id": "FR756758", "insee_code": {"$exists": false}}, {"$set": {"insee_code": "07077"}}, false, true)
	db.recipients.update({"_id": "FR764705", "insee_code": {"$exists": false}}, {"$set": {"insee_code": "61148"}}, false, true)
	db.recipients.update({"_id": "FR768167", "insee_code": {"$exists": false}}, {"$set": {"insee_code": "04077"}}, false, true)
	db.recipients.update({"_id": "FR769901", "insee_code": {"$exists": false}}, {"$set": {"insee_code": "53096"}}, false, true)
	db.recipients.update({"_id": "FR775502", "insee_code": {"$exists": false}}, {"$set": {"insee_code": "13036"}}, false, true)
	db.recipients.update({"_id": "FR786926", "insee_code": {"$exists": false}}, {"$set": {"insee_code": "16145"}}, false, true)
	db.recipients.update({"_id": "FR798252", "insee_code": {"$exists": false}}, {"$set": {"insee_code": "07096"}}, false, true)
	db.recipients.update({"_id": "FR829559", "insee_code": {"$exists": false}}, {"$set": {"insee_code": "60344"}}, false, true)
	db.recipients.update({"_id": "FR835722", "insee_code": {"$exists": false}}, {"$set": {"insee_code": "05070"}}, false, true)
	db.recipients.update({"_id": "FR860014", "insee_code": {"$exists": false}}, {"$set": {"insee_code": "87091"}}, false, true)
	db.recipients.update({"_id": "FR877916", "insee_code": {"$exists": false}}, {"$set": {"insee_code": "49204"}}, false, true)
	db.recipients.update({"_id": "FR892535", "insee_code": {"$exists": false}}, {"$set": {"insee_code": "09206"}}, false, true)
	db.recipients.update({"_id": "FR894775", "insee_code": {"$exists": false}}, {"$set": {"insee_code": "01262"}}, false, true)
	db.recipients.update({"_id": "FR942186", "insee_code": {"$exists": false}}, {"$set": {"insee_code": "29213"}}, false, true)
	db.recipients.update({"_id": "FR966774", "insee_code": {"$exists": false}}, {"$set": {"insee_code": "07192"}}, false, true)
	db.recipients.update({"_id": "FR975497", "insee_code": {"$exists": false}}, {"$set": {"insee_code": "01334"}}, false, true)
	db.recipients.update({"_id": "FR975589", "insee_code": {"$exists": false}}, {"$set": {"insee_code": "07212"}}, false, true)
	db.recipients.update({"_id": "FR1005611", "insee_code": {"$exists": false}}, {"$set": {"insee_code": "16298"}}, false, true)
	db.recipients.update({"_id": "FR1061069", "insee_code": {"$exists": false}}, {"$set": {"insee_code": "01388"}}, false, true)
	db.recipients.update({"_id": "FR1066952", "insee_code": {"$exists": false}}, {"$set": {"insee_code": "03277"}}, false, true)
	db.recipients.update({"_id": "FR1069469", "insee_code": {"$exists": false}}, {"$set": {"insee_code": "33530"}}, false, true)
	db.recipients.update({"_id": "FR1071421", "insee_code": {"$exists": false}}, {"$set": {"insee_code": "03284"}}, false, true)
	db.recipients.update({"_id": "FR1073900", "insee_code": {"$exists": false}}, {"$set": {"insee_code": "26351"}}, false, true)
	db.recipients.update({"_id": "FR1077276", "insee_code": {"$exists": false}}, {"$set": {"insee_code": "81301"}}, false, true)
	db.recipients.update({"_id": "FR1087543", "insee_code": {"$exists": false}}, {"$set": {"insee_code": "03298"}}, false, true)


Calculs :
---------

Consolidation des données de paiment issues de la base à l'aide des 
map/reduce décrits dans `aggregation-data.js`:

  - Par région/an et par type de subvention :
	{
		"result" : "payments_per_region_year",
		"timeMillis" : 171472,
		"counts" : {
			"input" : 1165359,
			"emit" : 2591213,
			"reduce" : 125308,
			"output" : 148
		},
		"ok" : 1,
	}

  - Par département/an et par type de subvention :
	{
		"result" : "payments_per_department_year",
		"timeMillis" : 156303,
		"counts" : {
			"input" : 1164889,
			"emit" : 2590462,
			"reduce" : 150021,
			"output" : 596
		},
		"ok" : 1,
	}

  - Par communes/ans et par type de subvention :
	{
		"result" : "payments_per_town_year",
		"timeMillis" : 276460,
		"counts" : {
			"input" : 1164954,
			"emit" : 2590547,
			"reduce" : 624816,
			"output" : 199118
		},
		"ok" : 1,
	}

Export town/year :
------------------

Export des données depuis MongoDB :
	mongoexport -d pac -c payments_per_town_year -o export-payments-per-town-year.json
Puis conversion du JSON en CSV :
	import csv, json, codecs
	headers = ["insee_code", "year", "Livestock", "Crop", 
		"Paiements prêts bonifiés (Feader)", 
		"European Agricultural Fund for Rural Development", "Autres paiements du Feaga", 
		"Paiements directs aux agriculteurs au titre du Feaga", "total"]
	with codecs.open("export-payments-per-town-year.json", "r", "utf-8") as fhread:
		with open("export-payments-per-town-year.csv", "w") as fhwrite:
			writer = csv.DictWriter(fhwrite, fieldnames=headers, restval="0")
			writer.writeheader()
			for line in fhread:
				doc = json.loads(line)
				row = {"insee_code": doc["_id"]["town"], "year": doc["_id"]["year"]}
				for k in doc["value"].keys():
					row[k.encode("utf-8")] = doc["value"][k]
				writer.writerow(row)

Export department/year :
------------------------

Export des données depuis MongoDB :
	mongoexport -d pac -c payments_per_department_year -o export-payments-per-department-year.json
Puis conversion du JSON en CSV :
import csv, json, codecs
headers = ["department", "year", "Livestock", "Crop", 
	"Paiements prêts bonifiés (Feader)", 
	"European Agricultural Fund for Rural Development", "Autres paiements du Feaga", 
	"Paiements directs aux agriculteurs au titre du Feaga", "total"]
with codecs.open("export-payments-per-department-year.json", "r", "utf-8") as fhread:
	with open("export-payments-per-department-year.csv", "w") as fhwrite:
		writer = csv.DictWriter(fhwrite, fieldnames=headers, restval="0")
		writer.writeheader()
		for line in fhread:
			doc = json.loads(line)
			row = {"department": doc["_id"]["department"].encode("utf-8"), "year": doc["_id"]["year"]}
			for k in doc["value"].keys():
				row[k.encode("utf-8")] = doc["value"][k]
			writer.writerow(row)

Export region/year :
--------------------

Export des données depuis MongoDB :
	mongoexport -d pac -c payments_per_region_year -o export-payments-per-region-year.json
Puis conversion du JSON en CSV :
import csv, json, codecs
headers = ["region", "year", "Livestock", "Crop", 
	"Paiements prêts bonifiés (Feader)", 
	"European Agricultural Fund for Rural Development", "Autres paiements du Feaga", 
	"Paiements directs aux agriculteurs au titre du Feaga", "total"]
with codecs.open("export-payments-per-region-year.json", "r", "utf-8") as fhread:
	with open("export-payments-per-region-year.csv", "w") as fhwrite:
		writer = csv.DictWriter(fhwrite, fieldnames=headers, restval="0")
		writer.writeheader()
		for line in fhread:
			doc = json.loads(line)
			row = {"region": doc["_id"]["region"].encode("utf-8"), "year": doc["_id"]["year"]}
			for k in doc["value"].keys():
				row[k.encode("utf-8")] = doc["value"][k]
			writer.writerow(row)

Projection sur la carte des départements :
------------------------------------------

