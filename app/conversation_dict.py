from datetime import datetime,timezone

all_conversation = {}
pop_dict={}

def clean_dict():
    now = int(datetime.now(timezone.utc).timestamp())
    empty_list=[]
    for i in pop_dict:
        if pop_dict[i]<now:
            all_conversation.pop(i,None)
            empty_list.append(i)

    for i in empty_list:
        pop_dict.pop(i,None)


#all convo structure
a = {'user_id' :
        {
        'model1' : [{'you'},{'user'}],
        'model2' : []
        }
    }