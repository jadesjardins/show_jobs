# SET UP

```bash
ssh <username>@<clustername>.computecanada.ca

cd /project/<accountname>/
git clone https:/github.com/jadesjardins/show_jobs.git
cd show_jobs

module load StdEnv/2020
module load python/3.8.10

python -m venv env_show_jobs
source env_show_jobs/bin/activate

python -m pip install ViewClust-Vis
python -m pip install jupyterlab
python -m pip install ipykernel
python -m ipykernel install --user --name show_jobs_kernel

echo -e '#!/bin/bash\nunset XDG_RUNTIME_DIR\njupyter notebook --ip $(hostname -f) --no-browser' > $VIRTUAL_ENV/bin/notebook.sh
chmod u+x $VIRTUAL_ENV/bin/notebook.sh
```


# INTERACTIVE JOB

```bash 
ssh <username>@<clustername>.computecanada.ca

cd /project/<accountname>/show_jobs

module load StdEnv/2020
module load python/3.8.10

source env_show_jobs/bin/activate

salloc --time=3:0:0 --ntasks=1 --cpus-per-task=1 --mem-per-cpu=4G --account=<accountname> srun $VIRTUAL_ENV/bin/notebook.sh

...
[I 11:47:49.705 NotebookApp] Serving notebooks from local directory: /project/6006282/jobs_props
[I 11:47:49.705 NotebookApp] Jupyter Notebook 6.4.10 is running at:
[I 11:47:49.705 NotebookApp] http://gra797.graham.sharcnet:8888/?token=ed60c54ebdbf877e86c69f3af3cb6bbb62ac8fc354a28f8f
[I 11:47:49.705 NotebookApp]  or http://127.0.0.1:8888/?token=ed60c54ebdbf877e86c69f3af3cb6bbb62ac8fc354a28f8f
[I 11:47:49.705 NotebookApp] Use Control-C to stop this server and shut down all kernels (twice to skip confirmation).
[C 11:47:49.717 NotebookApp] 
    
    To access the notebook, open this file in a browser:
        file:///home/jdesjard/.local/share/jupyter/runtime/nbserver-24844-open.html
    Or copy and paste one of these URLs:
        http://gra797.graham.sharcnet:8888/?token=ed60c54ebdbf877e86c69f3af3cb6bbb62ac8fc354a28f8f
     or http://127.0.0.1:8888/?token=ed60c54ebdbf877e86c69f3af3cb6bbb62ac8fc354a28f8f
```



# OPEN SSH TUNNEL

```bash
ssh -L 9999:gra797.graham.sharcnet:8888 jdesjard@graham.computecanada.ca
```

# NAVIGATE BROWSER TO NOTEBOOK

```bash
http://localhost:9999/lab?token=ed60c54ebdbf877e86c69f3af3cb6bbb62ac8fc354a28f8f
```
