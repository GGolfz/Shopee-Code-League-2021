import numpy as np
import pandas as pd
import spacy
from tqdm import tqdm
n_iter=5
spacy.require_gpu()
data = pd.read_csv('./train.csv')
data["POI"] = data["POI/street"].str.split(pat='/').apply(lambda x:x[0])
data["Street"] = data["POI/street"].str.split(pat='/').apply(lambda x:x[1])
TRAIN_DATA = []
STREET_DATA = set()
POI_DATA = set()
print("Start Data Preparation")
for index,row in data.iterrows():
    if (index+1) % 10000 == 0:
        print(index+1)
    entities = []
    if row["POI"] != '':
        start = 0
        end = 0
        find = row["raw_address"].find(row["POI"])
        if find == -1:
            sp = row["POI"].split(' ')
            count = 0
            for i in sp:
                v = i if len(i) < 3 else i[0:3]
                find = row["raw_address"].find(v)
                if find != -1:
                    if count == 0:
                        start = find
                    end = find
                    for j in range(len(i)):
                        if (find+j) < len(row["raw_address"]) and row["raw_address"][find+j] == i[j]:
                            end = find+j
                        else:
                            break
                    count+=1
        else:
            start = find
            end = find+len(row["POI"]) - 1
        POI_DATA.add(row["POI"])
        entities.append((start,end+1,row["POI"]))
    if row["Street"] != '':
        start = 0
        end = 0
        find = row["raw_address"].find(row["Street"])
        if find == -1:
            sp = row["Street"].split(' ')
            count = 0
            for i in sp:
                v = i if len(i) < 3 else i[0:3]
                find = row["raw_address"].find(v)
                if find != -1:
                    if count == 0:
                        start = find
                    end = find
                    for j in range(len(i)):
                        if (find+j) < len(row["raw_address"]) and row["raw_address"][find+j] == i[j]:
                            end = find+j
                        else:
                            break
                    count+=1
        else:
            start = find
            end = find+len(row["Street"]) - 1
        entities.append((start,end+1,row["Street"]))
        STREET_DATA.add(row["Street"])
    TRAIN_DATA.append((row["raw_address"],{'entities':entities}))
print("Finish Data Preparation")
print("Create Blank en model")
ner_model = spacy.blank('en')
if 'ner' not in ner_model.pipe_names:
    ner = ner_model.create_pipe('ner')
    ner_model.add_pipe('ner', last=True)
else:
    ner = ner_model.get_pipe('ner')
print("Start Add Label to NER")
count = 0
for _,annotations in TRAIN_DATA:
    count += 1
    if count % 10000 == 0:
        print(count)
    all_entities = annotations.get('entities')
    for ent in all_entities:
        ner.add_label(ent[2])
other_pipes = [pipe for pipe in ner_model.pipe_names if pipe != 'ner']
print("Finish Add Label to NER")
print("Start Trainning Model")
with ner_model.disable_pipes(*other_pipes):
    optimizer = ner_model.begin_training()
    for itn in range(n_iter):
        losses = {}
        print("Iteration",itn+1)
        count = 0
        for text,annotations in tqdm(TRAIN_DATA):
            count += 1
            if count % 10000 == 0:
                print(itn+1,":",count)
            ner_model.update(([text],[annotations]),drop=0.5,sgd=optimizer,losses=losses)
print("Finish Tranning Model")
print("Load Test File")
test_df = pd.read_csv('./test.csv')
TEST_RESULT = []
print("Start Testing Model")
count = 0
for index,row in test_df.iterrows():
	count += 1
	if count % 10000 == 0:
		print(count)
	doc = ner_model(row["raw_address"])
	poiTest = ''
	streetTest = ''
	for ent in doc.ents:
		temp = ent.label_
		if temp in POI_DATA:
			poiTest = ent.text
		elif temp in STREET_DATA:
			streetTest = ent.text
	TEST_RESULT.append([row["id"],poiTest+'/'+streetTest])
print("Finish Testing Model")
answerDF = pd.DataFrame(TEST_RESULT,columns=['id', 'POI/street'])
print("Start save output to file success")
answerDF.to_csv('./output.csv',index=False)
print("Save output to file success")