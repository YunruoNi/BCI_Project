from util import *
from sklearn.svm import SVC
from sklearn.neural_network import MLPClassifier
from sklearn.preprocessing import StandardScaler

if __name__ == '__main__':
    monkey = 'N'
    all_feat, labels = get_all_feat_and_labels(monkey, 'GO-ON', 0.2, 0.5)
    elecs = get_electrodes(monkey, 8, 1, 3)

    data = []
    for ch in elecs:
        if ch == -1: continue
        data.append(all_feat[ch]['st_feat'][:,None])
    if monkey == 'N':
        for ch in elecs:
            if ch == -1: continue
            data.append(all_feat[ch]['lfp_feat'])
    data = np.concatenate(data, axis=1)

    X_train, y_train, X_test, y_test = data[:120], labels[:120], data[120:], labels[120:]

    # Normalize data
    scaler = StandardScaler()  # normalization: zero mean, unit variance
    scaler.fit(X_train)  # scaling factor determined from the training set

    X_train = scaler.transform(X_train)
    X_test = scaler.transform(X_test)
    # clf = MLPClassifier(hidden_layer_sizes=(50), learning_rate_init=0.01, max_iter=500, verbose=0)
    clf = SVC(kernel='linear', C=1)
    clf.fit(X_train, y_train)

    accuracy = (clf.predict(X_test) == y_test).mean()
    print(accuracy)