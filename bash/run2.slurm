#! /bin/bash
#SBATCH --account=p_masi_gpu
#SBATCH --partition=pascal
#SBATCH --gres=gpu:1
#SBATCH --nodes=1
#SBATCH --ntasks=2
#SBATCH --mem=40G
#SBATCH --time=120:00:00
#SBATCH --output=/scratch/yaoy4/SceneClassification/log/run2.log
module load Anaconda2
source activate FCN
setpkgs -a tensorflow_0.12
cd /scratch/yaoy4/SceneClassification/
python  /scratch/yaoy4/SceneClassification/main.py exp exp2
