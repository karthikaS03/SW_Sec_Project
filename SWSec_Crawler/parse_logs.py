import os
import math
import json

import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

from collections import defaultdict
from matplotlib.colors import LogNorm
from pprint import pprint


dir_path = './logs/'


all_tokens= list(set(['{Headers}', '{IDBRequest}',  '{IDBDatabase}',  '{PushManager}',
 '{ServiceWorkerRegistration}',  '{ExtendableMessageEvent}',  '{IDBRequest}',
 '{IDBDatabase}',  '{MessageChannel}',  '{Response}',  '{IDBObjectStore}',
 '{URLSearchParams}',  '{ServiceWorkerRegistration}',  '{Cache}', 
 '{NavigationPreloadManager}',  '{IDBCursorWithValue}',  '{Request}',  '{Iterator}',
 '{ReadableStream}',  '{IDBFactory}',  '{WorkerNavigator}',  '{NavigationPreloadManager}',
  '{ServiceWorker}',  '{InstallEvent}',  '{Event}',  '{Headers}',  '{WindowClient}',
 '{IDBCursorWithValue}', '{IDBOpenDBRequest}',  '{WindowClient}',
  '{ExtendableEvent}',  '{Iterator}',  '{MessageChannel}',  '{Request}',  '{IDBVersionChangeEvent}',
  '{IDBVersionChangeEvent}',  '{Crypto}',  '{UnderlyingSourceBase}',  '{UnderlyingSourceBase}',
 '{IDBIndex}',  '{ServiceWorkerGlobalScope}',  '{ServiceWorkerGlobalScope}',
 '{URL}',  '{IDBTransaction}',  '{WorkerLocation}',  '{Cache}',  
 '{URL}',  '{FetchEvent}',  '{FormData}',  '{PushManager}',  '{Event}',  '{Clients}',
 '{MessagePort}',  '{ExtendableMessageEvent}',  '{CacheStorage}',  '{Response}',
 '{CacheStorage}',  '{WorkerLocation}',  '{WorkerNavigator}',  '{IDBOpenDBRequest}',
 '{FetchEvent}',  '{URLSearchParams}',  '{IDBObjectStore}',  '{DOMStringList}',
  '{Clients}']))


def plot_heatmap(token_freq):

    fig, ax = plt.subplots()
    im = ax.imshow(token_freq)

    # We want to show all ticks...
    ax.set_yticks(np.arange(100))
    ax.set_xticks(np.arange(len(all_tokens)))
    # ... and label them with the respective list entries
    ax.set_yticklabels(range(100))
    ax.set_xticklabels(all_tokens)

    # Rotate the tick labels and set their alignment.
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right",
            rotation_mode="anchor")

   
    ax.set_title("API call frequencies in service workers")
    fig.tight_layout()
    plt.show()


def plot_heatmap_sns(token_freq):

    log_norm   = LogNorm(vmin=token_freq.min().min(), vmax=token_freq.max().max())
    cbar_ticks = [math.pow(10, i) for i in range(int(token_freq.min().min()), 
                    int(1+math.ceil(math.log10(token_freq.max().max()))))]
    print(cbar_ticks)
    ax = sns.heatmap(token_freq, center=0, 
            cmap='summer', 
            vmin=2, vmax=5000,
            norm = log_norm,
            cbar_kws={"ticks": cbar_ticks}
    )

    # We want to show all ticks...
    ax.set_yticks(np.arange(100))
    ax.set_xticks(np.arange(len(all_tokens)))
    # ... and label them with the respective list entries
    ax.set_yticklabels(range(100))
    ax.set_xticklabels(all_tokens)
    
    # Rotate the tick labels and set their alignment.
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right",
            rotation_mode="anchor")

   
    ax.set_title("API call frequencies in service workers")
    plt.tight_layout()
    plt.show()


def parse_sw_logs():

    all_tokens_dict = np.zeros((100,len(all_tokens)))+1

    def get_tokens(sw_file):
        tokens_dict ={}
        with open(sw_file,'r') as f:
            line = f.readline()
            
            while line:
                tokens = line.split(':')[1:3]
                # print(tokens)
                for t in tokens:
                    t = t.replace('\n','')
                    if t in all_tokens:
                        tokens_dict[t] = tokens_dict.get(t,1) +1
                        
                line = f.readline()

        return tokens_dict

    for dir in os.listdir(dir_path):
        log_path = os.path.join(dir_path,dir)
        print(dir)
        for log in os.listdir(log_path):
            if 'ServiceWorker' in log and '.log' in log:
                print(log)
                tokens_dict = get_tokens(os.path.join(log_path,log))
                # pprint(tokens_dict)
                
                for k,v in tokens_dict.items():
                    all_tokens_dict[int(dir)][all_tokens.index(k)]=v 

                with open(os.path.join(log_path,log.replace('.log','_tokens.json')),'w') as f:
                    json.dump(tokens_dict,f,indent=2)
    pprint(all_tokens_dict)
    # all_tokens_dict = np.log2(all_tokens_dict)
    plot_heatmap_sns(all_tokens_dict)
    # pprint(all_tokens_dict.keys())
    # with open(dir_path+'/sw_tokens.json','w') as fw:
    #     json.dump(all_tokens_dict,fw,indent=2)


if __name__ =='__main__':

    parse_sw_logs()

            