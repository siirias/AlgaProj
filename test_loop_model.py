import os
import algae_tools as agt
conf_dat = agt.conf_dat
oper_dir = conf_dat['oper_dir']
output_dir = conf_dat['output_dir']
config_dir = conf_dat['config_dir']
agt.read_cmd_params()
if(os.path.isfile(oper_dir + 'last_step.txt')):
    os.remove(oper_dir + 'last_step.txt')
for i in range(90):
    os.system('python run_model.py')
