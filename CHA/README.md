# 1.projekt do IPP v roce 2015

Skript slouží k vyhledání hlavičkových souborů, nalezení v nich funkcí v jazyce C a zpracování informací o nich do formátu XML.

php -d open_basedir=““ cha.php [VOLITELNE]

Volitelné parametry:

1) cesta k souboru nebo ke složce, pokud není zadano, tak se prohledává aktuální složka

2) --no-inline - skript přeskočí funkce, které obsahují identifikátor inline a tudíž je nevypíše na výstup

3) --remove-whitespace - odstraní všechny přebytečné bílé znaky u návratovém typu funkce a u typů parametrů funkce a nahradí je mezerou

4) --no-duplicates - přeskočení duplicitních funkcí

5) --max-par Number - budou zpracovány jen funkce, které mají stejně nebo méně parametrů než Number 