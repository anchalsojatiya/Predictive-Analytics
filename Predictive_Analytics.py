# -*- coding: utf-8 -*-
"""Predictive_Analytics_2.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1zzGuGvclsMcyvd1-4hUDAEDJroaWv57F
"""

import pandas as pd
import numpy as np

dataset = np.genfromtxt('data.csv', delimiter=',')
print("dataset" + str(dataset.shape))

dataset = np.delete(dataset,0,0)
print("dataset" + str(dataset.shape))

index = np.random.choice(dataset.shape[0],size=int(dataset.shape[0]*0.75),replace=False)

Y_train=dataset[index,-1]
y_true=dataset[list(set(range(len(dataset))) - set(index)),-1]

train=np.delete(dataset,-1,1)
print("train" + str(train.shape))

X_train=train[index]
X_test=train[list(set(range(len(dataset))) - set(index))]

print("X_train" + str(X_train.shape))
print("Y_train" + str(Y_train.shape))
print("X_test" + str(X_test.shape))
print("y_true" + str(y_true.shape))

def Accuracy(y_true,y_pred):
    """
    :type y_true: numpy.ndarray
    :type y_pred: numpy.ndarray

    :rtype: float
    """
    conf_mat = ConfusionMatrix(y_true,y_pred)
    accuracy = sum([conf_mat[i][i] for i in range(len(np.unique(y_true)))])/len(y_true)
    return accuracy

def Recall(y_true,y_pred):
    """
    :type y_true: numpy.ndarray
    :type y_pred: numpy.ndarray

    :rtype: float
    """
    conf_mat = ConfusionMatrix(y_true,y_pred)
    recall = sum([(conf_mat[i][i])/sum(conf_mat[i]) for i in range(len(np.unique(y_true)))])/len(np.unique(y_true))
    return recall

def Precision(y_true,y_pred):
    """
    :type y_true: numpy.ndarray
    :type y_pred: numpy.ndarray

    :rtype: float
    """

    conf_mat = ConfusionMatrix(y_true,y_pred)
    precision = sum([(conf_mat[i,i])/sum(conf_mat[:,i]) for i in range(len(np.unique(y_true)))])/len(np.unique(y_true))
    return precision

def WCSS(Clusters):
    """
    :Clusters List[numpy.ndarray]
    :rtype: float
    """
    Final_WCSS = 0    
    Row,Column = X_train.shape
    centroid_clusters = np.zeros((X_train.shape))
    sum_squared_clusters = np.zeros(Row)
    
    for j in np.unique(Clusters):
            centroids_val=np.where(Clusters==j)[0]
            centroid_clusters[j]=np.mean(X_train[centroids_val],axis=0)
            for i in centroids_val:
                dist = np.linalg.norm(X_train[i] - centroid_clusters[j])
                sum_squared_clusters[j] += (dist)**2
                
            Final_WCSS += sum_squared_clusters[j]
            
    return Final_WCSS

def ConfusionMatrix(y_true,y_pred):
    """
    :type y_true: numpy.ndarray
    :type y_pred: numpy.ndarray

    :rtype: float
    """ 
    c = len(np.unique(y_true))
    z = y_true*c + y_pred
    conf_mat = np.reshape(list(np.histogram(z,bins = c*c)[0]),(c,c))
    return conf_mat

def KNN(X_train,X_test,Y_train):
    """
    :type X_train: numpy.ndarray
    :type X_test: numpy.ndarray
    :type Y_train: numpy.ndarray

    :rtype: numpy.ndarray
    """
    Y_test=[]
    ind = len(X_train)
    normalized = np.vstack((X_train,X_test))
    r,c = normalized.shape
    val_min=np.zeros(shape=(c))
    val_max=np.zeros(shape=(c))
    for index in range(c):
        val_min[index]=np.min(normalized[:,index])
        val_max[index]=np.max(normalized[:,index])

    data=np.copy(normalized)
    for ind1 in range(r):
        for ind2 in range(c):
            data[ind1,ind2]=(normalized[ind1,ind2]-val_min[ind2])/(val_max[ind2]-val_min[ind2])

    X_train = data[:ind,:]
    X_test = data[ind:len(data)+1,:]
    
    length = len(X_train)

    for i in range(0,len(X_test)):    
        dist = np.sqrt(np.sum((np.asarray(X_train) - X_test[i])**2, axis=1))
        new_data=np.column_stack((dist,np.array(Y_train)))
        sortedArr = new_data[new_data[:,0].argsort()]
        val=np.apply_along_axis(lambda x: np.bincount(x).argmax(), axis=0, arr=sortedArr[0:22,][:,1].astype(int))
        Y_test.append(val)
    return np.array(Y_test)

def RandomForest(X_train,Y_train,X_test):
    """
    :type X_train: numpy.ndarray
    :type X_test: numpy.ndarray
    :type Y_train: numpy.ndarray
    
    :rtype: numpy.ndarray
    """
    import math
    features=6
    tree_depth=5
    random_trees=50
    initial_depth=1
    forest = list()
    x = np.column_stack((X_train,Y_train))
    data = x.copy()

    for n in range(random_trees):
        index = np.random.choice(data.shape[0],size=int((len(x))/random_trees),replace=False)
        tree = data[index]
        data = np.delete(data,index,axis=0)
        tree = build_tree(tree, tree_depth, features)
        forest.append(tree)
    y_pred = [bagging_predict(forest, row) for row in X_test]
    return np.array(y_pred)

def build_tree(tree, tree_depth, features):
    div = get_split(tree, features)
    split(div, tree_depth, features,1)
    return div

def get_split(tree, features):
    div_index, div_value, div_score, div_left ,div_right = 999, 999, 999, None,None

    used_features = np.random.choice(tree.shape[1]-1,size=features,replace=False)

    for ind in used_features:
        tree = tree[tree[:,ind].argsort()]

        for index,row in enumerate(tree):
            left = tree[0:index,:]
            right = tree[index:len(tree),:]

            gini = 0.0
            if len(left) > 0:
                score = 0.0
                unique , count = np.unique(left[:,-1], return_counts=True)
                for val in count:
                    p = val / len(left)
                    score += p * p
                gini += (1.0 - score) * (len(left) / len(tree))

            if len(right) > 0:
                score = 0.0
                unique , count = np.unique(right[:,-1], return_counts=True)
                for val in count:
                    p = val / len(right)
                    score += p * p
                gini += (1.0 - score) * (len(right) / len(tree))

            if gini < div_score:
                div_index, div_value, div_score, div_left ,div_right = ind, row[ind], gini, left, right
    return {'index':div_index, 'value':div_value, 'left':div_left, 'right':div_right}

def split(branch, tree_depth, n_features, depth):
    left = branch['left']
    right = branch['right']
    if (left.size == 0):
        values,counts = np.unique(right[:,-1],return_counts=True)
        index = np.argmax(counts)
        branch['left'] = branch['right'] = values[index]
        return
    elif(right.size == 0):
        values,counts = np.unique(left[:,-1],return_counts=True)
        index = np.argmax(counts)
        branch['left'] = branch['right'] = values[index]
        return
    if depth >= tree_depth:
        values,counts = np.unique(right[:,-1],return_counts=True)
        index = np.argmax(counts)
        branch['right'] = values[index]
        values,counts = np.unique(left[:,-1],return_counts=True)
        index = np.argmax(counts)
        branch['left'] = values[index]
        return
    if len(left) == 1:
        values,counts = np.unique(left[:,-1],return_counts=True)
        index = np.argmax(counts)
        branch['left'] = values[index]
    else:
        branch['left'] = get_split(left, n_features)
        split(branch['left'], tree_depth, n_features, depth+1)
    if len(right) == 1:
        values,counts = np.unique(right[:,-1],return_counts=True)
        index = np.argmax(counts)
        branch['right'] = values[index]
    else:
        branch['right'] = get_split(right, n_features)
        split(branch['right'], tree_depth, n_features, depth+1)

def bagging_predict(forest, row):
    predictions = [predict(tree, row) for tree in forest]
    return max(set(predictions), key=predictions.count)

def predict(branch, row):
    if row[branch['index']] <= branch['value']:
        if isinstance(branch['left'], dict):
            return predict(branch['left'], row)
        else:
            return branch['left']
    else:
        if isinstance(branch['right'], dict):
            return predict(branch['right'], row)
        else:
            return branch['right']

def PCA(X_train,N):
    """
    :type X_train: numpy.ndarray
    :type N: int
    :rtype: numpy.ndarray
    """
    mean_rows=X_train.mean(axis=0)
    Cov_mat = X_train - mean_rows
    u, s, v = np.linalg.svd(Cov_mat, full_matrices = False)
    top_eigens = v[0:N]
    principal_comp = np.dot(Cov_mat,top_eigens.T)
    return principal_comp

def Kmeans(X_train,N):
    """
    :type X_train: numpy.ndarray
    :type N: int
    :rtype: List[numpy.ndarray]
    """
    K =  N
    row_num = X_train.shape[0]
    col_num = X_train.shape[1]
    centroids_val = np.random.randint(0,K,row_num)
    centroid_clusters = np.zeros((K,col_num))
    centroid_clusters_loop = np.zeros((K,col_num))

    for i in range(K):
      new_val = list()
      for ind,j in enumerate(centroids_val):
        if(j==i):
          new_val.append(ind) 

      if(len(new_val)>=1):
        centroid_clusters[i]=np.mean(X_train[new_val],axis=0)
      else:
        centroid_clusters[i]=np.mean(X_train,axis=0)

    niters=100
    for n in range(niters):
      new_dist= [[] for i in range(K)]
      for j in range(K):
        new_dist[j] = (np.linalg.norm(np.subtract(X_train,centroid_clusters[j]),axis = 1))
      centroids_val=np.argmin(new_dist,axis=0)

      for i in range(K):
        new_val1 = list()
        for ind,j in enumerate(centroids_val):
          if(j==i):
            new_val1.append(ind) 
        if(len(new_val1)>=1):
          centroid_clusters_loop[i] = np.mean(X_train[new_val1],axis=0)
        else:
          centroid_clusters_loop[i] = X_train[np.random.randint(len(X_train))]
      
      new_dist1=0
      for i in range(K):
        dist1=[]
        for j in range(K):
          dist1.append(np.linalg.norm(centroid_clusters_loop[i] - centroid_clusters[j]))
        new_dist1 += min(dist1)

        centroid_clusters = np.copy(centroid_clusters_loop)
        
    clusters = [ [] for i in range(len(np.unique(centroids_val))) ]
    for k in np.unique(centroids_val):
      clusters[k] = X_train[np.where(centroids_val==k)]
    return clusters

def SklearnSupervisedLearning(X_train,Y_train,X_test):
    """
    :type X_train: numpy.ndarray
    :type X_test: numpy.ndarray
    :type Y_train: numpy.ndarray
    
    :rtype: List[numpy.ndarray] 
    """
    from sklearn import neighbors
    from sklearn import tree
    from sklearn import svm
    from sklearn import linear_model
    from sklearn import metrics
    from sklearn.preprocessing import StandardScaler
    
    #data normalization
    scaler = StandardScaler()
    norm_val = scaler.fit(np.vstack((X_train,X_test)))
    X_train = norm_val.transform(X_train)
    X_test = norm_val.transform(X_test)

    #SVM
    SVM_2 = svm.SVC(kernel='linear',C=1)
    SVM_2=SVM_2.fit(X=X_train,y=Y_train)
    SVM_pred = SVM_2.predict(X_test)
    acc_svm=metrics.accuracy_score(y_true,SVM_pred)*100

    #Logistic Regression
    Logistic_model = linear_model.LogisticRegression()
    Logistic_model=Logistic_model.fit(X_train, Y_train)
    Logistic_pred = Logistic_model.predict(X_test)
    acc_LR=metrics.accuracy_score(y_true,Logistic_pred)*100

    #Decision Tree
    Decision_Tree = tree.DecisionTreeClassifier()
    Decision_Tree = Decision_Tree.fit(X_train, Y_train)
    Decision_Tree_pred = Decision_Tree.predict(X_test)
    acc_DT=metrics.accuracy_score(y_true,Decision_Tree_pred)*100

    #KNN
    KNN_2 = neighbors.KNeighborsClassifier(n_neighbors=5)
    KNN_2 = KNN_2.fit(X_train, Y_train)
    KNN_pred = KNN_2.predict(X_test)
    acc_KNN=metrics.accuracy_score(y_true,KNN_pred)*100
    
    accuracies=[acc_svm,acc_LR,acc_DT,acc_KNN]
    method=['SVM', 'Logistic Regression','Decision Tree','KNN']
    accuracy_table = pd.DataFrame(zip(method,accuracies), columns = ["Method","Accuracy_Score"] )
    print(accuracy_table)

    return ([SVM_pred,Logistic_pred,Decision_Tree_pred,KNN_pred])

def SklearnVotingClassifier(X_train,Y_train,X_test):
    """
    :type X_train: numpy.ndarray
    :type X_test: numpy.ndarray
    :type Y_train: numpy.ndarray
    
    :rtype: List[numpy.ndarray] 
    """
    from sklearn import ensemble
    from sklearn import neighbors
    from sklearn import tree
    from sklearn import svm
    from sklearn import linear_model
    from sklearn import metrics
    from sklearn.preprocessing import StandardScaler
    
    #data normalization
    scaler = StandardScaler()
    norm_val = scaler.fit(np.vstack((X_train,X_test)))
    X_train = norm_val.transform(X_train)
    X_test = norm_val.transform(X_test)


    SVM_2 = svm.SVC(kernel='linear',C=1)
    SVM_2=SVM_2.fit(X=X_train,y=Y_train)

    Logistic_model = linear_model.LogisticRegression()
    Logistic_model=Logistic_model.fit(X_train, Y_train)

    Decision_Tree = tree.DecisionTreeClassifier()
    Decision_Tree = Decision_Tree.fit(X_train, Y_train)

    KNN_2 = neighbors.KNeighborsClassifier(n_neighbors=5)
    KNN_2= KNN_2.fit(X_train, Y_train)

    voting_classifier = ensemble.VotingClassifier(estimators=[
                                ('SVM', SVM_2),
                                ('LogisticRegression', Logistic_model), 
                                ('DecisionTree', Decision_Tree), 
                                ('KNN', KNN_2)], voting='hard')
     
    voting_classifier.fit(X_train, Y_train)
    vote_pred = voting_classifier.predict(X_test)
    print("Accuracy of Voting Classifier = "+str(metrics.accuracy_score(y_true, vote_pred)*100))

    return ([vote_pred])

def confusion_plot(X_train,Y_train,X_test,y_true):
    import matplotlib.pyplot as plt
    from sklearn.metrics import confusion_matrix
    from sklearn import metrics
  
    t = ["SVM","Logistic Regression","Decision Tree","KNN","Voting Classifier"]
    f, s = plt.subplots(5, 1,figsize=(25,25))
    y_pred=(SklearnSupervisedLearning(X_train,Y_train,X_test))+(SklearnVotingClassifier(X_train,Y_train,X_test))

    flag=True
    for i,p in enumerate(y_pred):
        cm = confusion_matrix(y_true, p)
        if flag==True:
          flag=False
          inter = s[i].imshow(cm,cmap = 'cividis')
          Legend=inter.properties()['clim']
        else:
          s[i].imshow(cm,cmap = 'cividis',clim=Legend)

        s[i].set_title(t[i])
        s[i].set_xticks(np.arange(cm.shape[1]))
        s[i].set_yticks(np.arange(cm.shape[0]))
        for ind in range(cm.shape[0]):
            for ind2 in range(cm.shape[1]):
                text = s[i].text(ind2, ind, cm[ind, ind2],
                            ha="center", va="center", color="w") 

    f.colorbar(inter,ax=s.ravel().tolist())              
    for x in s.flat:
        x.set(xlabel='prediction', ylabel='actual')
    for x in s.flat:
        x.label_outer()

#Calling Function
confusion_plot(X_train,Y_train,X_test,y_true)

def Grid_Search_SVM(X_train,Y_train,X_test):
    import matplotlib.pyplot as plt
    from sklearn import metrics
    from sklearn import svm

    accuracy = []
    params = {'C': [0.1, 1, 10, 100]} 
    
    for feat in list(params.values())[0]:
      model_svm = svm.SVC(kernel='linear',C=feat)
      model_svm.fit(X_train,Y_train)
      prediction=model_svm.predict(X_test)
      accuracy.append(metrics.accuracy_score(prediction,y_true))
    print(accuracy)
    plt.plot(list(params.values())[0],accuracy,label='SVM')
    plt.xticks(list(params.values())[0])

#Calling GridSearch
Grid_Search_SVM(X_train,Y_train,X_test)

def Grid_Search_Decision(X_train,Y_train,X_test,y_true):
    import matplotlib.pyplot as plt
    from sklearn import metrics
    from sklearn import tree
    
    accuracy=[]
    params = {'max_features': [5,10,15,20]}

    for feat in list(params.values())[0]:
        model_DT = tree.DecisionTreeClassifier(max_features=feat)
        model_DT.fit(X_train,Y_train)
        prediction=model_DT.predict(X_test)
        accuracy.append(metrics.accuracy_score(prediction,y_true))
    print(accuracy)
    plt.plot(list(params.values())[0],accuracy,label='DT')
    plt.xticks(list(params.values())[0])
    
#Calling GridSearch
Grid_Search_Decision(X_train,Y_train,X_test,y_true)

def Grid_Search_KNN(X_train,Y_train,X_test):
    import matplotlib.pyplot as plt
    from sklearn import metrics
    from sklearn import neighbors

    scaler = StandardScaler()
    norm_value = scaler.fit(np.vstack((X_train,X_train)))
    X_train = norm_value.transform(X_train)
    X_test = norm_value.transform(X_test)
    accuracy = []
    params = {'n_neighbors':[5,7,9,11,13]}
    
    for feat in list(params.values())[0]:
      model_knn= neighbors.KNeighborsClassifier(n_neighbors=feat)
      model_knn.fit(X_train,Y_train)
      prediction=model_knn.predict(X_test)
      accuracy.append(metrics.accuracy_score(prediction,y_true))
    print(accuracy)
    plt.plot(list(params.values())[0],accuracy,label='KNN')
    plt.xticks(list(params.values())[0])

#Calling GridSearch
Grid_Search_KNN(X_train,Y_train,X_test)