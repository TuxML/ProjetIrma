# To run this script, you have to set up RSA keys on the machines you wish to use


echo -n "login: "
read login

list=("e008m" "e010m" "e103m" "e105m" "e212m")

machine=("01" "02" "03" "04" "05" "06" "07" "08" "09" "10")

cpt=0

# Machines de l'istic
for elem in ${list[@]}
do
  for m in ${machine[@]}
  do
    cpt=$((cpt + 1))
    (echo $elem$m -- BEGIN; ssh -o StrictHostKeyChecking=no -tt $login@$elem$m.istic.univ-rennes1.fr "nohup ~/TP/ProjetIrma/MLfood.py 100 --force-compilation-limits --dev --no-kernel --no-logs --no-check-log --silent > /dev/null; exit" > /dev/null;  echo $elem$m -- DONE)&
  done
done

echo "$cpt machines are used"
