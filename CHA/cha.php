<?php
#!/usr/bin/php
#CHA:xpolan07

mb_internal_encoding("UTF-8");

/* POLE PRO ZISKANI HODNOT ZE VSTUPU */
$option = array("input:",
				"output:",
				"no-duplicate",
				"max-par:",
				"no-inline",
				"help",
				"pretty-xml::");


$in = false;
$out = false;
$inline = false;
$no_d = false;
$max = false;
$pretty = false;
$white = false;

/* POLE, ZDA BYL PARAMETR ZADAN */
$is_param = array('in' => false,
				 'out' => false,
				'inline' => false,
				'no_d' => false,
				'max' => false,
				'pretty' => false,
				'white' => false);

/* POLE PRO HODNOTY ZE VSTUPU */
$arg_hodnoty = array('in' => "",
					'out' => "",
					'max' => 0,
					'pretty' => 0);

/* POLE REGEXP PRO VSTUPY */
$param = array('1' => "/^--?input=.+$/",
			   '2' => "/^--?output=.+$/",
			   '3' => "/^--?no-inline$/",
			   '4' => "/^--?no-duplicates$/",
			   '5' => "/^--?remove-whitespace$/",
			   '6' => "/^--?max-par=[0-9]+/",
			   '7' => "/^--?pretty-xml=?[0-9]*/");

/* ZISKANI HODNOT ZE VSTUPU */
$get = getopt("",$option);

$arg_input = "";
$arg_output = "";
$arg_pretty = 4;
$arg_max = 0;

$glob_utf = 1;
$vystup_file;
$dir = "";
$konkat = "";
$glob_file = "";



/* FUNKCE PRO NAPOVEDU */
function napoveda()
{
	printf("Vypracoval: Petr Polansky\n
Login: xpolan07\n
Projekt: CHA: C HEADER ANALYSIS\n\n
Popis: Skript ma za ucel prohledat cely adresar,\n
\t vyhledat veskere hlavickove soubory, ktere se v nem\n
\t nachazi a z nich potom vypsat informace o funkcich\n\n
Parametry pro spusteni: \n
\t --help : vytiskne napovedu\n
\t --input=fileordir : cesta muze udavat soubor nebo adresar\n
	\t\t pokud je zadana cesta primo k souboru, musi to byt .h soubor\n
\t --output=file : cesta k souboru, do ktereho se vypise XML informace\n
\t --pretty-xml=k : udava jak velke bude odsazeni mezi zanorenimi\n
\t --no-inline : budou ignorovany funkce se specifikatorem inline\n
\t --max-par=n : budou vypsany pouze funkce s 'n' a mene parametry\n
\t --no-duplicates : pokud budou v souboru funkce se stejnymi jmeny,\n
	\t\t tak se vypise pouze prvni z nich a zbyle se preskoci\n
\t --remove-whitespace : vsechny bile znaky u parametru rettype a type\n
	\t\t budou nahrazeny mezerou\n\n
\t Skript muze byt spusten i bez parametru.\n
\t Pokud neni zadan parametr --output, tak se vystup vypise na stdout\n");
}

/* PROHLEDANI VSTUPU */
/* Jako parametr je predano pole udavajici,ktere parametry byly
   zadany, cesta k souboru a pole hodnot ziskanych z parametru */

function rek_search($input,$is_param, $arg_hodnoty) // rekurzivni prohledani
{
	global $dir;
	global $glob_file;

	/* NEBYL ZADAN VSTUP => PROHLEDAT VSE */
	if (empty($input) == true && $is_param['in'] == false) 
	{
		//printf("PR: $input\n");
		$input = "./";	
		$dir = "./";
	}

	/* Pokud je input adresar, mozna zbytecne */
	if(is_dir($input))
	{	

	}	

	/* ZADAN PRIMO SOUBOR => NEKONTROLOVAT PRIPONU */
	elseif (is_file($input)) 
	{
		$glob_file = $input;
		if(zprac_file($is_param, $input, $arg_hodnoty) == 1)
		{
			exit(1);
		}
		return(0);
	}

	else
	{
		fprintf(STDERR, "Ani soubor ani adresar\n");	
		exit(2);
	}


	/* OTEVRENI A CTENI ADRESARE */
	if ($handle = opendir($input)) 
	{
		/* CTENI OBSAHU ADRESARE */
		while (false !== ($entry = readdir($handle))) 
		{
			
			if (($entry != ".") && ($entry != "..")) // toto nechceme prohledavat
			{
				
				$jo_dir = $input."/".$entry; // spojime cestu se souborem v adresari
				
				if (is_dir($jo_dir)) // pokud vznikne adresar, musime rekurzivne dal prohledat
				{	
					rek_search($jo_dir,$is_param, $arg_hodnoty);
				}

				elseif (is_file($jo_dir)) // pokud je to soubor, musime zkontrolovat priponu
				{
					$h_file = substr($jo_dir, -2);
					
					if (strcmp($h_file, ".h") == 0) 
					{
						$glob_file = str_replace($dir."/","", $jo_dir);						
						if(zprac_file($is_param, $jo_dir, $arg_hodnoty) == 1)
						{
							closedir($handle);
							exit(1);							
						}

					}
					
				}				
			}
		}
		
	}
	else
	{	
		fprintf(STDERR, "Nepodarilo se otevrit adresar.\n");
		exit(2);
	}

	closedir($handle);
	return 0;
}

/* ZPRACOVANI JEDNOTLIVEHO SOUBORU */
/* Jako parametr je predano pole udavajici,ktere parametry byly
   zadany, cesta k souboru a pole hodnot ziskanych z parametru
 */
function zprac_file($is_param, $jo_dir,$arg_hodnoty) 
{
	global $glob_utf;
	global $vystup_file;
	global $dir;
	global $konkat;
	global $glob_file;

	$odsad_f = ""; 
	$odsad_p = "";
	$promenne_par = "no";

	/* REGEXP PRO FUNKCI*/
	$funkce = "/[a-zA-z0-9_ *\s]+\([a-zA-Z0-9_ ,*.\s\[\]\(\)]*\);?/";
	
	/* REGEXP PRO NAVRATOVY TYP FUNKCE */	
	$typ = "/[a-zA-Z0-9_\s\*\(\)]+[\s\*]+(?=[a-zA-Z0-9_]+\s*\()/";
	
	/* REGEXP PRO KOMENTARE */
	$komentare = "/(\/\*.*?\*\/|\/\/.*?(\n|$))/";
	
	/* REGEXP PRO JMENO FUNKCE */
	$jmeno = "/[a-zA-Z0-9_]*(?=\s*\()/";	

	/* REGEP PRO PARAMETRY FUNKCE */	
	$argum = "/\([a-zA-Z0-9_,.* \s\[\]]*\)/";	
	
	/* REGEXP PRO TYP PROMENNE */
	$typ_promenne = "/[a-zA-Z0-9_\* \s]+[ \*]+(?=[a-zA-Z0-9_\s])/";
	
	/* REGEXP PRO PROMENNE PARAMETRY */
	$prom_arg = "/\.\.\./";
	
	
	/*  ZPRACOVANI VYSTUPU */	
	if ($is_param['out'] == true && $glob_utf <= 1) 
	{
		if (($vystup_file = fopen($arg_hodnoty['out'], "w+")) == false) 
		{
			fprintf(STDERR, "Nepodarilo se otevrit vystupni soubor.\n");
			exit(3);	
		}
		
	}	
	else if($is_param['out'] == false)
	{
		$vystup_file = STDOUT;
		
	}

	/* VLOZIME OBSAH SOUBORU DO STRING */
	if(($file = file_get_contents($jo_dir)) === false)
	{
		fclose($vystup_file);
		exit(2);
	}

	$file = preg_replace("/\\\.*\n/", "", $file);


	/* NAHRAZENI KOMENTARU */
	if (preg_match("/(\/\*.*?\*\/|\/\/.*?(\n|$))/s", $file, $matches)) // nahradime komentare 
	{
		$file = preg_replace("/(\/\*.*?\*\/|\/\/.*?(\n|$))/s" , "", $file);	
	}

	
	
	/* NAHRAZENI RETEZCU */
	if (preg_match("/(\".*\"|'.*')/s", $file, $matches)) // nahradime komentare 
	{
		$file = preg_replace("/(\".*\"|\'.*\')/s", "", $file);
	}


	/* NAHRAZENI MAKER */
	if (preg_match("/#define.*(?<!\\\\)(\n|$)/", $file, $matches)) // nahradime komentare 
	{
		$file = preg_replace("/(#define.*)(?<!\\\\)(\n|$)/", "", $file);
	}

	
	
	
	/* ZPRACOVANI PARAMETRU PRETTY-XML */
	if ($is_param['pretty'] == true) 
	{
		$konkat = "\n";	
		for ($i=0; $i < $arg_hodnoty['pretty']; $i++) 
		{ 
			$odsad_f .= " ";
		}
		$odsad_p .= $odsad_f . $odsad_f;
	}

	/* ZAJISTIME, ABY SE HLAVICKA NEOPAKOVALA */
	if ($glob_utf <= 1) 
	{
		
		fwrite($vystup_file, "<?xml version=\"1.0\" encoding=\"utf-8\"?>$konkat");
		fwrite($vystup_file, "<functions dir=\"$dir\">$konkat");
		
		$glob_utf++;
	}

	/* VYHLEDANI FUNKCI V SOUBORU */
	if (preg_match_all($funkce, $file, $matches)) 
	{
		$pole_jmen = array();		// pole pro seznam funkci

		foreach ($matches as $value) 
		{
			foreach ($value as $hod) // zpracovani konkretni funkce
			{
				/* NALEZENI NAVRATOVEHO TYPU FUNKCE */
				if(preg_match($typ, $hod, $matches)) 
				{
					$typ_funkce = $matches[0];
					$typ_funkce = trim($typ_funkce);
					
					if (empty($typ_funkce)) 
					{
						continue;
					}
					$typ_funkce = preg_replace("/^\s*(?=[a-zA-Z])/", '', $typ_funkce); // nahradime bile znaky pred slovem
					
					$typ_funkce = preg_replace("/(?<=[a-zA-Z\*])\s*$/", '', $typ_funkce);  // nahradime bile znaky za slovem

					
				
					/* POKUD JE ZADAN PARAMETR NO-INLINE */
					if ($is_param['inline'] == true) // pokud byl zadan parametr --no-inline
					{
						$inline = strpos($matches[0], 'inline'); // zjisteni zda neni typ inline
					
						if ($inline === false) 
						{
							
						}
						
						else
						{							
							continue; // pokud je inline tak funkci ignorujeme
						}
					}

					/* POKUD BYL ZADAN PARAMETR REMOVE-WHITESPACE */
					if ($is_param['white'] == true) 
					{
						$typ_funkce = preg_replace('/\s+/', ' ', $typ_funkce); // vsechny bile znaky jsou nahrazeny mezerou
						
						$typ_funkce = preg_replace("/ (?=\*)/","", $typ_funkce); // mezera pred ukazatelem je smazana
					
						$typ_funkce = preg_replace("/(?<=\*) ?/","", $typ_funkce);
					
					}
					
				}
				

				/* NALEZENI JMENA FUNKCE */
				if(preg_match($jmeno, $hod, $matches)) // nalezeni jmena funkce
				{
					$jmeno_funkce = $matches[0];

					/* POKUD JE ZADAN PARAMETR NO-DUPLICATES */
					if ($is_param['no_d'] == true) // pokud byl zadan parametr --no-duplicates
					{
						if (in_array($matches[0], $pole_jmen)) // pokud uz funkce stejneho jmena existuje tak ignorujeme
						{ 
							continue;	
						}
						
						else
						{
							array_push($pole_jmen, $matches[0]); // pokud funkce zatim neexistuje, tak si ulozime jeji jmeno
						}
					}
				}

				/* NALEZENI PARAMETRU FUNKCE */
				if(preg_match($argum, $hod, $matches)) // zpracovani parametru funkce
				{
					$neuprav = $matches[0];
					$uprav = substr($neuprav, 1, -1);	// odstranime zavorky po stranach
					
					$pole_par= explode(",", $uprav);	// oddelime jednotlive parametry podle carky(",")

					$cislo_par = count($pole_par);

					foreach ($pole_par as $value) // zjistime zda funkce nema promenny pocet parametru
					{
						$value = trim($value);
						if (preg_match($prom_arg, $value, $matches)) // zjistime zda nebyl zadan promnenny pocet parametru funkce
						{		
							$promenne_par = "yes";
							$cislo_par--;							
						}
						/* POKUD JE PARAMETR PRAZDNY NEBO VOID TAK JE POCET PARAMETU 0 */
						if (strcmp($value, "void") == 0 || empty($value)) // pokud je parametr void nebo neni zadan, preskocime
						{
							$cislo_par = 0;
						}
					}

					/* POKUD JE ZADAN PARAMETR MAX-PAR */
					if ($is_param['max'] == true) // pokud je zadan parametr --par-max
					{

						if ($cislo_par <= $arg_hodnoty['max']) // zjistime zda pocet parametru odpovida max-par 
						{
														
						}
						
						else
						{
							continue; // tuto funkci nevypiseme
						}
					}

					fwrite($vystup_file, "$odsad_f<function file=\"$glob_file\" name=\"$jmeno_funkce\" varargs=\"$promenne_par\" rettype=\"$typ_funkce\">$konkat");
					
					$promenne_par = "no"; // ihned negujeme
					$cislo_par = 0; 

					/* VYHLEDANI TYPU PROMENNE */
					foreach ($pole_par as $value) 
					{
						$cislo_par++;
				
						if(preg_match($typ_promenne, $value, $matches)) // zjistime typ promenne parametru
						{
							
							$navrt_promenne = $matches[0];
							
							/* ZPRACOVANI POLI V JAKO NAVRATOVEHO TYPU */
							if (preg_match("/\s*[\[\]]+/", $value, $matches)) 
							{
								$navrt_promenne .= $matches[0];
							}

							$navrt_promenne = preg_replace("/^\s*(?=[a-zA-Z])/", '', $navrt_promenne); // odstraneni bilych znaku pred slovem
							
							$navrt_promenne = preg_replace("/(?<=[a-zA-Z\*])\s*$/", '', $navrt_promenne); // odstraneni bilych znaku za slovem
							
							/* POKUD BYL ZADAN PARAMETR REMOVE-WHITESPACE */
							if ($is_param['white'] == true) 
							{
								$navrt_promenne = preg_replace('/\s+/', ' ', $navrt_promenne); // vsechny bile znaky jsou nahrazeny mezerou
						
								$navrt_promenne = preg_replace("/ (?=\*)/","", $navrt_promenne); // mezera pred ukazatelem je smazana
								
								$navrt_promenne = preg_replace("/(?<=\*) ?/","", $navrt_promenne); 
								
								$navrt_promenne = preg_replace("/ ?(?=\[\])/","", $navrt_promenne);
							}
						}
						
						/* PRESKOCIME FUNKCI S PROMENNYMI PARAMETRY */
						else if (preg_match($prom_arg, $value, $matches)) // zjistime zda nebyl zadan promnenny pocet parametru funkce
						{	
							continue;
						}

						else
						{

							continue;
						}
						$value = trim($value);
						/* PRESKOCIME PRAZDNE PARAMETRY A VOID */
						if (strcmp($value, "void") == 0 || empty($value)) // pokud je parametr void nebo neni zadan, preskocime
						{
							continue;
						}
						else
						{	
							fwrite($vystup_file,"$odsad_p<param number=\"$cislo_par\" type=\"$navrt_promenne\" />$konkat");							
						}

					}
					fwrite($vystup_file, "$odsad_f</function>$konkat");
	
				}

			}
		}	
	}


}

/* ZPRACOVANI ARGUMENTU */
for ($i=1; $i < $argc; $i++) 
{
		$nalezeno = false; 
		if (($argv[$i] == "--help") && ($argc == 2))  {
			Napoveda();
			exit(0);
		}
		else if(($argv[$i] == "--help") && ($argc > 2))
		{
			fprintf(STDERR, "Parametr neodpovida povolenym.\n");
			exit(1);
		}

		foreach ($param as $key => $value) 
		{
			if (preg_match($value,  $argv[$i])) 
			{	
					$nalezeno = true;

					switch ($key) {
						case '1':
							if($in)
							{
								fprintf(STDERR, "Parametr se vyskytuje vicekrat\n");
								exit(1);
							}
							$in = true;
							$is_param['in'] = true;
							$arg_input = $get['input'];
							if (is_dir($arg_input)) 
							{
								$dir = $arg_input;
							}
								
							break;
						case '2':
							if($out)
							{
								fprintf(STDERR, "Parametr se vyskytuje vicekrat\n");
								exit(1);
							}
							$out = true;
							$is_param['out'] = true;
							$arg_hodnoty['out'] = $get['output'];
							
							break;
						case '3':
							if($inline)
							{
								fprintf(STDERR, "Parametr se vyskytuje vicekrat\n");
								exit(1);
							}
							$inline = true;
							$is_param['inline'] = true;	
							break;	
						case '4':
							if($no_d)
							{
								fprintf(STDERR, "Parametr se vyskytuje vicekrat\n");
								exit(1);
							}
							$no_d = true;
							$is_param['no_d'] = true;
							break;
						case '5':
							if($white)
							{
								fprintf(STDERR, "Parametr se vyskytuje vicekrat\n");
								exit(1);
							}
							$white = true;
							$is_param['white'] = true;
							break;
						case '6':
							if($max)
							{
								fprintf(STDERR, "Parametr se vyskytuje vicekrat\n");
								exit(1);
							}
							$max = true;
							$is_param['max'] = true;
							if ($get['max-par'] == "0") 
							{
								
								$arg_hodnoty['max'] = 0;
								break;	
							}
							
							if (empty($get['max-par'])) 
							{
								
								$arg_hodnoty['max'] = $get['max-par'];
								
								
								exit(1);
							}
														
							else
							{
								$arg_hodnoty['max'] = $get['max-par'];

								if (is_numeric($arg_hodnoty['max']) == false) 
								{
									fprintf(STDERR, "Zadane 'n' neni cislo\n");
									exit(1);
								}	
							}

							break;

						case '7':
							if($pretty)
							{
								fprintf(STDERR, "Parametr se vyskytuje vicekrat\n");
								exit(1);
							}

							
							$is_param['pretty'] = true;
							foreach ($get as $k => $v) 
							{
								if ($k == 'pretty-xml') 
								{
									$pretty = true;
								}
								
							}
							if($pretty == false)
							{
								fprintf(STDERR, "Parametr neodpovida povolenym.\n");
								exit(1);
							}
							
							if ($get['pretty-xml'] === "0") 
							{
								//printf("1. JOP\n");
								$arg_hodnoty['pretty'] = 0;
								
								break;	
							}
							
							if (empty($get['pretty-xml'])) 
							{
								//printf("2. JOP\n");
								$arg_hodnoty['pretty'] = 4;
								break;
							}
														
							else
							{
								$arg_hodnoty['pretty'] = $get['pretty-xml'];

								if (is_numeric($arg_hodnoty['pretty']) == false) 
								{
									fprintf(STDERR, "Zadane 'k' neni cislo\n");
									exit(1);
								}
								
							}
							
							break;		

						default:
							fprintf(STDERR, "Nezname\n");							
							break;
					}
			}	
	
		}
		
		if ($nalezeno == false) 
		{
			fprintf(STDERR, "Parametr neodpovida povolenym.\n");
			exit(1);
		}
}

rek_search($arg_input, $is_param, $arg_hodnoty);

fwrite($vystup_file, "</functions>$konkat");

exit(0);




?>