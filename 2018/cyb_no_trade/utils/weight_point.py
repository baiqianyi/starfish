

def weight_point(up_list, weights, point=0.1):
    weight_list = []
    for i in range(len(up_list)):
        weight_list.append(weights.get(up_list[i][0]))
    w_sum = sum(weight_list)
    point = w_sum*point
    weight_sum = 0
    for i in range(len(weight_list)):
        weight_sum = weight_sum + weight_list[i]
        if weight_sum > point:
            if i == 0:
                return up_list[0][1]
            return (up_list[i-1][1]*(weight_sum-point)/weight_list[i]+up_list[i][1]*(point-(weight_sum-weight_list[i]))/weight_list[i])
    return None