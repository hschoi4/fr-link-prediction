set -e
mkdir -p data
cd data/

if [ "$1" = jdm ]; then
  mkdir -p rezojdm16k
  cd rezojdm16k
  wget -O "09032019-LEXICALNET-JEUXDEMOTS-FR-NOHTML.txt.zip" "https://pimo.id/98145ac7/09032019-LEXICALNET-JEUXDEMOTS-FR-NOHTML.txt.zip"
  unzip 09032019-LEXICALNET-JEUXDEMOTS-FR-NOHTML.txt.zip
  mv JDM-LEXICALNET-FR originals

elif [ "$1" = rlf ]; then
  wget -O lexical-system-fr.zip "https://repository.ortolang.fr/api/content/export?&path=/lexical-system-fr/7/&filename=lexical-system-fr&scope=YW5vbnltb3Vz1"
  unzip lexical-system-fr.zip
  cd lexical-system-fr/
  mv 7/* .
  rmdir 7
  mv ls-fr-V2.1 originals
  cd ..
  mv lexical-system-fr/ rlf

  grep "family id" rlf/originals/14-lslf-model.xml | cut -d '"' -f2,4 --output-delimiter=$'\t' > rlf/originals/lffam-ids-names.csv.tmp
  echo -e "id\tname" | cat - rlf/originals/lffam-ids-names.csv.tmp > rlf/originals/lffam-ids-names.csv

  grep "cptype" rlf/originals/03-lscopolysemy-model.xml | cut -d '"' -f2,4 --output-delimiter=$'\t' > rlf/originals/cp-ids-names.csv.tmp
  echo -e "id\tname" | cat - rlf/originals/cp-ids-names.csv.tmp > rlf/originals/cp-ids-names.csv

  grep "ls:fr:lf:" rlf/originals/14-lslf-model.xml | cut -d '"' -f2,4 --output-delimiter=$'\t' > rlf/originals/lf-ids-names.csv.tmp
  echo -e "id\tname" | cat - rlf/originals/lf-ids-names.csv.tmp > rlf/originals/lf-ids-names.csv

else
  echo "$0: error, must be run with \"jdm\" or \"rlf\" as argument"
fi
