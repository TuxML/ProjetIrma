list=("e008m" "e003m" "e005m" "e010m" "e103m" "e105m" "e212m")

machine=("01" "02" "03" "04" "05" "06" "07" "08" "09" "10")

echo -n Password:
read -s password
echo

# for elem in ${list[@]}
# do
#   for m in ${machine[@]}
#   do
#     #sshpass -p "$password" ssh -o StrictHostKeyChecking=no -tt 14008349@$elem$m.istic.univ-rennes1.fr "~/TP/ProjetIrma/MLfood.py 100 --force-compilation-limits --dev --no-kernel --no-logs --no-check-log"&
#     # ssh -o StrictHostKeyChecking=no -tt 14008349@$elem$m.istic.univ-rennes1.fr "~/TP/ProjetIrma/MLfood.py 100 --force-compilation-limits --dev --no-kernel --no-logs --no-check-log"&
#   done
# done

ssh -o StrictHostKeyChecking=no -tt alemasle@131.254.18.201 "~/TP/ProjetIrma/MLfood.py 1 --force-compilation-limits --dev --no-kernel --no-logs --no-check-log"&
