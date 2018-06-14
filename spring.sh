
# spring.sh is the "spring" from where comes all the ssh connexions to your IT infrastructure to run
# a given number of compilation via MLfood.py
# To run this script, you have to set up RSA keys on the machines you wish to use

room=("e008" "e010" "d020" "d022" "d024" "d026" "d028" "d122")

machine=("m01" "m02" "m03" "m04" "m05" "m06" "m07" "m08" "m09" "m10")

cpt=0

if [ $# -eq 0 ]
  then
    echo "Please precise a number of compilation to spread: ./compilIstic.sh [number]"
    exit -1
fi

re='^[0-9]+$'
if ! [[ $1 =~ $re ]] ; then
   echo "error: Not a number" >&2; exit 1
fi


echo -n "login: "
read login

# Machines de l'istic
for elem in ${room[@]}
do
  echo "Room $elem -- START"
  for m in ${machine[@]}
  do
    cpt=$((cpt + 1))
    (ssh -o StrictHostKeyChecking=no -tt $login@$elem$m.istic.univ-rennes1.fr "nohup ~/ProjetIrma/MLfood.py $1 --force-compilation-limits --dev --no-logs --no-check-log > /dev/null; exit" > /dev/null;  echo $elem$m -- END)&
  done
done

echo "$login has spread $1 compilations on $cpt machines"
