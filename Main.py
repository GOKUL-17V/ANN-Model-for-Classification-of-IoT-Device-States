from tkinter import *
import tkinter
from tkinter import filedialog
from tkinter.filedialog import askopenfilename
from tkinter import simpledialog

import pandas as pd
import numpy as np
import seaborn as sns
import os
import matplotlib.pyplot as plt
import joblib

from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import recall_score,f1_score,precision_score
from sklearn.metrics import accuracy_score,confusion_matrix,classification_report
from sklearn.model_selection import train_test_split

#sample classifiers
from sklearn.ensemble import ExtraTreesClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.neural_network import MLPClassifier


accuracy = []
precision = []
recall = []
fscore = []

categories=['Normal','Anomaly']
target_name  ='attack'
model_folder = "model"


def Upload_Dataset():
    global dataset
    filename = filedialog.askopenfilename(initialdir = "Dataset")
    text.delete('1.0', END)
    text.insert(END,filename+' Loaded\n')
    dataset = pd.read_csv(filename)
    text.insert(END,str(dataset.head())+"\n\n")

def Preprocess_Dataset():
    global dataset
    global X,y
    text.delete('1.0', END)
    
    dataset = dataset.dropna()
    text.insert(END,str(dataset.isnull().sum())+"\n\n")
    
    non_numeric_columns = dataset.select_dtypes(exclude=['int', 'float']).columns


    for col in non_numeric_columns:
        le = LabelEncoder()
        dataset[col] = le.fit_transform(dataset[col])
    y = dataset[target_name]
    X = dataset.drop(target_name, axis=1)
# Display count plot after label encoding
    sns.set(style="darkgrid")  # Set the style of the plot
    plt.figure(figsize=(8, 6))  # Set the figure size
    ax = sns.countplot(x=target_name, data=dataset, palette="Set3")
    plt.title("Count Plot")  # Add a title to the plot
    plt.xlabel("Categories")  # Add label to x-axis
    plt.ylabel("Count")  # Add label to y-axis
    for p in ax.patches:
        ax.annotate(f'{p.get_height()}', (p.get_x() + p.get_width() / 2., p.get_height()),ha='center', va='center', fontsize=10, color='black', xytext=(0, 5),
                textcoords='offset points')

    plt.show()  # Display the plot

def Train_Test_Splitting():
    global X,y
    global x_train,y_train,x_test,y_test

    # Create a count plot
    x_train, x_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=0)
    
# Display information about the dataset
    text.delete('1.0', END)
    text.insert(END, "Total records found in dataset: " + str(X.shape[0]) + "\n\n")
    text.insert(END, "Total records found in dataset to train: " + str(x_train.shape[0]) + "\n\n")
    text.insert(END, "Total records found in dataset to test: " + str(x_test.shape[0]) + "\n\n")

def Calculate_Metrics(algorithm, predict, y_test):
    global categories

    a = accuracy_score(y_test,predict)*100
    p = precision_score(y_test, predict,average='macro') * 100
    r = recall_score(y_test, predict,average='macro') * 100
    f = f1_score(y_test, predict,average='macro') * 100

    accuracy.append(a)
    precision.append(p)
    recall.append(r)
    fscore.append(f)
    
    text.insert(END,algorithm+" Accuracy  :  "+str(a)+"\n")
    text.insert(END,algorithm+" Precision : "+str(p)+"\n")
    text.insert(END,algorithm+" Recall    : "+str(r)+"\n")
    text.insert(END,algorithm+" FScore    : "+str(f)+"\n")
    conf_matrix = confusion_matrix(y_test, predict)
    total = sum(sum(conf_matrix))
    se = conf_matrix[0,0]/(conf_matrix[0,0]+conf_matrix[0,1])
    se = se* 100
    text.insert(END,algorithm+' Sensitivity : '+str(se)+"\n")
    sp = conf_matrix[1,1]/(conf_matrix[1,0]+conf_matrix[1,1])
    sp = sp* 100
    text.insert(END,algorithm+' Specificity : '+str(sp)+"\n\n")
    
    CR = classification_report(y_test, predict,target_names=categories)
    text.insert(END,algorithm+' Classification Report \n')
    text.insert(END,algorithm+ str(CR) +"\n\n")

    
    plt.figure(figsize =(6, 6)) 
    ax = sns.heatmap(conf_matrix, xticklabels = categories, yticklabels = categories, annot = True, cmap="viridis" ,fmt ="g");
    ax.set_ylim([0,len(categories)])
    plt.title(algorithm+" Confusion matrix") 
    plt.ylabel('True class') 
    plt.xlabel('Predicted class') 
    plt.show()       


def existing_classifier():
    
    global x_train,y_train,x_test,y_test
    text.delete('1.0', END)

    model_filename = os.path.join(model_folder, "Gaussian_NBC.pkl")

    if os.path.exists(model_filename):
        mlmodel = joblib.load(model_filename)
    else:
        mlmodel = GaussianNB()
        mlmodel.fit(x_train, y_train)
        joblib.dump(mlmodel, model_filename)

    y_pred = mlmodel.predict(x_test)
    Calculate_Metrics("Existing Gaussian NBC", y_pred, y_test)

def proposed_classifier():
    global x_train, y_train, x_test, y_test, mlmodel
    text.delete('1.0', END)

    # Step 1: MLP Feature Extraction
    mlp_model_filename = os.path.join(model_folder, "mlp_feature_extractor.pkl")
    if os.path.exists(mlp_model_filename):
        mlp = joblib.load(mlp_model_filename)
    else:
        mlp = MLPClassifier(hidden_layer_sizes=(128, 64), max_iter=500, random_state=42)
        mlp.fit(x_train, y_train)
        joblib.dump(mlp, mlp_model_filename)

    # Extract intermediate features using decision_function or predict_proba
    x_train_features = mlp.predict_proba(x_train)
    x_test_features = mlp.predict_proba(x_test)

    # Step 2: ETC Classification
    etc_model_filename = os.path.join(model_folder, "extratrees_model.pkl")
    if os.path.exists(etc_model_filename):
        mlmodel = joblib.load(etc_model_filename)
    else:
        mlmodel = ExtraTreesClassifier(n_estimators=100, random_state=42)
        mlmodel.fit(x_train, y_train)
        joblib.dump(mlmodel, etc_model_filename)

    # Step 3: Prediction and Evaluation
    y_pred = mlmodel.predict(x_test)
    Calculate_Metrics("Proposed MLP with Extra Trees Classifier", y_pred, y_test)

def Prediction():
    global mlmodel, categories

    filename = filedialog.askopenfilename(initialdir="Dataset")
    text.delete('1.0', END)
    text.insert(END, f'{filename} Loaded\n')
    test = pd.read_csv(filename)
    
    # Do preprocessing ( label encoding mandatory )
    non_numeric_columns = test.select_dtypes(exclude=['int', 'float']).columns  
    for col in non_numeric_columns:
        le = LabelEncoder()
        test[col] = le.fit_transform(test[col])
    predict = mlmodel.predict(test)   

    # Iterate through each row of the dataset and print its corresponding predicted outcome
    text.insert(END, f'Predicted Outcomes for each row:\n')
    for index, row in test.iterrows():
        # Get the prediction for the current row
        prediction = predict[index]
        
         # Map predicted index to its corresponding label using unique_labels_list
        predicted_outcome = categories[prediction]
        # Print the current row of the dataset followed by its predicted outcome
        text.insert(END, f'Row {index + 1}: {row.to_dict()} - Predicted Outcome: {predicted_outcome}\n\n\n\n\n')

def graph():
    # Create a DataFrame
    df = pd.DataFrame([
    ['Existing', 'Precision', precision[0]],
    ['Existing', 'Recall', recall[0]],
    ['Existing', 'F1 Score', fscore[0]],
    ['Existing', 'Accuracy', accuracy[0]],
    ['Proposed', 'Precision', precision[1]],
    ['Proposed', 'Recall', recall[1]],
    ['Proposed', 'F1 Score', fscore[1]],
    ['Proposed', 'Accuracy', accuracy[1]],
    ], columns=['Parameters', 'Algorithms', 'Value'])

    # Pivot the DataFrame and plot the graph
    pivot_df = df.pivot_table(index='Parameters', columns='Algorithms', values='Value', aggfunc='first')
    pivot_df.plot(kind='bar')
    # Set graph properties
    plt.title('Classifier Performance Comparison')
    plt.ylabel('Score')
    plt.xticks(rotation=0)
    plt.tight_layout()
    # Display the graph
    plt.show()


def close():
    main.destroy()
import tkinter as tk

def show_admin_buttons():
    # Clear ADMIN-related buttons
    clear_buttons()
    # Add ADMIN-specific buttons
    tk.Button(main, text="IoMT Dataset", command=Upload_Dataset, font=font1).place(x=50, y=600)
    tk.Button(main, text="Preprocess Dataset", command=Preprocess_Dataset, font=font1).place(x=200, y=600)
    tk.Button(main, text="Train Test Splitting", command=Train_Test_Splitting, font=font1).place(x=400, y=600)
    tk.Button(main, text="Existing Gaussian NBC", command=existing_classifier, font=font1).place(x=600, y=600)
    tk.Button(main, text="Proposed ANN with Extra Trees Classifier", command=proposed_classifier, font=font1).place(x=900, y=600)

def show_user_buttons():
    # Clear USER-related buttons
    clear_buttons()
    # Add USER-specific buttons
    tk.Button(main, text="Prediction", command=Prediction, font=font1).place(x=200, y=600)
    tk.Button(main, text="Comparison Graph", command=graph, font=font1).place(x=400, y=600)

def clear_buttons():
    # Remove all buttons except ADMIN and USER
    for widget in main.winfo_children():
        if isinstance(widget, tk.Button) and widget not in [admin_button, user_button]:
            widget.destroy()

# Initialize the main tkinter window
main = tk.Tk()
screen_width = main.winfo_screenwidth()
screen_height = main.winfo_screenheight()
main.geometry(f"{screen_width}x{screen_height}")

# Configure title
font = ('times', 18, 'bold')
title_text = "Artificial Neural Networks Model For Classification of IOT Device states in Medical Industry"
title = tk.Label(main, text=title_text, bg='white', fg='black', font=font, height=3, width=120)
title.pack()

# ADMIN and USER Buttons (Always visible)
font1 = ('times', 14, 'bold')
admin_button = tk.Button(main, text="ADMIN", command=show_admin_buttons, font=font1, width=20, height=2, bg='LightBlue')
admin_button.place(x=50, y=100)

user_button = tk.Button(main, text="USER", command=show_user_buttons, font=font1, width=20, height=2, bg='LightGreen')
user_button.place(x=300, y=100)

# Text area for displaying results or logs
text = tk.Text(main, height=20, width=140)
scroll = tk.Scrollbar(text)
text.configure(yscrollcommand=scroll.set)
text.place(x=50, y=160)
text.config(font=font1)

main.config(bg='deep sky blue')
main.mainloop()





