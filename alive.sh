
# spring.sh is the "spring" from where comes all the ssh connexions to your IT infrastructure to run
# a given number of compilation via MLfood.py
# To run this script, you have to set up RSA keys on the machines you wish to use

room=("e008" "e010" "e103" "e105" "e212")

machine=("m01" "m02" "m03" "m04" "m05" "m06" "m07" "m08" "m09" "m10")

cpt=0

echo -n "login: "
read login
echo ""

# Machines de l'istic
for elem in ${room[@]}
do
  echo "CHECKING -- Room $elem"
  for m in ${machine[@]}
  do
    cpt=$((cpt + 1))
    echo -n "Machine $elem$m : "; (ssh -o StrictHostKeyChecking=no -tt $login@$elem$m.istic.univ-rennes1.fr "ps -aux | grep -m1 MLfood; exit") | grep -v grep
  done
  echo ""
done

echo "$login -- $cpt machines CHECKED"
