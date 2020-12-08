import os
import pandas as pd 
import time
import json
import tldextract
import hdbscan
from sklearn.metrics import pairwise_distances
from sklearn.cluster import DBSCAN
from sklearn.metrics import silhouette_samples, silhouette_score
from sklearn.neighbors import NearestNeighbors
import seaborn as sns

from pprint import pprint
from collections import defaultdict
                
sw_files =[]
sw_tokens= defaultdict()
sw_ast_dir_path='../../SWSec_Data/SW_ASTs/'

def get_service_worker_files():         
        from pyjsparser import parse 
        sw_dir_path = '../../SWSec_Data/ServiceWorkers/'
        sw_ast_dir_path = '../../SWSec_Data/SW_ASTs/'
        for file in os.listdir(sw_dir_path):
                # if not any([n in file for n in ['403065', '308982','45963' ]]):
                if os.path.getsize(sw_dir_path+file)<60:
                        continue
                if os.path.exists(sw_ast_dir_path+file.replace('.js','.txt')):
                        continue

                print('--------------------------------')
                print(file)
                print('---------------------------------')
                try:
                        ast = None
                        with open(sw_dir_path+file, 'r') as f:
                                js_code = f.read()
                               
                                js_code = js_code.replace('\\n\\n','; ').replace('\\n','\n').replace('\\t','\t').replace('\\"','\"')
                                # print(js_code.rfind('\"'))
                                js_code = js_code[1:js_code.rfind('\"')]
                                # print(len(js_code))
                                js_code = js_code.decode('unicode_escape')
                                
                                # print(js_code)          
                                # print('\n\n')    
                                
                                ast = parse(js_code)
                                # pprint(ast,indent=2, width=50)  
                        if ast!=None:   
                                with open(sw_ast_dir_path+file.replace('.js','.txt'),'w') as f:
                                        json.dump(ast,f,indent=2)
                                
                        
                except Exception as e:
                        print(e)
                        # break
                        continue
                                

"""Extract nested values from a JSON tree."""

def json_extract(file, key):
    """Recursively fetch values from nested JSON."""
    global sw_ast_dir_path
    arr = []
    ast = None

    with open(sw_ast_dir_path+file,'r') as f:
        ast = json.load(f)

    def parse_value(val):
        if not isinstance(val,str):
                return val
        if 'http' in val:
                ext = tldextract.extract(val)
                return '.'.join(ext[:2])
        elif '/' in val:
                return val.split('/')[-1]
        return val
        
    
    def extract(obj, arr, key, level):
        
        level +=1
        """Recursively search for values of key in JSON tree."""
        if isinstance(obj, dict):
            for k, v in obj.items():
                if isinstance(v, (dict, list)):
                        extract(v, arr, key, level)
                elif k in key:
                        arr.append((level,parse_value(v)))
                                          
        elif isinstance(obj, list):
            for item in obj:
                extract(item, arr, key, level)
        # arr.append(child_arr)
        return arr

    values = extract(ast, arr, key,-1)
    return values


def tokenize(tokens):
        tokens_level = defaultdict(set) 
        for l,t in tokens:
                
                if isinstance(t,unicode):
                        t = t.encode('ascii','ignore')
                tokens_level[l].add(str(t))                
        tokens = set([' '.join(v) for k,v in tokens_level.items()])
        return tokens

def calculate_distance(ind1, ind2):
        global sw_files
        global sw_tokens

        sw_ast_dir_path='../../SWSec_Data/SW_ASTs/'  
        file1=sw_files[int(ind1[0])]
        file2=sw_files[int(ind2[0])]

        def get_tokens(file):
                
                if file in sw_tokens:
                        return sw_tokens.get(file)
                
                
                tokens = json_extract(file,['type','value'])
                tokens = tokenize(tokens)
                sw_tokens[file]=tokens
                return tokens

        def jaccard_dist(t1,t2):
                intersection_count = len(t1.intersection(t2))
                union_count = len(t1.union(t2))
                return float(intersection_count)/union_count

        tokens_1 = get_tokens(file1)
        tokens_2 = get_tokens(file2)
        dst = jaccard_dist(tokens_1,tokens_2)

        # print(file1,file2,dst)
        return dst


def cluster_sw_asts():
        global sw_files 

        
        sw_files = os.listdir(sw_ast_dir_path)
        print(len(sw_files))
        indices = [[i] for i in range(len(sw_files))]
        dist_matrix = pairwise_distances(indices, metric=calculate_distance)
        # clus = hdbscan.HDBSCAN(metric="precomputed")
        # clus.fit(dist_matrix)
        # print(set(clus.labels_))
        # clus.cluster_hierarchy_.plot()
        # pprint(zip(sw_files,clus.labels_))
        # print(dist_matrix)

        do_dbscan(dist_matrix)

def do_dbscan(dist_matrix):
        import numpy as np 
        import matplotlib.pyplot as plt

        neigh = NearestNeighbors(n_neighbors=2,metric='euclidean')
        nbrs = neigh.fit(dist_matrix)
        distances, indices = nbrs.kneighbors(dist_matrix)
        print(distances)    
        distances = np.sort(distances, axis=0)
        distances = distances[:,1]
        plt.plot(distances)    
        # plt.show()

        from sklearn.manifold import TSNE

        tsne = TSNE(n_components=2, verbose=1, perplexity=40, n_iter=300)
        ep_use=0
        
        for ep in range(11,14,1):
                ep_use=float(ep)/10
                print(ep_use)
                labels = DBSCAN(eps=ep_use, min_samples=2).fit_predict(dist_matrix)

                with open('cluster_'+str(ep_use)+'.csv','w') as fout:
                        for f,cluster in zip(sw_files,labels):
                                tokens = tokenize(json_extract(f,['name']))
                                tokens_arr = []
                                for t in tokens:
                                        if ' ' in t:
                                                tokens_arr = tokens_arr + [ti  for ti in t.split(' ') if len(ti)>3]
                                        elif len(t)>3:
                                                tokens_arr.append(t)
                                         
                                tokens = ' ** '.join(list(set(tokens_arr)))
                                fout.write(','.join([ f,str(cluster),str(os.path.getsize(sw_ast_dir_path+f)), tokens ]) +'\n')

                
                def plot_tsne():
                        # X_subset = [ X_array[i] for i in indices ]
                        # X_labels = [labels[i] for i in indices]
                        colors = len(set(labels))

                        tsne_results = tsne.fit_transform(dist_matrix)
                        print(colors)
                        plt.figure(figsize=(16,10))
                        plt.title('Cluster Number :' + str(ep))
                        sns.scatterplot(
                        x=tsne_results[:,0], y=tsne_results[:,1],
                        hue=labels,           
                        palette= sns.color_palette('hls', n_colors=colors),         
                        legend="full",
                        size = labels,
                        alpha=0.8
                        )
                        plt.legend(scatterpoints=1, frameon=False, labelspacing=1)
                        plt.show()
                        
                # plot_tsne()
                unlabeled = list(filter(lambda x:x==-1,labels))
                # print(len(unlabeled))
                # The silhouette_score gives the average value for all the samples.
                # This gives a perspective into the density and separation of the formed
                # clusters
                silhouette_avg = silhouette_score(dist_matrix, labels)
                print("For eps = ", ep_use,"n_clusters =", max(labels),
                        "The average silhouette_score is :", silhouette_avg)
        


def do_hierarchy():
    from scipy.cluster.hierarchy import dendrogram, linkage
    from sklearn.cluster import AgglomerativeClustering
    from matplotlib import pyplot as plt

    # linked = linkage(X_array, 'ward')
    # plt.figure(figsize=(10, 7))
    # dendrogram(linked,
    #             orientation='top',                
    #             distance_sort='descending',
    #             show_leaf_counts=True)
    # plt.show()
    method= 'ward'
    from sklearn import metrics
    points_average = [] 
    labels_average= []
    points_complete = []
    labels_complete= [] 
    values_in_range = []
    for x in range( 10,20,1 ):     
        values_in_range.append( x )
        cluster_topics = AgglomerativeClustering( n_clusters=None, affinity='euclidean', linkage=method, distance_threshold=x)
        model_topics = cluster_topics.fit(X_array)
        
        labels_average.append(  model_topics.labels_ )
        
        if len( np.unique(model_topics.labels_) )<= 2  :
            break
            
        score = metrics.silhouette_score(X_array, model_topics.labels_ , metric='euclidean')
        
        points_average.append( [ x, score ] )

    plt.plot( [x[0] for x in points_average],[x[1] for x in points_average] )
    plt.title( 'average method/ title+body hirarchical model silhuet score' )
    plt.xlabel( 'cut off threshold' )
    plt.ylabel('Silhuent Score')
    plt.show()
                        
def main():                      
        get_service_worker_files()   
        cluster_sw_asts()             
                

if __name__ == "__main__":
        main()
