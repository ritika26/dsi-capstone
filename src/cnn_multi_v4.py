from keras.models import Sequential
from keras.layers import Dense, Dropout, Activation, Flatten
from keras.layers import Convolution2D, MaxPooling2D, AveragePooling2D
from keras.layers.convolutional import Conv2D
from keras.utils import np_utils
from keras import backend as K
from keras.callbacks import EarlyStopping
from keras.callbacks import TensorBoard
import pandas as pd
import numpy as np
from keras.layers.normalization import BatchNormalization
from keras.optimizers import SGD, Adadelta
from sklearn.model_selection import train_test_split
from sklearn.metrics import recall_score
from sklearn.metrics import precision_score
# from imblearn.over_sampling import SMOTE
import os

np.random.seed(1337)


def split_data(X, y, test_data_size):
    '''
    Split data into test and training datasets.
    INPUT
        X: NumPy array of arrays
        y: Pandas series, which are the labels for input array X
        test_data_size: size of test/train split. Value from 0 to 1
    OUPUT
        Four arrays: X_train, X_test, y_train, and y_test
    '''
    return train_test_split(X, y, test_size=test_data_size, random_state=42)


def reshape_data(arr, img_rows, img_cols, channels):
    '''
    Reshapes the data into format for CNN.
    INPUT
        arr: Array of NumPy arrays.
        img_rows: Image height
        img_cols: Image width
        channels: Specify if the image is grayscale (1) or RGB (3)
    OUTPUT
        Reshaped array of NumPy arrays.
    '''
    return arr.reshape(arr.shape[0], img_rows, img_cols, channels)


def cnn_model(X_train, X_test, y_train, y_test, kernel_size, nb_filters, channels, nb_epoch, batch_size, nb_classes):
    '''
    Define and run the Convolutional Neural Network
    INPUT
        X_train: Array of NumPy arrays
        X_test: Array of NumPy arrays
        y_train: Array of labels
        y_test: Array of labels
        kernel_size: Initial size of kernel
        nb_filters: Initial number of filters
        channels: Specify if the image is grayscale (1) or RGB (3)
        nb_epoch: Number of epochs
        batch_size: Batch size for the model
        nb_classes: Number of classes for classification
    OUTPUT
        Fitted CNN model
    '''

    model = Sequential()


    model.add(Conv2D(64, (4,4),
        padding='valid',
        strides=4,
        input_shape=(img_rows, img_cols, channels)))
    model.add(BatchNormalization())
    model.add(Activation('relu'))

    model.add(MaxPooling2D(pool_size=(2,2)))


    model.add(Conv2D(32, (4,4)))
    model.add(BatchNormalization())
    model.add(Activation('relu'))


    model.add(Conv2D(32, (4, 4)))
    model.add(BatchNormalization())
    model.add(Activation('relu'))


    model.add(MaxPooling2D(pool_size=(2,2)))


    model.add(Flatten())
    print("Model flattened out to: ", model.output_shape)


    model.add(Dense(2048))
    model.add(Activation('relu'))
    model.add(Dropout(0.20))


    model.add(Dense(nb_classes))
    model.add(Activation('softmax'))


    model.compile(loss = 'categorical_crossentropy',
                    optimizer='adam',
                    metrics=['accuracy'])


    stop = EarlyStopping(monitor='val_loss',
                            min_delta=0.001,
                            patience=2,
                            verbose=0,
                            mode='auto')


    tensor_board = TensorBoard(log_dir='./Graph', histogram_freq=0, write_graph=True, write_images=True)


    model.fit(X_train,y_train, batch_size=batch_size, epochs=nb_epoch,
                verbose=1,
                validation_split = 0.2,
                # validation_data=(X_test,y_test),
                class_weight= 'auto',
                callbacks=[stop, tensor_board])

    return model



if __name__ == '__main__':

    # Specify GPU's to Use
    os.environ["CUDA_VISIBLE_DEVICES"]="0,1,2,3"

    # Specify parameters before model is run.
    batch_size = 1000

    nb_classes = 3
    nb_epoch = 10


    img_rows, img_cols = 256, 256
    channels = 3
    nb_filters = 32
    # pool_size = (2,2)
    kernel_size = (32,32)

    # Import data
    labels = pd.read_csv("../labels/trainLabels_master_256_v2.csv")
    X = np.load("../data/X_train_256_v2.npy")
    # y = np.array([1 if l >= 1 else 0 for l in labels['level']])
    labels.loc[labels.level == 2, 'level'] = 1
    labels.loc[labels.level == 4, 'level'] = 3
    labels.loc[labels.level == 3, 'level'] = 2
    y = np.array(labels['level'])


    print("Splitting data into test/ train datasets")
    X_train, X_test, y_train, y_test = split_data(X, y, 0.2)

    # print("Applying SMOTE")
    # sm = SMOTE()
    # X_res, y_res = sm.fit_sample(X_train, y_train)

    print("Reshaping Data")
    X_train = reshape_data(X_train, img_rows, img_cols, channels)
    X_test = reshape_data(X_test, img_rows, img_cols, channels)

    print("X_train Shape: ", X_train.shape)
    print("X_test Shape: ", X_test.shape)


    input_shape = (img_rows, img_cols, channels)


    print("Normalizing Data")
    X_train = X_train.astype('float32')
    X_test = X_test.astype('float32')

    X_train /= 255
    X_test /= 255


    y_train = np_utils.to_categorical(y_train, nb_classes)
    y_test = np_utils.to_categorical(y_test, nb_classes)
    print("y_train Shape: ", y_train.shape)
    print("y_test Shape: ", y_test.shape)


    print("Training Model")


    model = cnn_model(X_train, X_test, y_train, y_test, kernel_size, nb_filters, channels, nb_epoch, batch_size, nb_classes)


    # print("Saving Model")
    # model.save('DR_All_Classes_100_epochs.h5')

    print("Predicting")
    predicted = model.predict(X_test)

    score = model.evaluate(X_test, y_test, verbose=0)
    print('Test score:', score[0])
    print('Test accuracy:', score[1])

    # print("Precision: ", precision_score(y_test, predicted))
    # print("Recall: ", recall_score(y_test, predicted))

    print("Completed")
