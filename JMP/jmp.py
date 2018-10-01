#!/usr/bin/python
# -*- coding: utf-8 -*-
#JMP:xpolan07
import re;
import getopt, sys;
from sys import stdin

# TRIDA PRO PRAMETRY
class Par_info:
	def __init__(self):
		self.jmeno = "";
		self.misto = 0;
	
# TRIDA PRO MAKRA
class V_info:
	def __init__(self):
		
		self.jmeno = "";
		self.parametr = [];
		self.metoda = "";
		self.p_par = 0;
		self.pocet_nacteni = 0;
		self.original = 0;

# JEDNOTLIVE IDENTIFIKATORY
class identifikatory:
	def __init__(self):
		self.is_jmeno = 0; # JEDNA SE O JMENO
		self.is_makro = 0; # JEDNA SE O MAKRO
		self.is_parametr = 0; # JEDNA SE O PARAMETR
		self.is_definice = 0; # DEFINICE
		self.is_metoda = 0; # METODA
		self.blok = 0; # BLOK
		self.is_cancel = 0; # UNDEF
		self.pocet_L = 0; # POCET {
		self.pocet_P = 0; # POCET }
		self.white = 0; # SET WHITESPACE
		
# FUNKCE PRO TISK NAPOVEDY		
def napoveda():
	print("Projekt JMP: Jednoduchy makroprocesor");
	print("Vypracoval: Petr Polanský");
	print("Login: xpolan07");
	print("Popis: projekt nahrazuje makra v textu.");
	print("\tMakra jsou nahrazena telem makra po dosazeni"
		  " parametru.");
	print("--help : vypise napovedu, musi byt zadan samostatne");
	print("--input=filename : jmeno souboru, ze ktereho se ma cist");
	print("\t\tPokud neni tento parametr zadan, ocekava se text ze stdin.");
	print("--output=filename : jmeno souboru, do ktereho se bude zapisovat");
	print("\t\tPokud neni tento parametr zadan, vystup je smerovan na stdout.");
	print("--cmd=text : text bude zapsan pred text vstupniho souboru.");
	print("-r : redefinice jiz definovaneho makra bude brana jako chyba");

# VYHLEDANI A EXPANZE MAKRA
def nalezeni(prvni,druhy,tabulka_maker,metoda,ident,redefinice):
	
	nalezeno = 0;
	for polozka_t in tabulka_maker:		
		if prvni.jmeno == polozka_t.jmeno:
			nalezeno = 1;
			if polozka_t.p_par == druhy.pocet_nacteni: # provedeme dosazeni
				metoda = polozka_t.metoda;
				for s in druhy.parametr:
					
					for ve in polozka_t.parametr:
						if ve.misto == s.misto :
							
							metoda = expanze(metoda,ve.jmeno,s.jmeno);
												
				ident.is_parametr = 0;
				ident.pocet_L = 0;
				ident.pocet_P = 0;
				jmeno = "";
				druhy = V_info();
				#print("TTocet sedi");

			else:
				ident.is_parametr = 1;
	if nalezeno == 0:
		sys.stderr.write("chyba takove makro neexistuje.\n");
		sys.exit(56);
	return prvni,druhy,tabulka_maker,metoda ,ident;						

# ZRUSENI MAKRA Z TABULKY MAKER
def undef(jmeno,tabulka_maker):
	jmeno = jmeno.replace("@","");
	nalezeno = 0;
	for x in tabulka_maker:
		if x.jmeno == jmeno:
			
			nalezeno = 1;
			tabulka_maker.remove(x);

	if nalezeno == 0:
		sys.stderr.write("chyba makro neexistuje\n");
		sys.exit(56);
	return tabulka_maker;		

# VLOZENI VESTAVENYCH MAKER
def pred_def(tabulka_maker):
	prvni = V_info();
	prvni.jmeno = "def";
	prvni.original = 1;
	tabulka_maker.append(prvni);

	prvni = V_info();
	prvni.jmeno = "__def__";
	prvni.original = 1;
	tabulka_maker.append(prvni);

	prvni = V_info();
	prvni.jmeno = "undef";
	prvni.original = 1;
	tabulka_maker.append(prvni);

	prvni = V_info();
	prvni.jmeno = "__undef__";
	prvni.original = 1;
	tabulka_maker.append(prvni);

	prvni = V_info();
	prvni.jmeno = "set";
	prvni.original = 1;
	tabulka_maker.append(prvni);

	prvni = V_info();
	prvni.jmeno = "__set__";
	prvni.original = 1;
	tabulka_maker.append(prvni);

	return tabulka_maker;

# ZPRACOVANI SAMOSTATNEHO BLOKU VCETNE MAKER
def zprac_blok(blok):
	pro_tisk = "";
	is_makro = 0;
	
	for txt in blok:
		if txt == '@' and is_makro == 0 : # pozname makro
			is_makro = 1;			
			continue;
	
		if is_makro == 1 : # zpracujeme makro
			if txt == '@':
				pro_tisk += "@";
				is_makro = 0;
				continue;

			elif txt == '{':
				pro_tisk += "{";
				is_makro = 0;
				continue;

			elif txt == '}':
				pro_tisk += "}";
				is_makro = 0;
				continue;

			else: # jmeno makra
				pro_tisk += "@";
				pro_tisk += txt;
				is_makro = 0;
				continue;
		else:
			pro_tisk += txt;

	return pro_tisk;

# PROHLEDANI A DOSAZENI PARAMETRU
def expanze(metoda,defin,volan):
	par = 0;
	dalsi = "";
	kopirovaci = "";
	regex = re.compile("\$[a-zA-Z][a-zA-Z0-9_]*$");
	param = Par_info();
	for txt in metoda:
		
		if txt == "$":
			if par == 1:
				if param.jmeno == defin:
					kopirovaci += volan;
				else:
					kopirovaci += param.jmeno;
																
				param.jmeno = "";
				dalsi = "";
			par = 1;
			param.jmeno += txt;
			dalsi += txt;
			
			continue;

		if par == 1:
			dalsi += txt;
			p = regex.match(dalsi);
			if not p: # jmeno ulozime											
				if param.jmeno == defin:
					kopirovaci += volan;
				else:
					kopirovaci += param.jmeno;
				kopirovaci += txt;											
				param.jmeno = "";
				dalsi = "";
				par = 0;
			
			else:
				param.jmeno += txt;										
		else:
			kopirovaci += txt;

	p = regex.match(dalsi);
	
	if not p:
		par = 1;
		kopirovaci += dalsi;
	else:
		
		if param.jmeno == defin:
			kopirovaci += volan;
			
		else:
			kopirovaci += param.jmeno;

	metoda = kopirovaci;

	return metoda;	

# HLAVNI FUNKCE PRO ZPRACOVANI VSTUPU
def zpracovani(text, pro_tisk, tabulka_maker,redefinice):
	pro_tisk = "";
	do_bloku = "";
	jmeno = "";
	
	nalezeno = 0;
	
	dalsi = "";
	prvni = V_info();
	druhy = V_info();
	ident = identifikatory();
	par = Par_info();
	regex = re.compile("\$[a-zA-Z_][a-zA-Z0-9_]*$");
	correct_name = re.compile("^[a-zA-Z_][a-zA-Z0-9_]*$");
	correct_par = re.compile("@[a-zA-Z_][a-zA-Z0-9_]*$");
	delka = len(text);
	i = -1;
	while i < delka:
		i += 1;
		
		if i == len(text): # POKUD JE TO POSLEDNI ZNAK => KONEC
			break;

		pomer = delka - i; # INFORMACE O POCTU ZBYVAJICICH ZNAKU NA VSTUPU
		
		white = 0;
		
		# OSETRENI KDY POSLEDNI ZNAKY JSOU ZAVORKY
		if pomer == 1:
			if text[i] == "{": 
				sys.stderr.write("chyba, pocet zavorek neni stejny\n");
				sys.exit(55);

			if text[i] == "}" and ident.pocet_L == ident.pocet_P:
				sys.stderr.write("chyba, , pocet zavorek neni stejny\n");
				sys.exit(55);

		# IDENTIFIKATOR PRO PRESKAKOVANI BILYCH ZNAKU
		if ident.white == 1 and ident.blok == 0:
			if text[i].isspace():
				white = 1;	
		
		# POKUD JE NA VSTUPU JMENO
		if ident.is_jmeno == 1: # na vstupu mame nazev makra
			# JEDNA SE O PARAMETR
			if ident.is_parametr == 1: # jmeno makra na vstupu je parametr
				dalsi = "";
				dalsi = par.jmeno;
				dalsi += text[i];

				p = correct_par.match(dalsi); # overime ze je spravna syntaxe
				
				# ZNAK JIZ NEVYHOVUJE PARAMETRU MAKRA
				if (not p or text[i].isspace() == True) and ident.is_definice == 0  and white == 0:
					
					if jmeno == "undef" or jmeno == "__undef__":
						for x in tabulka_maker:
							if x.jmeno == jmeno:
								if x.original == 1:
									
									tabulka_maker = undef(par.jmeno,tabulka_maker);
									
									ident.is_cancel = 0;
									par = Par_info();
									jmeno = "";
									ident.is_jmeno = 0;
									ident.is_parametr = 0;
									ident.is_definice = 0;
									ident.is_makro = 0;			

					else:

						ident.is_jmeno = 0;
						ident.is_parametr = 0;
						ident.is_definice = 0;
						ident.is_makro = 0;
												
						druhy.pocet_nacteni += 1;
						par.misto +=1;
						par.jmeno += text[i];

						para = par.misto;
						druhy.parametr.append(par);
						
						par = Par_info(); # vynulujeme parametry
						par.misto = para;
						
						metoda = "";

						prvni, druhy, tabulka_maker, metoda, ident = nalezeni(prvni, druhy, tabulka_maker, metoda ,ident,redefinice);			
						
						if ident.is_parametr == 0:							
							text = metoda + text[i:];
							i = -1;
							delka = len(text);
							jmeno = "";
							ident.is_jmeno = 0;
							ident.is_makro = 0;
						
							par = Par_info();
						
						if ident.is_parametr == 0:
							jmeno = "";
							par = Par_info();
						continue; # POZOR NEBEZPECI
				else:
					
					if white == 1:
						prvni.jmeno = jmeno;
						if (jmeno == "def" or jmeno == "__def__") and ident.is_definice == 0:
							for x in tabulka_maker:
								if x.jmeno == jmeno:
									if x.original == 1:
										if par.jmeno == "@__undef__" or par.jmeno == "@__set__" or par.jmeno == "@__def__":
											sys.stderr.write("chyba makro nelze zrusit\n");
											sys.exit(57);
											
										ident.is_definice = 1;
										ident.is_makro = 0;
										jmeno = "";
								
									else:
										prvni.jmeno = jmeno;
										if ident.is_definice == 0:
											for x in tabulka_maker:
												if x.jmeno == jmeno:
													if x.p_par == 0: # proste vypise metodu

														text = x.metoda + text[i:];
														i = -1;
														delka = len(text);
														jmeno = "";
														ident.is_jmeno = 0;
														ident.is_makro = 0;
														dalsi = "";
													else:
														ident.is_parametr = 1;# TADY

														par.jmeno += text[i];

														ident.is_makro = 0;
														ident.is_jmeno = 0;	
											continue; # POZOR NEBEZPECI			
						
						elif (jmeno == "undef" or jmeno == "__undef__"):
							for x in tabulka_maker:
								if x.jmeno == jmeno:
									if x.original == 1:
										if par.jmeno == "@__undef__" or par.jmeno == "@__set__" or par.jmeno == "@__def__":
											sys.stderr.write("chyba makro nelze zrusit\n");
											sys.exit(57);
										
										ident.is_cancel = 1;
										ident.is_parametr = 1;
										ident.is_jmeno = 0;			
										ident.is_makro = 0;
										par.jmeno += text[i];
	

									else:
										prvni.jmeno = jmeno;
										if ident.is_definice == 0:
											for x in tabulka_maker:
												if x.jmeno == jmeno:
													if x.p_par == 0: # proste vypise metodu

														text = x.metoda + text[i:];
														i = -1;
														delka = len(text);
														jmeno = "";
														ident.is_jmeno = 0;
														ident.is_makro = 0;
														dalsi = "";
													else:
														ident.is_parametr = 1;# TADY
														par.jmeno += text[i];
														ident.is_makro = 0;
														ident.is_jmeno = 0;
											continue; # POZOR NEBEZPECI			

						elif jmeno == "set" or jmeno == "__set__":
							
							ident.is_parametr = 1;
							ident.is_jmeno = 0;
							ident.is_makro = 0;
							

						else:
							p = correct_name.match(jmeno); # overime ze je spravna syntaxe
							if not p:
								
								sys.stderr.write("spatny format jmena makra\n");		
								sys.exit(55);
								# KONEC
							else:
								#print(jmeno);
								prvni.jmeno = jmeno;
								if ident.is_definice == 0:
									for x in tabulka_maker:
										if x.jmeno == jmeno:
											if x.p_par == 0: # proste vypise metodu
												text = x.metoda + text[i:];
												i = -1;
												delka = len(text);
												jmeno = "";
												ident.is_jmeno = 0;
												ident.is_makro = 0;
												dalsi = "";
											else:
												ident.is_parametr = 1;# TADY
												par.jmeno += text[i];
												
												ident.is_makro = 0;
												ident.is_jmeno = 0;																																			
									continue; # POZOR NEBEZPECI


			if text[i] == "{" and ident.is_jmeno == 1: # muze to byt jedine parametr pri volani, porovname zda makro existuje

				p = correct_name.match(jmeno); # overime ze je spravna syntaxe
				if not p and ident.is_definice == 0:
					sys.stderr.write("spatny format jmena makra\n");
					sys.exit(55);		
					# KONEC
				else:
					prvni.jmeno = jmeno;
					
					if ident.is_definice == 0: # nejedna se o definici
						for x in tabulka_maker:
							if x.jmeno == jmeno:
								if jmeno == "undef" or jmeno == "__undef__":
									ident.is_cancel = 1;
									ident.is_parametr = 1;
									ident.is_jmeno = 0;
									ident.is_makro = 0;
									ident.blok = 1;
									continue;

								if jmeno == "set" or jmeno == "__set__":									
									
									ident.is_parametr = 1;
									ident.is_jmeno = 0;
									ident.is_makro = 0;
									ident.blok = 1;
									ident.pocet_L += 1;
									break;	

								if x.p_par == 0: # proste vypise metodu

									text = x.metoda + text[i:];
									
									i = -1;
									delka = len(text);
									jmeno = "";
									ident.is_jmeno = 0;
									ident.is_makro = 0;
									dalsi = "";
								else:
									
									ident.is_parametr = 1;# TADY
									ident.blok = 1;
									ident.pocet_L += 1;
									#print("JOP");
									ident.is_makro = 0;
									ident.is_jmeno = 0;
						continue; # POZOR NEBEZPECI

					else:	# rozdeleny podminky														
						jmeno = "";
						
						ident.is_jmeno = 0;
						ident.is_makro = 0;
				
					
			elif text[i] == "@" and ident.is_jmeno == 1: # pokud to neni definice, je to parametr
				ident.is_jmeno = 0;
				prvni.jmeno = jmeno;
				
				if (jmeno == "def" or jmeno == "__def__") and ident.is_definice == 0:				
					if ident.is_definice == 0:						
						for x in tabulka_maker:
							if x.jmeno == jmeno:
								if x.original == 1:
									if par.jmeno == "@__undef__" or par.jmeno == "@__set__" or par.jmeno == "@__def__":
											sys.stderr.write("chyba makro nelze zrusit\n");
											sys.exit(57);
											
									ident.is_definice = 1;
									ident.is_makro = 0;

									jmeno = "";
								
								else:
									prvni.jmeno = jmeno;
									if ident.is_definice == 0:
										for x in tabulka_maker:
											if x.jmeno == jmeno:
												if x.p_par == 0: # proste vypise metodu

													text = x.metoda + text[i:];
													i = -1;
													delka = len(text);
													jmeno = "";
													ident.is_jmeno = 0;
													ident.is_makro = 0;
													dalsi = "";
												else:
													ident.is_parametr = 1;# TADY

													par.jmeno += text[i];

													ident.is_makro = 0;
													ident.is_jmeno = 0;
										continue; # POZOR NEBEZPECI			
					else:						
						jmeno = "";
				
				elif (jmeno == "undef" or jmeno == "__undef__"):
					
					for x in tabulka_maker:
						if x.jmeno == jmeno:
							if x.original == 1:
								if par.jmeno == "@__undef__" or par.jmeno == "@__set__" or par.jmeno == "@__def__":
											sys.stderr.write("chyba makro nelze zrusit\n");
											sys.exit(57);
								
								ident.is_cancel = 1;
								ident.is_parametr = 1;
								ident.is_jmeno = 0;			
								ident.is_makro = 0;

								par.jmeno += text[i];	

							else:
								prvni.jmeno = jmeno;
								if ident.is_definice == 0:
									for x in tabulka_maker:
										if x.jmeno == jmeno:
											if x.p_par == 0: # proste vypise metodu
												text = x.metoda + text[i:];
												i = -1;
												delka = len(text);
												jmeno = "";
												ident.is_jmeno = 0;
												ident.is_makro = 0;
												dalsi = "";
											else:
												ident.is_parametr = 1;# TADY
												par.jmeno += text[i];
												ident.is_makro = 0;
												ident.is_jmeno = 0;

									continue; # POZOR NEBEZPECI
				
				elif jmeno == "set" or jmeno == "__set__":
					sys.stderr.write("spatny parametr set\n");
					sys.exit(56);
					# KONEC:

				else:
					p = correct_name.match(jmeno); # overime ze je spravna syntaxe
					if not p:
						#print(ident.is_definice);
						sys.stderr.write("spatny format jmena makra\n");
						sys.exit(55);		
						# KONEC
					else:
						prvni.jmeno = jmeno;
						if ident.is_definice == 0:
							for x in tabulka_maker:
								if x.jmeno == jmeno:
									if x.p_par == 0: # proste vypise metodu
										

										text = x.metoda + text[i:];
										i = -1;
										delka = len(text);
										jmeno = "";
										ident.is_jmeno = 0;
										ident.is_makro = 0;
										dalsi = "";
								
									else:
										ident.is_parametr = 1;# TADY
										par.jmeno += text[i];
										#blok = 1;
										#print("JOP");
										ident.is_makro = 0;
										ident.is_jmeno = 0;
							continue; # POZOR NEBEZPECI								
				

			elif text[i] != "@" and text[i] != "{" and text[i] != "_" and text[i].isalpha() == False and text[i].isdigit() == False and white == 0: # jiny znak, mel by byt bran jako parametr
				ident.is_jmeno = 0;
				ident.is_makro = 0;
				dalsi = "";
				dalsi = jmeno;
				dalsi += text[i];
				
				if jmeno == "undef" or jmeno == "__undef__":
					sys.stderr.write("spatny parametr undef\n");
					# KONEC
				elif jmeno == "set" or jmeno == "__set__":
					sys.stderr.write("spatny parametr set\n");
					# KONEC:

				p = correct_name.match(dalsi); # overime ze je spravna syntaxe
				if not p or text[i].isspace() == True:
					
					prvni.jmeno = jmeno;
					if ident.is_definice == 0: # nejedna se o definici
						
						for x in tabulka_maker:
							if x.jmeno == jmeno:
								if x.p_par == 0: # proste vypise metodu
									
									text = x.metoda + text[i:];
									i = -1;
									delka = len(text);
									
									jmeno = "";
									ident.is_jmeno = 0;
									ident.is_makro = 0;
									dalsi = "";
									

								else:
									ident.is_parametr = 1;# TADY
									pomer = delka - i;
									metoda = "";
									
									par.jmeno += text[i];
									#print(text[i]);
									druhy.pocet_nacteni += 1;
									par.misto +=1;
									para = par.misto;
									druhy.parametr.append(par);
									par = Par_info(); # vynulujeme parametry
									par.misto = para;
									
									prvni, druhy, tabulka_maker, metoda, ident = nalezeni(prvni, druhy, tabulka_maker, metoda ,ident,redefinice);			
									if ident.is_parametr == 0:
										
										text = metoda + text[i:];
										i = -1;
										delka = len(text);
										jmeno = "";
										ident.is_jmeno = 0;
										ident.is_makro = 0;
										dalsi = "";
										par = Par_info();
										continue;
									if pomer == 1:

										if jmeno == "undef" or jmeno == "__undef__":
											for x in tabulka_maker:
												if x.jmeno == jmeno:
													if x.original == 1:
														#print("JOddP");
														if par.jmeno == "@__undef__" or par.jmeno == "@__set__" or par.jmeno == "@__def__":
															sys.stderr.write("chyba makro nelze zrusit\n");
															sys.exit(57);

														
														tabulka_maker = undef(par.jmeno,tabulka_maker);
														
														ident.is_cancel = 0;
														par= Par_info();
														jmeno = "";
														ident.is_jmeno = 0;
														ident.is_parametr = 0;
														ident.is_definice = 0;
														ident.is_makro = 0;		
										
										druhy.pocet_nacteni += 1;
										par.misto +=1;
										para = par.misto;
										druhy.parametr.append(par);
										par = Par_info(); # vynulujeme parametry
										par.misto = para;

										for x in tabulka_maker:
											if x.jmeno == jmeno:
												
												metoda = "";
												prvni, druhy, tabulka_maker, metoda, ident = nalezeni(prvni, druhy, tabulka_maker, metoda ,ident,redefinice);			
												text = metoda + text[i:];
												i = -1;
												delka = len(text);
												jmeno = "";
												ident.is_jmeno = 0;
												ident.is_makro = 0;
												dalsi = "";
										
						continue; # POZOR NEBEZPECI
				else:

					dalsi = "";
					jmeno = "";
					ident.is_jmeno = 0;
					ident.is_makro = 0;
			
			elif white == 1:				
				prvni.jmeno = jmeno;
				

				if (jmeno == "def" or jmeno == "__def__") and ident.is_definice == 0:
					for x in tabulka_maker:
						if x.jmeno == jmeno:
							if x.original == 1:
								if par.jmeno == "@__undef__" or par.jmeno == "@__set__" or par.jmeno == "@__def__":
									sys.stderr.write("chyba makro nelze zrusit\n");
									sys.exit(57);
											
								ident.is_definice = 1;
								ident.is_makro = 0;

								jmeno = "";
								
							else:
								prvni.jmeno = jmeno;
								if ident.is_definice == 0:
									for x in tabulka_maker:
										if x.jmeno == jmeno:
											if x.p_par == 0: # proste vypise metodu
												text = x.metoda + text[i:];
												i = -1;
												delka = len(text);
												jmeno = "";
												ident.is_jmeno = 0;
												ident.is_makro = 0;
												dalsi = "";
											else:
												ident.is_parametr = 1;# TADY
												par.jmeno += text[i];
												ident.is_makro = 0;
												ident.is_jmeno = 0;	
									continue; # POZOR NEBEZPECI

				elif (jmeno == "undef" or jmeno == "__undef__"):
					for x in tabulka_maker:
						if x.jmeno == jmeno:
							if x.original == 1:
								if par.jmeno == "@__undef__" or par.jmeno == "@__set__" or par.jmeno == "@__def__":
									sys.stderr.write("chyba makro nelze zrusit\n");
									sys.exit(57);
										
								ident.is_cancel = 1;
								ident.is_parametr = 1;
								ident.is_jmeno = 0;			
								ident.is_makro = 0;
								par.jmeno += text[i];
	

							else:
								prvni.jmeno = jmeno;
								if ident.is_definice == 0:
									for x in tabulka_maker:
										if x.jmeno == jmeno:
											if x.p_par == 0: # proste vypise metodu
												text = x.metoda + text[i:];
												i = -1;
												delka = len(text);
												jmeno = "";
												ident.is_jmeno = 0;
												ident.is_makro = 0;
												dalsi = "";
											else:
												ident.is_parametr = 1;# TADY
												par.jmeno += text[i];
												ident.is_makro = 0;
												ident.is_jmeno = 0;
									continue; # POZOR NEBEZPECI
				elif jmeno == "set" or jmeno == "__set__":
					
					ident.is_parametr = 1;
					ident.is_jmeno = 0;
					ident.is_makro = 0;
					

				else:
					p = correct_name.match(jmeno); # overime ze je spravna syntaxe
					if not p:
						
						sys.stderr.write("spatny format jmena makra\n");	
						sys.exit(55);	
						
					else:

						prvni.jmeno = jmeno;
						if ident.is_definice == 0:
							for x in tabulka_maker:
								if x.jmeno == jmeno:
									if x.p_par == 0: # proste vypise metodu
										
										
										text = x.metoda + text[i:];
										
										i = -1;
										delka = len(text);

										jmeno = "";
										ident.is_jmeno = 0;
										ident.is_makro = 0;
										dalsi = "";
									else:
										ident.is_parametr = 1;# TADY
										
										ident.is_makro = 0;
										ident.is_jmeno = 0;	
							continue; # POZOR NEBEZPECI
				
				ident.is_makro = 0;
				ident.is_jmeno = 0;
				jmeno = "";	
				continue;

		# POKUD NEJSME V BLOKU JEDNA SE O BLOK
		if text[i] == "{" and ident.blok == 0: # nesmime byt uprosted bloku a v pripade definice
												 # makra 
			
			if ident.is_makro == 0 or ident.is_jmeno == 1:
				ident.pocet_L += 1;
				ident.blok = 1;
				ident.is_makro = 0; 
				continue;
		
		if ident.blok == 1:
			
			# OSETRENI ESCAOE SEKVENCI
			if text[i] == '@' and ident.is_makro == 0 and ident.is_parametr == 0 and ident.is_definice == 0 and ident.is_metoda == 0: # pozname makro
				ident.is_makro = 1;			
				continue;
		
			if ident.is_makro == 1: # zpracujeme makro
				if text[i] == '@':
					pro_tisk += "@";
					ident.is_makro = 0;
					continue;

				elif text[i] == '{':
					pro_tisk += "{";
					ident.is_makro = 0;
					continue;

				elif text[i] == '}':
					pro_tisk += "}";
					if(delka - i) == 1 and ident.pocet_L != ident.pocet_P:
						sys.stderr.write("chyba, neukonceny blok\n");
						sys.exit(55);
					ident.is_makro = 0;
					continue;

				else: # jmeno makra	

					pro_tisk += "@";

					pro_tisk += text[i];
					ident.is_makro = 0;
					continue;
			
			# ZAVORKA UVNITR BLOKU
			if text[i] == "{" and ident.is_makro == 0: # zacatek bloku a pocita {
				ident.pocet_L += 1; # INKREMENTACE POCTU ZAVOREK
				
				if ident.is_definice == 0 and ident.is_metoda == 0 : # doplnen parametr
					if ident.is_parametr == 1 : # TADY
						par.jmeno += text[i];
						continue;

					pro_tisk += text[i];

					continue;
			
				
			if text[i] == "}" and ident.is_makro == 0 and ident.pocet_L != ident.pocet_P: # pocita }
				ident.pocet_P += 1;
				if ident.is_definice == 0 and ident.is_metoda == 0 and ident.pocet_L != ident.pocet_P: # pokud zavorky nesouviseji s definici a neni jich stejne
					if ident.is_parametr == 1: #TADY
						par.jmeno += text[i];
						continue;

					if(delka - i) == 1:
							sys.stderr.write("pocet zavorek neni stejny\n");	
							sys.exit(55);
						
					pro_tisk += text[i];
					
					continue;
		
			# DEFINICE MAKRA
			if ident.is_definice == 1: # parametry
				
				if text[i] == "$": # novy parametr					
					if par.misto != 0: # pokud to neni znak prvniho parametru makra
						m = regex.match(par.jmeno); # overime ze je spravna syntaxe
						if not m:							
							sys.stderr.write("spatny format parametru\n");
							sys.exit(55);
													
						prvni.parametr.append(par);
						para = par.misto;
						par = Par_info(); # vytvorime novy objekt	
						par.misto = para;

					prvni.p_par += 1;	
					par.misto += 1; # inkrementujeme pocet par na 1
					par.jmeno += text[i]; # musime $ pricitat uz tady, protoze do normalniho se nedostaneme
					continue;
				elif text[i] == " ": # ignoruji mezery mezi parametry				
					continue;

				elif text[i] == "}": # konec definice parametru
					m = regex.match(par.jmeno); # overime ze je spravna syntaxe
					if not m and par.jmeno:	
						sys.stderr.write("spatny format parametru\n");
						sys.exit(55);
						
					prvni.parametr.append(par); # vlozime i prazdny parametr
					par = Par_info(); # vytvorime novy objekt
					ident.blok = 0;
					ident.is_definice = 0;
					ident.is_metoda = 1;
					
					if ident.pocet_L != ident.pocet_P:
						sys.stderr.write("pocet zavorek neni stejny\n");	
						sys.exit(55);

					ident.pocet_P = 0;
					ident.pocet_L = 0;
					continue;

				elif text[i].isalpha() or text[i] == '_':
					par.jmeno += text[i];
					continue;

				# OMEZENI ZNAKU V DEFINICI
				else:
					sys.stderr.write("spatne parametry metody\n");
					sys.exit(55);


			if ident.is_metoda == 1: # ukladani metody
				# KONEC METODY, STRUKTURA SE ULOZI DO TABULKY
				if text[i] == "}" and ident.pocet_L == ident.pocet_P: # konec metody, vlozeni do tabulky maker
					
					ident.pocet_P = 0; # priprava pro dalsi blok
					ident.pocet_L = 0;
					for v in tabulka_maker:						
						if v.jmeno == prvni.jmeno:
							if jmeno == "__undef__" or jmeno == "__set__" or jmeno == "__def__":
								sys.stderr.write("chyba makro nelze zrusit\n");
								sys.exit(57);
							# POKUD JE ZAKAZANA REDEFINICE, TAK CHYBA	
							if redefinice == 1:
								sys.stderr.write("chyba redefinice\n");
								sys.exit(57);
							tabulka_maker.remove(v);

					tabulka_maker.append(prvni); # ulozeni do tabulky maker
							
					prvni = V_info();
					ident.is_metoda = 0;
					ident.is_makro = 0;

					ident.blok = 0;
					ident.is_jmeno = 0;
					continue;

				prvni.metoda += text[i];
				
				continue;
		
			# ZNACENI KONCE BLOKU
			if text[i] == "}" and ident.is_makro == 0 and ident.pocet_L == ident.pocet_P: # konec bloku ale neni to posledni zavorka
				ident.blok = 0;
				
				if ident.is_parametr == 1:
					if par.jmeno == "-INPUT_SPACES":

						par = Par_info();
						jmeno = "";
						
						ident.white = 1;
						ident.is_parametr = 0;
						continue;
					if par.jmeno == "+INPUT_SPACES":

						
						par = Par_info();
						jmeno = "";
						ident.white = 0;
						ident.is_parametr = 0;
						continue;
					
					# ULOZENI PARAMETRU
					druhy.pocet_nacteni += 1;
					par.misto +=1;
					para = par.misto;
					druhy.parametr.append(par); # dame do listu
					par = Par_info(); # vynulujeme parametry
					par.misto = para;
					metoda = "";
					
					# POKUD JE PARAMETR AKTIVNI, TAK DOCHAZI KE ZPRACOVANI
					prvni, druhy, tabulka_maker, metoda, ident = nalezeni(prvni, druhy, tabulka_maker, metoda ,ident,redefinice);			
					
					if ident.is_parametr == 0:
						i += 1;
						text = metoda + text[i:];
						#print(text);
						i = -1;
						delka = len(text);
						jmeno = "";
						ident.is_jmeno = 0;
						ident.is_makro = 0;
						
					else:
						metoda = "";

					
					if ident.is_parametr == 0:
						jmeno = "";
						par = Par_info();
					
					continue;	

				# POSLEME IHNED BLOK NA VYSTUP
				pro_tisk += zprac_blok(do_bloku); # blok expandujeme
				
				do_bloku = ""; # vynulovani po zpracovanem bloku
				ident.pocet_L = 0;
				ident.pocet_P = 0;
				continue;

			# POKUD JE BLOK PARAMETR
			if ident.is_parametr == 1: # doplnena podminka
				par.jmeno += text[i];	# TADY				
				continue;		

		if ident.white == 1 and ident.blok == 0:
			if text[i].isspace():
				white = 1;

		# ZPRACOVANI ESCAPE SEKVENCI A JMEN MAKER
		if text[i] == '@' and ident.is_makro == 0 : # pozname makro
			if (pomer == 1):
				sys.stderr.write("chyba, na konci vstupu nesmi byt @\n");
				sys.exit(55);

			ident.is_makro = 1;						
			continue;
	
		if ident.is_makro == 1 : # zpracujeme makro
			if text[i] == '$':
				ident.is_makro = 0;
				if ident.blok == 1:
					pro_tisk += "@";
				pro_tisk += "$";
				continue;

			elif text[i] == '@':
				pro_tisk += "@";
				ident.is_makro = 0;
				continue;

			elif text[i] == '{':
				pro_tisk += "{";
				ident.is_makro = 0;
				continue;

			elif text[i] == '}':
				pro_tisk += "}";
				ident.is_makro = 0;
				continue;

			elif text[i].isalpha() or text[i] == '_' or text[i].isdigit() or white == 1: # jmeno makra				
				if ident.blok == 1:
					pro_tisk += text[i];
					continue;
				
				if white == 1:
					continue;				
				else:
					ident.is_jmeno = 1;
				# ZPRACOVANI JMENA JAKO PARAMETRU
				if ident.is_parametr == 1:					
					par.jmeno += text[i];					
					if (delka - i) == 1:						
						if jmeno == "undef" or jmeno == "__undef__":
							for x in tabulka_maker:
								if x.jmeno == jmeno:
									if x.original == 1:										
										if par.jmeno == "@__undef__" or par.jmeno == "@__set__" or par.jmeno == "@__def__":
											sys.stderr.write("chyba makro nelze zrusit\n");
											sys.exit(57);
										
										tabulka_maker = undef(par.jmeno,tabulka_maker);										
										ident.is_cancel = 0;
										par= Par_info();
										jmeno = "";
										ident.is_jmeno = 0;
										ident.is_parametr = 0;
										ident.is_definice = 0;
										ident.is_makro = 0;		
														

						for x in tabulka_maker:
							if x.jmeno == jmeno:
								if x.p_par == 0: # proste vypise metodu
									text = x.metoda + text[i:];
									i = -1;
									delka = len(text);
									jmeno = "";
									ident.is_jmeno = 0;
									ident.is_makro = 0;
									dalsi = "";
								else:
									sys.stderr.write("Konec vstupu, nemozno nacist parametry\n");
									sys.exit(56);
					continue;
				# NACITANI JMENA MAKRA
				else:
					jmeno += text[i];					
					if (delka - i) == 1:						
						for x in tabulka_maker:
							if x.jmeno == jmeno:								
								nalezeno = 1;
								if x.p_par == 0: # proste vypise metodu									
									text = x.metoda;
									i = -1;
									delka = len(text);
									jmeno = "";
									ident.is_jmeno = 0;
									ident.is_makro = 0;
									dalsi = "";
												
								else:
									sys.stderr.write("Konec vstupu, nemozno nacist parametry\n");
									sys.exit(56);
						
						if nalezeno == 0:
							sys.stderr.write("chyba, makro nenalezeno\n");
							sys.exit(56);			
						
						continue;			

				if (delka - i) == 1:
					
					if ident.is_parametr == 1:
						druhy.pocet_nacteni += 1;
						par.misto +=1;
						para = par.misto;
						druhy.parametr.append(par);
						par.misto = para;
						
					else:
						prvni.jmeno = jmeno;	

					ident.is_jmeno = 0;
					metoda = "";					
					if jmeno == "undef" or jmeno == "__undef__":						
						for x in tabulka_maker:
							if x.jmeno == jmeno:
								if x.original == 1:
									if par.jmeno == "@__undef__" or par.jmeno == "@__set__" or par.jmeno == "@__def__":
											sys.stderr.write("chyba makro nelze zrusit\n");
											sys.exit(57);
									
									tabulka_maker = undef(par.jmeno,tabulka_maker);
							
									ident.is_cancel = 0;
									ident.is_parametr = 0;
									ident.is_jmeno = 0;			
									ident.is_makro = 0;
									jmeno = "";
									continue;
					metoda = "";
					prvni, druhy, tabulka_maker, metoda, ident = nalezeni(prvni, druhy, tabulka_maker, metoda ,ident,redefinice);			
					text = metoda + text[i:];
					i = -1;
					delka = len(text);
					jmeno = "";
					ident.is_jmeno = 0;
					ident.is_makro = 0;
					ident.is_parametr = 0;
					par = Par_info();				
			
				continue;

			else:				
				sys.stderr.write("chyba spatny znak\n");
				sys.exit(55);

		# ZPRACOVANI ZNAKU JAKO PARAMETRU 
		if ident.is_parametr == 1:			
			if white == 1:
				continue;
				
			par.jmeno += text[i];			
			druhy.pocet_nacteni += 1;
			par.misto +=1;
			para = par.misto;
			druhy.parametr.append(par); # dame do listu			
			par = Par_info(); # vynulujeme parametry
			par.misto = para;			
			metoda = "";
			prvni, druhy, tabulka_maker, metoda, ident = nalezeni(prvni, druhy, tabulka_maker, metoda ,ident,redefinice);			
			
			if ident.is_parametr == 0:
				i += 1;
				text = metoda + text[i:];
				i = -1;
				delka = len(text);
				jmeno = "";
				ident.is_jmeno = 0;
				ident.is_makro = 0;
				ident.is_parametr = 0;
				par = Par_info();
				#continue;
			if ident.is_parametr == 0:
				jmeno = "";
				par = Par_info();	
	
			continue;
		
		if text[i] == "$":
			sys.stderr.write("chyba nesmi byt $ samostatne\n");
			sys.exit(55);

		if text[i] == "}":

			sys.stderr.write("chyba nesmi byt } samostatne\n");
			sys.exit(55);

		if white == 0:
			
			pro_tisk += text[i];	

		if (delka - i) == 1:
			
			if ident.pocet_L != ident.pocet_P:
				
				sys.stderr.write("spatny pocet zavorek\n");
				sys.exit(55);

		
	return pro_tisk;
	

inputf = "";
outputf = "";
cmd = "";
vstup = 0; 
hlp = 0;
vystup = 0;
redefinice = 0;
pred = 0;
red = 0
data = ""; # kvuli cmd musi byt definovany


tabulka_maker = [];

prvni = V_info();

tabulka_maker = pred_def(tabulka_maker);

# ZPRACOVANI VOLANI
try:
	myopts, args = getopt.getopt(sys.argv[1:],"r",["help","input=","output=","cmd="]);
except getopt.GetoptError as err:
	print(err);
	sys.exit(1);

for o,a in myopts:
	if o == "--help":
		hlp += 1;
		if len(sys.argv) > 2:
			sys.stderr.write("nesmi byt vice argumentu s --help\n");
			sys.exit(1);
		napoveda();
		exit(0);

	if o in ("--input"):
		vstup += 1;
		inputf = a;
		try:
			file_i = open(inputf, 'r');	
		except IOError as e:
			print(e);
			sys.exit(2);
		

	if o in ("--output"):
		vystup += 1;
		outputf = a;
		try:	
			file_o = open(outputf, 'w');	
		except IOError as e:
			print(e);
			sys.exit(3);

	if o in ("--cmd"):
		pred += 1;
		cmd = a;
		#print(a);
	if o == "-r":
		red +=1;
		redefinice = 1;
			
if vstup > 1 or vystup > 1 or pred > 1 or hlp > 1 or red >1:
	sys.stderr.write("nesmi byt vice argumentu stejnych\n");
	sys.exit(1);

pro_tisk = "";

# PRO CMD PARAMETR
data = cmd;

if vstup == 1:
	data += file_i.read();


if vstup == 0:
	data += stdin.readline();
	data = data.rstrip('\n');


regex = re.compile("\$[a-zA-Z][a-zA-Z0-9_]*$");


pro_tisk += zpracovani(data,pro_tisk, tabulka_maker,redefinice);

if vystup == 0:
	pro_tisk = pro_tisk.lstrip('\n');
	#pro_tisk = pro_tisk.rstrip('\n');
	print(pro_tisk);
	sys.exit(0);	
else:
	pro_tisk = pro_tisk.lstrip('\n');
	#pro_tisk = pro_tisk.rstrip('\n');
	
	file_o.write(pro_tisk);