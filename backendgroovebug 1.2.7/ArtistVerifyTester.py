# -*- coding: utf-8 -*-
from django.utils import simplejson as json
import httplib2

json_works = {"library":[{"song count":"12","name":"A.F.I.","last played":"2011-10-22 01:26:48 +0000"},{"song count":"1","name":"Active Child","last played":"2011-10-22 01:55:30 +0000"},{"song count":"15","name":"Adam Green","last played":"(null)"},{"song count":"1","name":"Adema","last played":"(null)"},{"song count":"1","name":"Agoria","last played":"2011-10-27 02:53:39 +0000"},{"song count":"22","name":"Air","last played":"2011-10-24 03:46:13 +0000"},{"song count":"16","name":"Alice In Chains","last played":"(null)"},{"song count":"1","name":"Alicia Keys/Nas","last played":"2011-09-13 07:23:50 +0000"},{"song count":"25","name":"Alien Ant Farm","last played":"(null)"},{"song count":"1","name":"Amy LaVere","last played":"(null)"},{"song count":"11","name":"Animal Collective","last played":"(null)"},{"song count":"20","name":"Aphex Twin","last played":"(null)"},{"song count":"1","name":"Army Navy","last played":"(null)"},{"song count":"13","name":"At The Drive-In","last played":"(null)"},{"song count":"48","name":"Atmosphere","last played":"(null)"},{"song count":"14","name":"Audioslave","last played":"(null)"},{"song count":"1","name":"Avicii","last played":"2011-10-27 02:56:46 +0000"},{"song count":"27","name":"Barenaked Ladies","last played":"(null)"},{"song count":"93","name":"Beastie Boys","last played":"2011-06-16 01:39:56 +0000"},{"song count":"1","name":"Beastie Boys & Nas","last played":"(null)"},{"song count":"1","name":"Beastie Boys & Santigold","last played":"(null)"},{"song count":"76","name":"Beck","last played":"(null)"},{"song count":"1","name":"Beirut","last played":"2011-11-24 01:02:45 +0000"},{"song count":"13","name":"Better Than Ezra","last played":"(null)"},{"song count":"12","name":"Biffy Clyro","last played":"(null)"},{"song count":"12","name":"Bigdumbface","last played":"(null)"},{"song count":"26","name":"Bill Withers","last played":"(null)"},{"song count":"1","name":"Black Milk","last played":"(null)"},{"song count":"17","name":"Black Moth Super Rainbow","last played":"(null)"},{"song count":"11","name":"Blackie","last played":"(null)"},{"song count":"41","name":"Blink-182","last played":"2011-10-22 08:03:21 +0000"},{"song count":"11","name":"Bliss 66","last played":"(null)"},{"song count":"14","name":"Bloc Party","last played":"(null)"},{"song count":"1","name":"Blood Orange","last played":"2011-10-27 00:21:34 +0000"},{"song count":"1","name":"Bob Acri","last played":"(null)"},{"song count":"26","name":"Bob Dylan","last played":"(null)"},{"song count":"1","name":"Bobby Darin","last played":"(null)"},{"song count":"1","name":"Bon Jovi","last played":"(null)"},{"song count":"1","name":"Bootie Brown/Gorillaz","last played":"2011-10-31 00:57:55 +0000"},{"song count":"1","name":"Brand New","last played":"(null)"},{"song count":"12","name":"Brant Bjork","last played":"(null)"},{"song count":"1","name":"Bravehearts/Nas","last played":"(null)"},{"song count":"24","name":"Breaking Benjamin","last played":"2011-09-20 06:51:57 +0000"},{"song count":"14","name":"Brian Eno","last played":"(null)"},{"song count":"18","name":"Brian Eno & David Byrne","last played":"2011-10-24 02:07:10 +0000"},{"song count":"10","name":"Brian Eno & Jah Wobble","last played":"(null)"},{"song count":"7","name":"Bruce Springsteen","last played":"(null)"},{"song count":"1","name":"Bryan Ford","last played":"(null)"},{"song count":"17","name":"Buckethead","last played":"(null)"},{"song count":"1","name":"Buddy","last played":"(null)"},{"song count":"41","name":"Bush","last played":"2011-10-08 03:24:55 +0000"},{"song count":"11","name":"Cage The Elephant","last played":"(null)"},{"song count":"74","name":"Cake","last played":"(null)"},{"song count":"1","name":"Califone","last played":"2011-11-24 01:51:34 +0000"},{"song count":"1","name":"Captain Beefheart & The Magic Band","last played":"2011-11-24 00:44:19 +0000"},{"song count":"1","name":"Catcall","last played":"(null)"},{"song count":"27","name":"Catch 22","last played":"(null)"},{"song count":"1","name":"Cee Lo Green","last played":"(null)"},{"song count":"4","name":"Charles Mingus","last played":"(null)"},{"song count":"11","name":"Chevelle","last played":"(null)"},{"song count":"14","name":"Chim Charoo","last played":"(null)"},{"song count":"1","name":"Chingy/I-20/Ludacris/Tity Boi","last played":"(null)"},{"song count":"12","name":"Chronic Future","last played":"(null)"},{"song count":"35","name":"Citizen Cope","last played":"(null)"},{"song count":"11","name":"CKY","last played":"(null)"},{"song count":"1","name":"Claudette Ortiz/Kelis/Nas","last played":"(null)"},{"song count":"12","name":"Cold War Kids","last played":"(null)"},{"song count":"10","name":"Coldplay","last played":"(null)"},{"song count":"59","name":"Collective Soul","last played":"2011-10-22 08:36:21 +0000"},{"song count":"11","name":"Cream","last played":"(null)"},{"song count":"22","name":"Creed","last played":"(null)"},{"song count":"20","name":"Creedence Clearwater Revival","last played":"(null)"},{"song count":"1","name":"Crystal Antlers","last played":"(null)"},{"song count":"11","name":"The Cure","last played":"(null)"},{"song count":"12","name":"Dave Matthews Band","last played":"(null)"},{"song count":"9","name":"David Bowie","last played":"(null)"},{"song count":"23","name":"De La Soul","last played":"(null)"},{"song count":"1","name":"De La Soul/Gorillaz","last played":"2011-10-31 01:01:37 +0000"},{"song count":"29","name":"Dead Kennedys","last played":"(null)"},{"song count":"10","name":"The Decemberists","last played":"2011-10-22 09:47:00 +0000"},{"song count":"14","name":"Deerhoof","last played":"2011-06-16 22:49:34 +0000"},{"song count":"33","name":"Deftones","last played":"(null)"},{"song count":"21","name":"Deltron 3030","last played":"2011-06-29 04:33:20 +0000"},{"song count":"15","name":"Descendents","last played":"(null)"},{"song count":"13","name":"Desert Sessions","last played":"(null)"},{"song count":"17","name":"Devin The Dude","last played":"(null)"},{"song count":"1","name":"Dex Romweber Duo","last played":"(null)"},{"song count":"1","name":"Digitalism","last played":"(null)"},{"song count":"9","name":"Dirty Projectors","last played":"2011-11-14 04:29:12 +0000"},{"song count":"14","name":"Disturbed","last played":"(null)"},{"song count":"12","name":"DJ Shadow","last played":"(null)"},{"song count":"1","name":"Dolla Boy/Ludacris/Tity Boi","last played":"(null)"},{"song count":"9","name":"Donatello","last played":"(null)"},{"song count":"16","name":"Dr. Dre","last played":"(null)"},{"song count":"19","name":"Dr. Octagon","last played":"(null)"},{"song count":"1","name":"Drowning Pool","last played":"2011-08-16 01:13:10 +0000"},{"song count":"1","name":"Ducktails","last played":"(null)"},{"song count":"22","name":"Eddie Terrell","last played":"2011-09-06 20:33:50 +0000"},{"song count":"1","name":"Edens Edge","last played":"(null)"},{"song count":"32","name":"Edwin Terrell","last played":"(null)"},{"song count":"54","name":"Eminem","last played":"(null)"},{"song count":"1","name":"Eminem Ft. kobe-","last played":"2011-06-29 05:48:52 +0000"},{"song count":"1","name":"Eminem Ft. Lil Wayne","last played":"2011-06-29 05:38:36 +0000"},{"song count":"1","name":"Eminem Ft. Pink","last played":"2011-06-29 05:56:51 +0000"},{"song count":"1","name":"Eminem Ft. Rihanna","last played":"2011-06-29 06:42:50 +0000"},{"song count":"1","name":"Eric Clapton","last played":"(null)"},{"song count":"16","name":"Evanescence","last played":"(null)"},{"song count":"35","name":"Eve 6","last played":"(null)"},{"song count":"27","name":"Everclear","last played":"(null)"},{"song count":"1","name":"Excision & Datsik","last played":"2011-10-22 02:11:06 +0000"},{"song count":"1","name":"Exies","last played":"2011-10-22 02:13:57 +0000"},{"song count":"48","name":"Faith No More","last played":"2011-10-22 02:50:23 +0000"},{"song count":"1","name":"Fat Pat","last played":"(null)"},{"song count":"11","name":"Fatboy Slim","last played":"(null)"},{"song count":"14","name":"Feist","last played":"(null)"},{"song count":"2","name":"Filter","last played":"(null)"},{"song count":"48","name":"Foo Fighters","last played":"(null)"},{"song count":"11","name":"Foreign Objects","last played":"(null)"},{"song count":"7","name":"Frank Sinatra","last played":"(null)"},{"song count":"41","name":"Frank Zappa","last played":"(null)"},{"song count":"14","name":"Freestyle Fellowship","last played":"(null)"},{"song count":"2","name":"Frou Frou","last played":"(null)"},{"song count":"3","name":"Fuel","last played":"(null)"},{"song count":"24","name":"Fugazi","last played":"2011-10-07 03:14:04 +0000"},{"song count":"17","name":"The Fugees","last played":"(null)"},{"song count":"7","name":"Funkadelic","last played":"(null)"},{"song count":"1","name":"Future Islands","last played":"2011-10-27 00:11:14 +0000"},{"song count":"52","name":"G. Love & Special Sauce","last played":"(null)"},{"song count":"5","name":"Gangrene","last played":"(null)"},{"song count":"1","name":"Gangrene Feat. Big Twins","last played":"(null)"},{"song count":"3","name":"Gangrene Feat. DJ Romes","last played":"(null)"},{"song count":"1","name":"Gangrene Feat. Fashawn & Evidence","last played":"(null)"},{"song count":"1","name":"Gangrene Feat. Guilty Simpson","last played":"(null)"},{"song count":"1","name":"Gangrene Feat. MED","last played":"(null)"},{"song count":"1","name":"Gangrene Feat. Planet Asia","last played":"(null)"},{"song count":"1","name":"Gangrene Feat. Raekwon","last played":"(null)"},{"song count":"1","name":"Gangrene Feat. Roc C","last played":"(null)"},{"song count":"1","name":"Genesis","last played":"(null)"},{"song count":"14","name":"Gnarls Barkley","last played":"(null)"},{"song count":"1","name":"Godsmack","last played":"2011-06-29 08:55:31 +0000"},{"song count":"27","name":"Good Charlotte","last played":"(null)"},{"song count":"39","name":"Gorillaz","last played":"(null)"},{"song count":"1","name":"Gorillaz/MF Doom","last played":"2011-10-31 01:13:01 +0000"},{"song count":"1","name":"Gorillaz/Roots Manuva","last played":"2011-10-31 01:16:31 +0000"},{"song count":"58","name":"Green Day","last played":"(null)"},{"song count":"23","name":"Grizzly Bear","last played":"(null)"},{"song count":"12","name":"Guns N' Roses","last played":"(null)"},{"song count":"1","name":"Guster","last played":"(null)"},{"song count":"14","name":"The Gutter Puppies","last played":"(null)"},{"song count":"1","name":"Harry Partch","last played":"2011-11-24 01:08:24 +0000"},{"song count":"10","name":"Harvey Danger","last played":"(null)"},{"song count":"1","name":"The Head","last played":"(null)"},{"song count":"5","name":"The Heights Mafia","last played":"(null)"},{"song count":"6","name":"Henry Terrell","last played":"(null)"},{"song count":"1","name":"The Horrible Crowes","last played":"2011-11-24 00:51:18 +0000"},{"song count":"1","name":"Howlin' Wolf","last played":"2011-11-24 01:05:35 +0000"},{"song count":"1","name":"Iceage","last played":"(null)"},{"song count":"22","name":"In Denmark","last played":"(null)"},{"song count":"61","name":"Incubus","last played":"(null)"},{"song count":"12","name":"Infected Mushroom","last played":"(null)"},{"song count":"1","name":"Ingrid Michaelson","last played":"(null)"},{"song count":"13","name":"Interpol","last played":"(null)"},{"song count":"19","name":"J Dilla","last played":"(null)"},{"song count":"1","name":"Jack Kerouac","last played":"2011-11-24 00:54:41 +0000"},{"song count":"13","name":"Jay-Z","last played":"(null)"},{"song count":"16","name":"Jeff Beck","last played":"(null)"},{"song count":"1","name":"Jesca Hoop","last played":"2011-11-24 01:20:31 +0000"},{"song count":"15","name":"Jet","last played":"(null)"},{"song count":"10","name":"Jethro Tull","last played":"(null)"},{"song count":"12","name":"Jimi Hendrix","last played":"(null)"},{"song count":"25","name":"Jimmie's Chicken Shack","last played":"(null)"},{"song count":"11","name":"Jimmy Eat World","last played":"(null)"},{"song count":"1","name":"John Brim","last played":"2011-11-24 01:16:15 +0000"},{"song count":"1","name":"Johnny Dowd","last played":"(null)"},{"song count":"1","name":"The Joy Formidable","last played":"2011-10-27 03:05:30 +0000"},{"song count":"1","name":"Jully Black/Nas","last played":"(null)"},{"song count":"27","name":"Justin Timberlake","last played":"(null)"},{"song count":"1","name":"Kalae All Day & SciryL Cooper","last played":"(null)"},{"song count":"13","name":"Kanye West","last played":"(null)"},{"song count":"24","name":"Keith Jarrett","last played":"(null)"},{"song count":"1","name":"Kelis/OutKast","last played":"(null)"},{"song count":"1","name":"Kenny Rogers & The First Edition","last played":"(null)"},{"song count":"53","name":"Kid Cudi","last played":"(null)"},{"song count":"5","name":"King Crimson","last played":"(null)"},{"song count":"1","name":"King Kayvan","last played":"(null)"},{"song count":"11","name":"Kings Of Leon","last played":"(null)"},{"song count":"1","name":"KRS-One & Marley Marl","last played":"(null)"},{"song count":"21","name":"Kruder & Dorfmeister","last played":"(null)"},{"song count":"16","name":"Kyuss","last played":"(null)"},{"song count":"1","name":"Lake/Nas","last played":"2011-09-13 07:27:19 +0000"},{"song count":"9","name":"LCD Soundsystem","last played":"(null)"},{"song count":"24","name":"Led Zeppelin","last played":"(null)"},{"song count":"1","name":"Leela James","last played":"(null)"},{"song count":"1","name":"Liam Lynch","last played":"(null)"},{"song count":"31","name":"Lightning Bolt","last played":"(null)"},{"song count":"1","name":"Lil Troy","last played":"(null)"},{"song count":"29","name":"Lil Wayne","last played":"(null)"},{"song count":"1","name":"Lil' Fate/Ludacris/Shawnna","last played":"(null)"},{"song count":"1","name":"Lil' Flip/Ludacris","last played":"(null)"},{"song count":"10","name":"Limp Bizkit","last played":"(null)"},{"song count":"45","name":"Linkin Park","last played":"(null)"},{"song count":"12","name":"Lit","last played":"(null)"},{"song count":"1","name":"Little Dragon","last played":"(null)"},{"song count":"40","name":"Live","last played":"(null)"},{"song count":"1","name":"Lost Prophets","last played":"(null)"},{"song count":"10","name":"Lou Reed","last played":"(null)"},{"song count":"1","name":"The Low Anthem","last played":"(null)"},{"song count":"43","name":"Ludacris","last played":"(null)"},{"song count":"1","name":"Ludacris/Shawnna","last played":"(null)"},{"song count":"1","name":"Ludacris/Snoop Dogg","last played":"(null)"},{"song count":"2","name":"Ludwig van Beethoven (1770-182","last played":"(null)"},{"song count":"35","name":"Lupe Fiasco","last played":"2011-07-21 01:55:50 +0000"},{"song count":"1","name":"M83","last played":"2011-10-27 02:43:23 +0000"},{"song count":"1","name":"The Mamas & the Papas","last played":"2011-07-21 02:39:55 +0000"},{"song count":"1","name":"Man Man","last played":"2011-11-24 00:47:43 +0000"},{"song count":"12","name":"Marcy Playground","last played":"(null)"},{"song count":"6","name":"Martin Solveig","last played":"(null)"},{"song count":"1","name":"Martin Solveig vs. Ruffneck","last played":"(null)"},{"song count":"31","name":"Massive Attack","last played":"2011-09-24 06:00:00 +0000"},{"song count":"8","name":"Massive Attack Vs. Mad Professor","last played":"2011-09-27 01:21:57 +0000"},{"song count":"25","name":"Matchbox Twenty","last played":"(null)"},{"song count":"1","name":"Meek Mill","last played":"(null)"},{"song count":"10","name":"MGMT","last played":"2011-07-21 03:22:18 +0000"},{"song count":"24","name":"The Mighty Mighty Bosstones","last played":"2011-07-21 03:49:06 +0000"},{"song count":"11","name":"Miguel Zenón","last played":"(null)"},{"song count":"1","name":"Mikkhiel","last played":"2011-10-20 07:57:25 +0000"},{"song count":"7","name":"Miles Davis","last played":"(null)"},{"song count":"69","name":"Modest Mouse","last played":"2011-07-21 09:49:10 +0000"},{"song count":"14","name":"Mondo Generator","last played":"(null)"},{"song count":"12","name":"Morcheeba","last played":"(null)"},{"song count":"14","name":"Mozart","last played":"2011-10-31 00:06:31 +0000"},{"song count":"53","name":"Mr. A.L.I.","last played":"(null)"},{"song count":"1","name":"Mr. A.L.I. Feat Carla Prather","last played":"(null)"},{"song count":"1","name":"Mr. A.L.I.'s Electronic Jam","last played":"(null)"},{"song count":"4","name":"Mr. A.L.I.'s J.A.M. Sessions","last played":"(null)"},{"song count":"3","name":"Mr. A.L.I.'s J.A.M. Sessions feat Carla Prather","last played":"(null)"},{"song count":"1","name":"Mr. Ali","last played":"(null)"},{"song count":"20","name":"Mr. Bungle","last played":"(null)"},{"song count":"1","name":"Mr. Meeble","last played":"2011-09-10 05:22:09 +0000"},{"song count":"1","name":"Mr. Scruff","last played":"2011-08-31 00:47:39 +0000"},{"song count":"1","name":"Mugison","last played":"2011-10-27 00:18:36 +0000"},{"song count":"11","name":"Múm","last played":"2011-08-31 00:58:40 +0000"},{"song count":"10","name":"Muse","last played":"(null)"},{"song count":"11","name":"My Bloody Valentine","last played":"(null)"},{"song count":"17","name":"N.W.A","last played":"(null)"},{"song count":"67","name":"Nas","last played":"2011-06-28 23:15:23 +0000"},{"song count":"29","name":"Neutral Milk Hotel","last played":"(null)"},{"song count":"95","name":"Nine Inch Nails","last played":"(null)"},{"song count":"85","name":"Nirvana","last played":"(null)"},{"song count":"1","name":"Norah Jones/OutKast","last played":"(null)"},{"song count":"13","name":"Oasis","last played":"(null)"},{"song count":"1","name":"Off By One","last played":"(null)"},{"song count":"13","name":"The Offspring","last played":"(null)"},{"song count":"9","name":"Oingo Boingo","last played":"(null)"},{"song count":"23","name":"Oleander","last played":"(null)"},{"song count":"1","name":"Oliver Koletzki & Fran","last played":"2011-10-27 03:02:07 +0000"},{"song count":"14","name":"Opeth","last played":"(null)"},{"song count":"12","name":"Orgy","last played":"(null)"},{"song count":"40","name":"Outkast","last played":"(null)"},{"song count":"1","name":"OutKast/Rosario Dawson","last played":"(null)"},{"song count":"15","name":"P.O.D.","last played":"(null)"},{"song count":"83","name":"Papa Roach","last played":"(null)"},{"song count":"3","name":"Papa Roach - [EMG]","last played":"(null)"},{"song count":"37","name":"Pavement","last played":"(null)"},{"song count":"1","name":"Pearl Jam","last played":"(null)"},{"song count":"13","name":"A Perfect Circle","last played":"(null)"},{"song count":"1","name":"Peter Murphy","last played":"(null)"},{"song count":"8","name":"Peter Schilling","last played":"(null)"},{"song count":"1","name":"Pharoahe Monch","last played":"(null)"},{"song count":"14","name":"Philip Glass","last played":"(null)"},{"song count":"63","name":"Pink Floyd","last played":"(null)"},{"song count":"95","name":"Pixies","last played":"(null)"},{"song count":"33","name":"Placebo","last played":"2011-10-13 05:14:24 +0000"},{"song count":"24","name":"Portishead","last played":"(null)"},{"song count":"1","name":"Portugal. The Man","last played":"(null)"},{"song count":"13","name":"Powerman 5000","last played":"(null)"},{"song count":"29","name":"Primus","last played":"(null)"},{"song count":"1","name":"Pure X","last played":"(null)"},{"song count":"50","name":"Queens Of The Stone Age","last played":"2011-10-13 05:24:24 +0000"},{"song count":"25","name":"Radiohead","last played":"2011-07-23 01:51:19 +0000"},{"song count":"14","name":"Rage Against the Machine","last played":"(null)"},{"song count":"1","name":"Random Axe","last played":"(null)"},{"song count":"16","name":"Rise Against","last played":"2011-07-27 02:54:14 +0000"},{"song count":"1","name":"Shad","last played":"(null)"},{"song count":"1","name":"Skylar Grey","last played":"(null)"},{"song count":"1","name":"Sleeper Agent","last played":"(null)"},{"song count":"1","name":"Slimkat 78","last played":"(null)"},{"song count":"1","name":"Smif-n-Wessun","last played":"(null)"},{"song count":"1","name":"Soulsearcher","last played":"2011-10-27 02:48:05 +0000"},{"song count":"1","name":"Southside Johnny With LaBamba's Big Band","last played":"2011-11-24 00:59:01 +0000"},{"song count":"21","name":"Spoon","last played":"2011-09-29 02:16:12 +0000"},{"song count":"19","name":"STiRFRY","last played":"2011-11-16 07:13:05 +0000"},{"song count":"12","name":"Stone Temple Pilots","last played":"2011-11-16 07:31:53 +0000"},{"song count":"21","name":"Sublime","last played":"(null)"},{"song count":"24","name":"Sugarcult","last played":"2011-11-18 06:26:29 +0000"},{"song count":"1","name":"Summer Camp","last played":"(null)"},{"song count":"14","name":"System of a Down","last played":"(null)"},{"song count":"1","name":"Talib Kweli","last played":"(null)"},{"song count":"13","name":"Them Crooked Vultures","last played":"(null)"},{"song count":"1","name":"Theophilus London","last played":"2011-10-27 00:14:40 +0000"},{"song count":"40","name":"Third Eye Blind","last played":"(null)"},{"song count":"12","name":"Three Days Grace","last played":"(null)"},{"song count":"63","name":"Tom Waits","last played":"(null)"},{"song count":"46","name":"Tool","last played":"(null)"},{"song count":"11","name":"Trakan","last played":"(null)"},{"song count":"11","name":"Trapt","last played":"(null)"},{"song count":"28","name":"A Tribe Called Quest","last played":"(null)"},{"song count":"1","name":"Unknown Mortal Orchestra","last played":"(null)"},{"song count":"33","name":"Weezer","last played":"2011-07-21 22:15:17 +0000"},{"song count":"1","name":"White Denim","last played":"(null)"},{"song count":"16","name":"The White Stripes","last played":"2011-06-28 23:45:48 +0000"},{"song count":"32","name":"The Who","last played":"(null)"},{"song count":"1","name":"William Elliott Whitmore","last played":"2011-11-24 01:13:30 +0000"},{"song count":"12","name":"Wu-Tang Clan","last played":"(null)"},{"song count":"11","name":"The xx","last played":"(null)"},{"song count":"3","name":"2 Pac","last played":"(null)"},{"song count":"35","name":"2Pac","last played":"(null)"},{"song count":"1","name":"2Pac/J. Phoenix/Nas","last played":"2011-09-13 07:15:00 +0000"},{"song count":"23","name":"3 Doors Down","last played":"(null)"},{"song count":"1","name":"8 Ball/Carl Thomas/Ludacris/MJG","last played":"(null)"},{"song count":"12","name":"311","last played":"(null)"}],"favorites":["Blondie","Shifty Johnson & Terry Swank","UNKLE","Wagon Christ","Andy Dick and the Bitches of the Century","múm","Bryan Ford","Soundgarden","The Mighty Mighty Bosstones","Lady Gaga","Sonic Youth","Dr. Dre","Nas","Miles Davis","Adema","Seven Mary Three","Beyoncé","The Presidents of the United States of America","Skrillex","Pixies","A Tribe Called Quest","ジャパハリネット","Portishead","The Toasters","Deadmau5","Incubus","Nirvana","Catch 22","サンボマスター","Massive Attack","Kruder & Dorfmeister","Rilo Kiley","Happy End","Jenna Jameson","Parliament","The Offspring","ガガガSP","Cake","東京スカパラダイスオーケストラ","The Residents","Stone Temple Pilots","Red Hot Chili Peppers","The Notorious B.I.G.","Thelonious Monk","Primus","Talking Heads","Aphex Twin","Wu-Tang Clan","A Perfect Circle","The Cure","Cold War Kids","At the Drive-In","Thievery Corporation","Chronic Future","La Roux","Roy Ayers","Slick Rick","Bloc Party"]}
json_works = json.dumps(json_works)
h = httplib2.Http()

resp, content = h.request('http://localhost:8080/v2/home?user=bradstestudid&fbauth=AAACWxMASSIcBAGyxJOersM9vnhy4ZAxgakzmN23WLIGBdz2CrAvjZAM5qGGtZAWFhXFqjWjNLoD4ZCpzPomLRNGouqmDF9YZD', 
        'POST', 
        json_works ,
        headers={'Content-Type': 'application/json'})


print content
