from turtle import color
import datetime
import pandas as pd
import numpy as np
import subprocess
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots



def get_sacct_jobs(d_from, account, debugging=False):
    """Script for profiling the memory usage of an account via sacct.

    DEPRECATION WARNING.

    Always outputs various statistical measures to stdout, but can
    also plot information.

    Parameters
    -------
    d_from: date str
        Beginning of the query period, e.g. '2019-04-01T00:00:00'.
    account: str
        Account to query via sacct, e.g. 'def-tk11br_cpu'
    fig_out: str, optional
        Writes the generated figure to file as the given name.
        If empty, skips writing. Defaults to empty.
    debugging: boolean, optional
        Boolean for reporting progress to stdout. Default False.
    """

    get_steps_cmd = ['sacct', '-a', '-A', account, '-S', d_from,
                '-p', '--delimiter', '"|"', '-n',
                '--units=M', '-o',
                'jobid,user,submit,eligible,start,end,elapsedraw,timelimitraw,state,ncpus,nnodes,reqmem,maxrss,partition,priority']
    steps = subprocess.check_output(get_steps_cmd).decode('UTF-8')

    steps_df = pd.DataFrame([x.split('"|"') for x in steps.split('\n')])
    steps_df = steps_df.iloc[:, :-1]  # Due to split implementation...
    steps_df = steps_df.iloc[:-1, :]  # Due to split implementation...

    steps_df.columns = ['jobid','user','submit','eligible','start','end','elapsed','timelimit','state','reqcpus','nnodes','reqmem','maxrss','partition','priority']

    batch_df = steps_df[steps_df.jobid.str.contains('batch', na=False)]
    batch_df = batch_df[batch_df.maxrss.str.contains('M', na=False)]
    batch_df.update(batch_df.maxrss.loc[lambda x: x.str.contains('M')]
                     .str.replace('M', ''))


    
    get_jobs_cmd = ['sacct', '-aX', '-A', account, '-S', d_from,
                '-p', '--delimiter', '"|"', '-n',
                '--units=M', '-o',
                'jobid,user,submit,eligible,start,end,elapsedraw,timelimitraw,state,ncpus,nnodes,reqmem,maxrss,partition,priority']
    jobs = subprocess.check_output(get_jobs_cmd).decode('UTF-8')

    jobs_df = pd.DataFrame([x.split('"|"') for x in jobs.split('\n')])
    jobs_df = jobs_df.iloc[:, :-1]  # Due to split implementation...
    jobs_df = jobs_df.iloc[:-1, :]  # Due to split implementation...

    jobs_df.columns = ['jobid', 'user','submit','eligible','start','end','elapsed','timelimit','state','reqcpus','nnodes','reqmem','maxrss','partition','priority']

    jobs_df['maxrss']=batch_df['maxrss']
    
    #print(jobs_df['elapsed'])

    time_columns = ['submit','eligible','start','end']
    jobs_df[time_columns] = jobs_df[time_columns].apply( pd.to_datetime, errors='coerce' )
    integer_columns = ['reqcpus','nnodes','elapsed','timelimit']
    jobs_df[integer_columns] = jobs_df[integer_columns].apply( pd.to_numeric, errors='coerce' ).fillna(0).astype('Int64')
    #duration_columns = ['elapsed','timelimit']
    jobs_df['timelimit'] = jobs_df['timelimit'].apply( pd.to_timedelta, errors='coerce', unit='m')
    jobs_df['elapsed'] = jobs_df['elapsed'].apply( pd.to_timedelta, errors='coerce', unit='s')

    #print(jobs_df['elapsed'])

    jobs_df['maxrss'] = pd.to_numeric(jobs_df['maxrss'])
    jobs_df['nnodes'] = pd.to_numeric(jobs_df['nnodes'])
    jobs_df['reqcpus'] = pd.to_numeric(jobs_df['reqcpus'])

    # Construct alloc_mem column
    jobs_df['memHold'] = jobs_df['reqmem'].map(
        lambda x: int(x.lstrip('+-').rstrip('MmNnCc')))
    core_mask = (jobs_df['reqmem'].str.contains('c'))
    node_mask = (jobs_df['reqmem'].str.contains('n'))

    jobs_df.loc[core_mask, 'memHold'] = (
        jobs_df['reqcpus'] * jobs_df['memHold'])
    jobs_df.loc[node_mask, 'memHold'] = (
        jobs_df['nnodes'] * jobs_df['memHold'])
    jobs_df = jobs_df.rename(columns={'memHold': 'mem'})

    jobs_df['submit'] = pd.to_datetime(jobs_df['submit'])

    if debugging:
        print('Done column building')
        
    return jobs_df





def job_scat(jobs_frame, x_var='',y_var='',c_var='',s_var='', title='',var_labels=''):
    
    jobs_frame['eligible_wait'] = jobs_frame['start'] - jobs_frame['eligible']
    jobs_frame['eligible_wait_sec']=jobs_frame['eligible_wait'] / np.timedelta64(1, 's')
    jobs_frame['eligible_wait_time']=pd.to_timedelta(jobs_frame['eligible_wait_sec'], unit='s')
    jobs_frame['eligible_wait_hours']=jobs_frame['eligible_wait_sec']/3600
    
    jobs_frame['eligible_delta'] = jobs_frame['eligible'] - jobs_frame['submit']
    jobs_frame['eligible_delta_sec']=jobs_frame['eligible_delta'] / np.timedelta64(1, 's')
    jobs_frame['eligible_delta_time']=pd.to_timedelta(jobs_frame['eligible_delta_sec'], unit='s')
    jobs_frame['eligible_delta_hours']=jobs_frame['eligible_delta_sec']/3600

    jobs_frame['mem_per_node'] = jobs_frame['mem'] / jobs_frame['nnodes']
    jobs_frame['mem_per_cpu'] = jobs_frame['mem'] / jobs_frame['reqcpus']
    jobs_frame['mem_delta'] = jobs_frame['mem'] - jobs_frame['maxrss']

    jobs_frame['elapsed_hours'] = jobs_frame['elapsed'] / 3600
    jobs_frame['timelimit_hours'] = jobs_frame['timelimit'] / 3600

    jobs_frame['time_delta_hours'] = jobs_frame['timelimit_hours'] - jobs_frame['elapsed_hours']
    jobs_frame['time_delta_norm'] = jobs_frame['time_delta_hours'] / jobs_frame['timelimit_hours']

    
    fig = px.scatter(jobs_frame,
                    x=x_var,
                    y=y_var,
                    opacity=.3,
                    color=c_var,
                    #size=s_var,
                    labels=var_labels,
                    marginal_y="histogram",
                    marginal_x="histogram",
                    title=title,
                    hover_data={
                            'jobid',
                            'state',
                            'submit',
                            'start',
                            'eligible',
                            'eligible_wait_hours',
                            'timelimit_hours',
                            'elapsed',
                            'mem_per_node',
                            'mem',
                            'maxrss',
                            'nnodes',
                            'priority'})
    fig.show()

def job_scat_3d(jobs_frame, x_var='',y_var='',c_var=''):
    
    jobs_frame['eligible_wait'] = jobs_frame['start'] - jobs_frame['eligible']
    jobs_frame['eligible_wait_sec']=jobs_frame['eligible_wait'] / np.timedelta64(1, 's')
    jobs_frame['eligible_wait_hours']=jobs_frame['eligible_wait_sec']/3600
    jobs_frame['mem_per_node'] = jobs_frame['mem'] / jobs_frame['allocnodes']

    
    fig = px.scatter_3d(jobs_frame,
                        x=x_var,
                        y=y_var,
                        z='mem_per_node',
                        opacity=.3,
                        color=c_var,
                        hover_data={
                            'jobid',
                            'submit',
                            'start',
                            'eligible',
                            'eligible_wait_hours',
                            'timelimit_sec',
                            'elapsed',
                            'mem_per_node',
                            'nnodes',
                            'priority'})
    fig.show()
