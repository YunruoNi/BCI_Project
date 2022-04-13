import scipy.io as scio

data_path = "/home/melodia/data/MEA_grasp/datasets_matlab/"

def get_trial_time_and_label(monkey, event_want='GO-ON'):
    assert monkey in ['L', 'N']
    if monkey == 'L':
        data_file = data_path + 'l101210-001_raw-lfp-spikes_ch12.mat'
    elif monkey == 'N':
        data_file = data_path + 'i140703-001_raw-lfp-spikes_ch02.mat'

    data = scio.loadmat(data_file)
    event_data = data['block']['segments'][0][0][0][0][0][0]['events'][0][2][0][0]
    assert event_data['name'] == 'TrialEvents'
    assert event_data['times_units'] == '(1.0/30000 * s)'
    samples = []
    t_trial = None
    lb_trial = None
    valid_trial = True
    for event, label, time in zip(event_data['an_trial_event_labels'],
                            event_data['an_belongs_to_trialtype'],
                            event_data['times'][0]):
        if event.strip() == event_want.strip():
            t_trial = time/30000
            lb_trial = label
        if 'ERROR' in event:
            valid_trial = False
        if event[:5] in ['TS-ON', 'NONE ']:
            if valid_trial and lb_trial:
                samples.append((t_trial, lb_trial))
            t_trial = None
            lb_trial = None
            valid_trial = True
    return samples