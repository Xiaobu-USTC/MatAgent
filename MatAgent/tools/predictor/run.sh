# 源 Intel 编译器环境变量
source /home/gpu2/intel2020/compilers_and_libraries_2020.4.304/linux/bin/compilervars.sh intel64

# 更新 PATH
export PATH=/home/gpu2/intel2020/compilers_and_libraries_2020.4.304/linux/mpi/intel64/bin:${PATH}

# 更新 LD_LIBRARY_PATH 和其他相关环境变量
export LD_LIBRARY_PATH=/home/gpu2/software/pwdft-lib/install/fftw-3.3.8/lib:$LD_LIBRARY_PATH
export LIBRARY_PATH=/home/gpu2/software/pwdft-lib/install/fftw-3.3.8/lib:$LIBRARY_PATH
export INCLUDE_PATH=/home/gpu2/software/pwdft-lib/install/fftw-3.3.8/include:$INCLUDE_PATH
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/home/gpu2/intel2020/compilers_and_libraries_2020.4.304/linux/mkl/lib/intel64_lin:/home/gpu2/intel2020/compilers_and_libraries_2020.4.304/linux/compiler/lib/intel64_lin
MPIRUN=/home/gpu2/intel2020/compilers_and_libraries_2020.4.304/linux/mpi/intel64/bin/mpirun
PWDFT=/home/gpu2/software/pwdft-new/hefeidgdft/examples/pwdft
#runvasp="$MPI $VASP"
#runvasp="$MPI -np $NCPUS -machinefile $PBS_NODEFILE $VASP"
logfile=runlog

                $MPIRUN -np 2 $PWDFT > runlog.out

