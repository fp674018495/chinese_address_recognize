# coding=utf-8
from dis import dis
import jieba.analyse
import jieba.posseg as pseg
from extract.complement import complement_st,clear_ends
import Levenshtein
from parms import *

for d in os.listdir(PATH_DICT):
    jieba.load_userdict(os.path.join(PATH_DICT, d))

tag_list = [COL_PROV, COL_CITY, COL_DIST, COL_ST, COL_VIL]


def my_distance(s1,s_l:list):
    res ={}
    best_dis = 99
    for s2 in s_l:
        s2=s2[0]
        if len(s1)<=len(s2):
            temp_dis =Levenshtein.distance(s1, s2[:len(s1)])
            res[temp_dis] = s2[:len(s1)]
            best_dis = min(best_dis,temp_dis)
        else:
            temp_dis =Levenshtein.distance(s1[len(s1)-len(s2):], s2)
            res[temp_dis] = s1[:len(s1)-len(s2)]+s2
            best_dis = min(best_dis,temp_dis)
    if best_dis >= len(s1): 
        return None,None
    best_res = res[best_dis]
    return res ,best_res

    
def rebuild_sentence(df,sentence,cut_message,sub_area):
    res =[ ]
    df_level = 0 
    for i,data in enumerate(cut_message):
        if data[1] in  tag_list:
            res.append(data[0]) 
            df_level = tag_list.index(data[1])+1
        elif i ==len(cut_message)-1:
            res.append(data[0]) 
            # for j  in range(df_level,5):
            #     my_distance(data[0],sub_area[tag_list[df_level]])
        else:
            s2_l= []
            for i in range(df_level, tag_list.index(cut_message[1+i][1])):
                if i == 0 or i ==1:
                    s2_l.append([df[tag_list[i]][0], clear_ends(df[tag_list[i]][0])])
                else:
                    s2_l.append([df[tag_list[i]][0]])
            _,best_res = my_distance(data[0],s2_l)
            if best_res !=None:
                res.append(best_res)
            else:
                res.append(data[0])
    return res 
def get_token_and_flag(sentence):
    cut_res = pseg.lcut(sentence)
    start = 0
    cut_message  =[]
    df = {i: ["unk"] for i in tag_list}
    lowest_level = 0
    for data in cut_res:
        end = len(data.word)+start
        if len(cut_message)>0 and cut_message[-1][1] not in tag_list and data.flag not in tag_list:
            cut_message[-1] = [cut_message[-1][0]+data.word,data.flag,(cut_message[-1][-1][0],end)]
        else:
            cut_message.append([data.word,data.flag,(start,end)]) 
        if data.flag in tag_list:
            df[data.flag] = [data.word,(start,end)]
            lowest_level = max(lowest_level, tag_list.index(data.flag))
        start = end 
    df,sub_area = complement_st(df,lowest_level)
    res = rebuild_sentence(df,sentence,cut_message,sub_area)
    return "".join(res)



if __name__=="__main__":
    txt1 = '胡建被安市石井镇后店北片88号祝义汽车投资有限公司'
    for i in range(3):
        txt1 = get_token_and_flag(txt1)
        print(txt1)
    
   
