if [ "$1" = jdm ]; then
  set -e
  cd data/
  mkdir rezojdm16k
  wget "https://pimo.id/98145ac7/09032019-LEXICALNET-JEUXDEMOTS-FR-NOHTML.txt.zip"
  unzip 09032019-LEXICALNET-JEUXDEMOTS-FR-NOHTML.txt.zip
  mv JDM-LEXICALNET-FR originals

elif [ "$1" = rlf ]; then
  set -e
  mkdir data
  cd data/
  wget "https://repository.ortolang.fr/api/content/export?&path=/lexical-system-fr/7/&filename=lexical-system-fr&scope=YW5vbnltb3Vz1"
  unzip lexical-system-fr.zip
  cd lexical-system-fr/
  mv 7/* .
  rmdir 7
  mv ls-fr-V2.1 originals
  cd ..
  mv lexical-system-fr/ rlf

  grep "family id" data/rlf/originals/14-lslf-model.xml | cut -d '"' -f2,4 --output-delimiter=$'\t' > data/rlf/originals/lffam-ids-names.csv.tmp
  echo -e "id\tname" | cat - data/rlf/originals/lffam-ids-names.csv.tmp > data/rlf/originals/lffam-ids-names.csv

  grep "cptype" data/rlf/originals/03-lscopolysemy-model.xml | cut -d '"' -f2,4 --output-delimiter$'\t' > data/rlf/originals/cp-ids-names.csv.tmp
  echo -e "id\tname" | cat - data/rlf/originals/lffam-ids-names.csv.tmp > data/rlf/originals/lffam-ids-names.csv

  grep "ls:fr:lf:" data/rlf/originals/14-lslf-model.xml | cut -d '"' -f2,4 --output-delimiter=$'\t' > data/rlf/originals/lf-ids-names.csv.tmp
  echo -e "id\tname" | cat - data/rlf/originals/lffam-ids-names.csv.tmp > data/rlf/originals/lffam-ids-names.csv

else
  echo "$0: error, must be run with \"jdm\" or \"rlf\" as argument"
fi
