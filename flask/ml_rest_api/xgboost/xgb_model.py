import numpy as np

def xgb_tree(x, num_booster):
    if num_booster == 0:
        state = 0
        if state == 0:
            state = (1 if x['Pclass']<3 or np.isnan(x['Pclass'])  else 2)
            if state == 1:
                state = (3 if x['Fare']<13.6459 or np.isnan(x['Fare'])  else 4)
                if state == 3:
                    return -0.00640085
                if state == 4:
                    state = (9 if x['Age']<42.5 else 10)
                    if state == 9:
                        return 0.0335449
                    if state == 10:
                        return 0.00980747
            if state == 2:
                state = (5 if x['Age']<6.5 else 6)
                if state == 5:
                    state = (11 if x['SibSp']<3 or np.isnan(x['SibSp'])  else 12)
                    if state == 11:
                        return 0.0521093
                    if state == 12:
                        return -0.0224916
                if state == 6:
                    return -0.0162228
    elif num_booster == 1:
        state = 0
        if state == 0:
            state = (1 if x['Pclass']<3 or np.isnan(x['Pclass'])  else 2)
            if state == 1:
                state = (3 if x['Fare']<52.2771 or np.isnan(x['Fare'])  else 4)
                if state == 3:
                    state = (7 if x['Parch']<1 or np.isnan(x['Parch'])  else 8)
                    if state == 7:
                        return 0.000147338
                    if state == 8:
                        return 0.0348956
                if state == 4:
                    return 0.0321656
            if state == 2:
                state = (5 if x['Age']<6.5 else 6)
                if state == 5:
                    state = (11 if x['SibSp']<3 or np.isnan(x['SibSp'])  else 12)
                    if state == 11:
                        return 0.0472049
                    if state == 12:
                        return -0.0203924
                if state == 6:
                    return -0.0146041
    elif num_booster == 2:
        state = 0
        if state == 0:
            state = (1 if x['Pclass']<3 or np.isnan(x['Pclass'])  else 2)
            if state == 1:
                state = (3 if x['Fare']<13.6459 or np.isnan(x['Fare'])  else 4)
                if state == 3:
                    return -0.00585524
                if state == 4:
                    return 0.0201724
            if state == 2:
                return -0.0114313

def xgb_predict(x):
    predict = 0.3838383838383838
# initialize prediction with base score
    for i in range(3):
        predict = predict + xgb_tree(x, i)
    return predict