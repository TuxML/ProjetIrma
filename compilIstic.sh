#!/usr/bin/bash

list=("e008m" "e003m" "e005m" "e010m" "e103m" "e105m" "e212m")

machine=("01" "02" "03" "04" "05" "06" "07" "08" "09" "10")

for elem in ${list[@]}
do
  for m in ${machine[@]}
  do
    ssh 14008349@$elem$m.istic.univ-rennes1.fr &
  done
done
