list=("e008m" "e010m" "e103m" "e105m" "e212m")

machine=("01" "02" "03" "04" "05" "06" "07" "08" "09" "10")

cpt=0

# Machines de l'istic
for elem in ${list[@]}
do
  for m in ${machine[@]}
  do
    cpt=$((cpt + 1))
    (echo $elem$m -- BEGIN; ssh -o StrictHostKeyChecking=no -tt 14008349@$elem$m.istic.univ-rennes1.fr "echo \"$elem$m -- BEGIN\";~/TP/ProjetIrma/MLfood.py 1 --force-compilation-limits --dev --no-kernel --no-logs --no-check-log --silent; exit" > /dev/null;  echo $elem$m -- DONE)&
  done
done

echo "$cpt machine are used"

# Works for sudo asking computer
# for x in $(seq 0 3)
# do
#   ssh -o StrictHostKeyChecking=no -tt alemasle@131.254.18.201 "echo \"$password\" | sudo -S ~/ProjetIrma/MLfood.py 1 --force-compilation-limits --dev --no-kernel --no-logs --no-check-log"&
# done
