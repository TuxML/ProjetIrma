
# spring.sh is the "spring" from where comes all the ssh connexions to your IT infrastructure to run
# a given number of compilation via MLfood.py
# To run this script, you have to set up RSA keys on the machines you wish to use

room=("e008" "e010" "e103" "e105" "e212")

machine=("m01" "m02" "m03" "m04" "m05" "m06" "m07" "m08" "m09" "m10")

cpt=0
action="ps -aux | grep -m1 MLfood"
act="CHECKING"
act2="CHECKED"

if [ "$#" -ne 0 ] && ([ "$1" != "--help" ] && [ "$1" != "-h" ] && [ "$1" != "--kill" ])
  then
    echo "Error \"$1\""
    echo "Use ./alive.sh [-h,--help] [--kill]"
    exit -1
fi


if [ "$1" = "-h" ] || [ "$1" = "--help" ]
  then
    echo "Use ./alive.sh [-h,--help] [--kill]"
    exit 0
fi


if [ "$1" = "--kill" ]
  then
    echo "You choose to kill all process."
    action="ps aux | grep MLfood | grep -v grep | grep -v clean.py | grep -v ssh | awk '{ print $2; }' | xargs kill -9 2> /dev/null; ~/TP/ProjetIrma/clean.py --docker 2> /dev/null"
    act="KILLING"
    act2="KILLED"
fi

echo -n "login: "
read login
echo ""

# Machines de l'istic
for elem in ${room[@]}
do
  echo "$act -- Room $elem"
  for m in ${machine[@]}
  do
    cpt=$((cpt + 1))
    echo -n "Machine $elem$m : "; (ssh -o StrictHostKeyChecking=no -tt $login@$elem$m.istic.univ-rennes1.fr "$action; exit") | grep -v grep
  done
  echo ""
done

echo "$login -- $cpt machines $act2"
