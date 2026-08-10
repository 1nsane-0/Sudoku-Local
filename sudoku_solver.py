from progress import count_step


def is_consistent(variable,value,assignment):
    for i in range(9):
        if (assignment[(variable[0],i)] == value):
            return False
        
    for j in range(9):
        if (assignment[(j,variable[1])] == value):
            return False
        
    square = (int(variable[0]/3),int(variable[1]/3))
    
    for i in range(3):
        for j in range(3):
            if(assignment[(square[0]*3+i,square[1]*3+j)] == value and variable != (square[0]*3+i,square[1]*3+j)):
                return False
    return True

def backtrack(assignment, variables, domain, depth=0):

    count_step()


    if (0 not in assignment.values()):
        return assignment
    
    result = None

    for variable in variables:
        if (assignment[variable]==0):
            for value in domain:
                if is_consistent(variable,value,assignment):
                    assignment[variable] = value
                    result = backtrack(assignment,variables,domain,depth+1)
                    if result is not None:
                        return result
                    assignment[variable] = 0
            return None
    return result
