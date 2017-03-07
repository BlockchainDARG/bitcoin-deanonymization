#!/bin/bash
# this file generates a pbs to run testname (shell file) with an argument
# 1st arugment -  testname
# 2nd argument -  arg for test

# available testnames and [args]
# hid1 [num nodes]
# hid2 [num nodes]
# datasize [size]
# gendata [run number]
testnames=['hid1','hid2','datasize','gendata']

function usage {
    echo "Usage: ./gen-pbs.sh <TESTNAME> <ARG> where"
    echo "       TESTNAME : hid1, hid2, datasize, gendata and"
    echo "       ARG      : num nodes, numnodes, addl runs, run number"
    echo "       respectively"
    echo "Sideeffects: create file in jobs/"
}
if [ $# -eq 0 ]; then
    usage;
    exit 1
fi

# NO ERROR CHECKING ON TESTNAMES

FILENAME=jobs/test-$1-$2.pbs
if [ -e $FILENAME ];
then rm $FILENAME
fi
touch $FILENAME
echo "#!/bin/bash" >> $FILENAME
echo "# Job generated by gen-pbs.sh" >> $FILENAME
echo "#PBS -l walltime=04:00:00" >> $FILENAME
echo "#PBS -l nodes=1:ppn=12:golub" >> $FILENAME
echo "#PBS -N test-"$1"-arg="$2 >> $FILENAME
echo "#PBS -q secondary" >> $FILENAME
echo "#" >> $FILENAME
echo "# End of embedded QSUB options" >> $FILENAME
echo "" >> $FILENAME

echo "# execute in my virtual env" >> $FILENAME
echo "source /home/limjiaj2/bitcoin-deanonymization/venv/bin/activate" >> $FILENAME
echo "" >> $FILENAME

echo "# change to bitcoin dir" >> $FILENAME
echo "cd /home/limjiaj2/bitcoin-deanonymization" >> $FILENAME
 echo "" >> $FILENAME

echo "# load necessary modules" >> $FILENAME
echo "module load python/2" >> $FILENAME
echo "module load gcc/6.2.0" >> $FILENAME
echo "" >> $FILENAME

echo "# Program below" >> $FILENAME
echo ./testscripts/test-$1.sh $2 >> $FILENAME
