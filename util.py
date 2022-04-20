import scipy.io as scio
from scipy import signal
import pandas as pd
import numpy as np

data_path = "/home/melodia/data/MEA_grasp/datasets_matlab/"
electrodeID_path = '/home/melodia/proj/BCI_Project/metadata/' #path to git repo CSV files

all_data = {}
all_data['N'] = {i: scio.loadmat(data_path + 'i140703-001_raw-lfp-spikes_ch{}.mat'.format(str(i).zfill(2))) for i in range(1,97)}
all_data['L'] = {i: scio.loadmat(data_path + 'l101210-001_raw-lfp-spikes_ch{}.mat'.format(str(i).zfill(2))) for i in range(1,97)}

def get_trial_time_and_label(monkey, event_want='GO-ON'):
    assert monkey in ['L', 'N']
    data = all_data[monkey][1]
    event_data = data['block']['segments'][0][0][0][0][0][0]['events'][0][2][0][0]
    assert event_data['name'] == 'TrialEvents'
    assert event_data['times_units'] == '(1.0/30000 * s)'
    samples = []
    t_trial = None
    lb_trial = None
    valid_trial = True
    valid_trial2 = False
    for event, label, time in zip(event_data['an_trial_event_labels'],
                            event_data['an_belongs_to_trialtype'],
                            event_data['times'][0]):
        if event.strip() == event_want.strip():
            t_trial = time/30000
            lb_trial = label
        if 'ERROR' in event:
            valid_trial = False
        if 'RW-ON' in event:
            valid_trial2 = True
        if event[:5] in ['TS-ON', 'NONE ']:
            if valid_trial and valid_trial2 and lb_trial:
                samples.append((t_trial, lb_trial))
            t_trial = None
            lb_trial = None
            valid_trial = True
    return samples

def get_electrodes(monkey_name, x, y, step):
    chunk_channel_id=[]
    assert monkey_name in ['L', 'N']
    if monkey_name=='L':
        df=pd.read_csv(electrodeID_path+'L.csv')
    else:
        df=pd.read_csv(electrodeID_path+'N.csv')   
    monkey_electrodes_id=df['Id'].tolist()
    start=(y-1)*10+x
    for col in range (0, step):
        for row in range (0,step):
            chunk_channel_id.append(monkey_electrodes_id[start+10*row-1])
        start=start+1   
    return chunk_channel_id

def get_st_feat(monkey, ch, start_time, window_time):
    data = all_data[monkey][ch]
    tmp = data['block']['segments'][0][0][0][0][0][0]['spiketrains'][0]
    st = None
    for i in range(tmp.shape[0]):
        if tmp[i][0][0]['an_unit_id'].item() == 1: st = tmp[i][0][0]
        elif tmp[i][0][0]['an_unit_id'].item() == 0 and st is None: st = tmp[i][0][0]
    assert st['times_units'].item() == '(1.0/30000 * s)'
    st['times'][0]
    st_op = start_time*30000
    st_ed = (start_time+window_time)*30000
    return ((st['times'][0] >= st_op) & (st['times'][0] < st_ed)).sum()

def get_lfp_feat(monkey, ch, start_time, window_time):
    data = all_data[monkey][ch]
    lfp_data = data['block']['segments'][0][0][0][0][0][0]['analogsignals'][0][0][0][0]#['file_origin'][0][-3:]
    assert lfp_data['file_origin'][0][-3:] == 'ns2'
    assert lfp_data['t_start_units'] == '(1.0/1000.0*s)'
    start_time_shifted = start_time - lfp_data['t_start'].item()
    op = int(start_time_shifted*1000)
    ed = int((start_time_shifted+window_time)*1000)
    sig = lfp_data['signal'].squeeze()[op:ed]
    freqs, psd = signal.welch(sig, 1000, nperseg=500)
    return psd[2:6]

def get_all_feat_and_labels(monkey, event_want, offset, window_time):
    trials = get_trial_time_and_label(monkey, event_want)

    all_feat = {}

    for ch in range(1,97):
        st_feat = []
        if monkey == 'N': lfp_feat = []
        for trial_t, label in trials:
            start_time = trial_t + offset
            st_feat.append(get_st_feat(monkey, ch, start_time, window_time))
            if monkey == 'N': lfp_feat.append(get_lfp_feat(monkey, ch, start_time, window_time))
        all_feat[ch] = {'st_feat': np.stack(st_feat)}
        if monkey == 'N': all_feat[ch]['lfp_feat'] = np.stack(lfp_feat)
    labels = np.stack([trial[1] for trial in trials])
    
    return all_feat, labels