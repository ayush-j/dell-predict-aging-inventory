import os 
import torch
import torch.nn as nn
from  torch.autograd  import Variable
import torch.optim as optim 
import pandas as pd
import random
import model as m
import zerorpc
import json
os.chdir('C:/Users/ayush/Dropbox/MUJ V Sem/dell-aging-inventory/data')

class model(nn.Module):
    
    def __init__(self):
        super(model , self ).__init__()
        self.layers = nn.Sequential(
                nn.Linear(36, 72),
                nn.ReLU(),
                nn.Linear(72, 144),
                nn.ReLU(),
                nn.Linear(144, 36),
                nn.ReLU(),
                nn.Linear(36, 18),
                nn.ReLU(),
                nn.Linear(18 , 9),
                nn.ReLU(),
                nn.Linear(9 , 1),                
                nn.Sigmoid())
        
    
    def forward(self , x ):

        return self.layers(x)



class master_model(nn.Module):
    
    def __init__(self):
        
        super(master_model ,self ).__init__()
        self.layers = nn.Sequential(
                            nn.Linear(2 , 11),
                            nn.ReLU(),
                            nn.Linear(11 , 22),
                            nn.ReLU(),
                            nn.Linear(22 , 44),
                            nn.ReLU(),
                            nn.Linear(44 , 88),
                            nn.ReLU(),
                            nn.Linear(88 , 44),
                            nn.Softmax()
                )
        
            
    def forward ( self , x ):
        return self.layers( x )

def encode_locations(loc = None):
    encode = [0 for i in range(34)]
    flag = False
    for i in range(len(locations)):
        if locations[i] == loc :
            flag = True
            break
    if flag :
        encode[i] = 1
    return encode

models  = []
main_model = master_model()
main_model.load_state_dict(torch.load('main_model_saved.pkl'))
main_model.eval()
for i in range(10):
    mod = model()
    mod.load_state_dict(torch.load('saved_state_of_logistic{0}.pkl'.format(i+1)))
    mod.eval()
    models.append(mod)
locations = pd.read_csv('./csv2/location.csv' , header = None).values.tolist()[0]
ratings = pd.read_csv('./csv2/rating.csv' , header = None).values.tolist()[0]


def predict_logistic(y):
    # input as 'logisticnumber,price,city/optional'
    y = list(y.split(","))
    logistic_number =int( y[0]) - 1
    del(y[0])
    if len(y) == 1 :
        y.append(None)
    input = []
    input.append(int(y[0]) / 312499)
    input.extend(encode_locations(y[1]))
    input.append(ratings[logistic_number] / 5)
    input = Variable(torch.FloatTensor(input))
    pred = models[logistic_number].forward(input)
    pred = pred.data.tolist()
    pred = str(int(pred[0] * 120))
    return pred


def predict_main(x):
    #x has value as price
    price = int(x)
    x = price/312499
    input = []
    input.append(x) #price
    input.append(ratings[random.randint(0 , 9)] / 5)
    input = Variable(torch.FloatTensor(input))
    pred = main_model.forward(input)
    pred = pred.data.tolist()
    location = pred[0 : 34]
    logistic = pred[34 :]
    _ , l ,pred = m.mod(location , logistic)
    loc ,_ ,  log = m.mod(location  , logistic)
    location = locations[loc]
    logistic = log
    response = '{0},{1},{2}'.format(location , logistic + 1 , predict_logistic(str('{0},{1},{2} '.format(logistic , price ,location ))))
    return response       
    


class NodeCOMM(object):
    def predict(self, data):
        data = json.loads(data)
        resp = []
        for x in data:
            p = predict_main(x)
            resp.append(str(p))
        return '|'.join(resp)

    def PING(self, data):
        return 'PONG'

s = zerorpc.Server(NodeCOMM())
s.bind("tcp://0.0.0.0:8679")
s.run()