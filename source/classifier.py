
import os
import sys
import time
import numpy as np
from netinfo import *
from datetime import datetime
from keras.preprocessing import image
from sklearn import svm
from sklearn.externals import joblib
import matplotlib.pyplot as plt
from sklearn.metrics import confusion_matrix

start = time.time()

net_name = sys.argv[1]
crop_mode = sys.argv[2]
 
print(crop_mode)

if(crop_mode != "full"):
    crop_modes = { 
        "bottom-right":  (4/5, 2/3, 1, 1), 
        "top-left":  (0, 0, 1/5, 1/3),
        "top-right": (0, 2/3, 1/5, 1),
        "bottom-left": (0, 2/3, 1/5, 1), 
    }

    mode = crop_modes[crop_mode]
    crop_x1 = mode[0]
    crop_y1 = mode[1]
    crop_x2 = mode[2]
    crop_y2 = mode[3]


# Check if the model is trained
if not os.path.exists('../models/labels_' + net_name + '.txt') or not os.path.exists('../models/'+net_name+'.model'):
    print("Error: there is no trained model for " + net_name)

# Create report file
if not os.path.exists("../reports/"):
    os.mkdir("../reports/")
    #%m/%d/%Y, %H:%M:%S
freport_name = "../reports/" + net_name + "_" + crop_mode + "_report_{}".format(datetime.now().strftime("%Y_%m_%d_%H_%M_%S"))
freport = open(freport_name + ".txt", "w+")
freport.write(net_name + " " + crop_mode + "\n")
freport.write("FAILED:\n\n")

if(net_name == "vgg16"):
    from keras.applications.vgg16 import VGG16
    from keras.applications.vgg16 import preprocess_input as preprocess_vgg
    modelClass = VGG16
    preprocess_function = preprocess_vgg 

if(net_name == "inception"):
    from keras.applications.inception_v3 import InceptionV3
    from keras.applications.inception_v3 import preprocess_input as preprocess_inception
    modelClass = InceptionV3
    preprocess_function = preprocess_inception 

if(net_name == "mobilenet"):
    from keras.applications.mobilenet_v2 import MobileNetV2
    from keras.applications.mobilenet_v2 import preprocess_input as preprocess_mobilenet
    modelClass = MobileNetV2
    preprocess_function = preprocess_mobilenet 

if(net_name == "resnetv2"):
    from keras.applications.inception_resnet_v2 import InceptionResNetV2
    from keras.applications.inception_resnet_v2 import preprocess_input as preprocess_resnetv2
    modelClass = InceptionResNetV2
    preprocess_function = preprocess_resnetv2 
    
if(net_name == "nas"):
    from keras.applications.nasnet import NASNetLarge
    from keras.applications.nasnet import preprocess_input as preprocess_nas
    modelClass = NASNetLarge
    preprocess_function = preprocess_nas
    

if(net_name == "dense"):
    from keras.applications.densenet import DenseNet201
    from keras.applications.densenet import preprocess_input as preprocess_dense
    modelClass = DenseNet201
    preprocess_function = preprocess_dense

if(net_name == "resnet"):
    from keras.applications.resnet_v2 import ResNet152V2
    from keras.applications.resnet_v2 import preprocess_input as preprocess_resnet
    modelClass = ResNet152V2
    preprocess_function = preprocess_resnet

if(net_name == "resnext"):
    from keras.applications.resnext import ResNeXt101
    from keras.applications.resnext import preprocess_input as preprocess_resnext
    modelClass = NASNetLarge
    preprocess_function = preprocess_resnext
    
if(net_name == "vgg19"):
    from keras.applications.vgg19 import VGG19
    from keras.applications.vgg19 import preprocess_input as preprocess_vgg19
    modelClass = VGG19
    preprocess_function = preprocess_vgg19

feat_size = features_sizes[net_name]
input_size = input_sizes[net_name]

with open('../models/labels_' + net_name + '.txt') as f:
    labels_names = [os.path.splitext(line.strip()) for line in f]


print("Extracting features Using "+net_name+" net")
extractor_model = modelClass(weights='imagenet', include_top=False)
print(labels_names)
test_path = "../test/"
correct = 0
count = 0
y_true = []
y_pred = []
print("Loading model " + net_name)
model = joblib.load('../models/'+net_name+'.model')
for dirname in os.listdir(test_path):
    for fname in os.listdir(test_path + dirname):

        #skip unused directories
        if not (dirname) in labels_names:
            continue

        #load target image
        img_path = test_path + dirname + "/" + fname 
        #img_path = "/home/empo/Scrivania/progettottr/dset/overwatch/Overwatch 2019-06-01 09-33-21-84.bmp"
        img = image.load_img(img_path)
        if(crop_mode != "full"): 
                img = img.crop((crop_x1 * img.width, crop_y1 * img.height, crop_x2 * img.width, crop_y2 * img.height,)) 
           
        img = img.resize(input_size)
        img_data = image.img_to_array(img)
        img_data = np.expand_dims(img_data, axis=0)
        img_data = preprocess_function(img_data)
        
        features = extractor_model.predict(img_data).flatten() 

        label_truth = labels_names.index(dirname)
        label_predicted = model.predict(np.asmatrix(features)) 
        
        #print("probability: " + str(model.predict_proba(np.asmatrix(features)))) 
         
        y_true.append(label_truth) 
        y_pred.append(label_predicted)
        if(label_predicted == label_truth):
            correct += 1
            print("[v] " + fname + " | predicted: " + str(labels_names[int(label_predicted)])) 
        else :
            print("[ ] " + fname + " | predicted: " + str(labels_names[int(label_predicted)]))
            freport.write(fname + " | predicted: " + str(labels_names[int(label_predicted)]) + "\n")
        count += 1

print("ratio: " + str((correct / count) * 100) + "%")
freport.write("\n----------------------\n\nRatio: " + str((correct / count) * 100) + "%")

##########################
#### CONFUSION MATRIX ####
##########################
color_map=plt.cm.Blues 
np.set_printoptions(precision=2)

cm = confusion_matrix(y_true, y_pred)
#classes = classes[unique_labels(y_true, y_pred)] # Only use the labels that appear in the data 
print('Confusion ,matrix')
print(cm)

fig, ax = plt.subplots()
im = ax.imshow(cm, interpolation='nearest', cmap=color_map)
ax.figure.colorbar(im, ax=ax)
# We want to show all ticks...
ax.set(xticks=np.arange(cm.shape[1]),
        yticks=np.arange(cm.shape[0]),
        # ... and label them with the respective list entries
        xticklabels=labels_names, yticklabels=labels_names,
        title= 'Confusion matrix ' + net_name + " " + crop_mode,
        ylabel='Ground truth',
        xlabel='Predicted')


# Rotate the tick labels and set their alignment.
plt.setp(ax.get_xticklabels(), rotation=45, ha="right",
            rotation_mode="anchor")

# Loop over data dimensions and create text annotations.
thresh = cm.max() / 2.
for i in range(cm.shape[0]):
    for j in range(cm.shape[1]):
        ax.text(j, i, format(cm[i, j], 'd'),
                ha="center", va="center",
                color="white" if cm[i, j] > thresh else "black")
fig.tight_layout()

#plt.show()
plt.savefig(freport_name + ".png")

print("Execution time:" + str(time.time() - start))