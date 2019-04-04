import json
import math

INF = -1


def load_data(path):
    file = open(path)
    loaded_data = json.load(file)
    return loaded_data


def all_inequalities_solved_min(point, ab_matrix, c_matrix):
    eps = 0.001
    for i in range(0, len(ab_matrix)):
        if not ab_matrix[i][0] * point[0] + ab_matrix[i][1] * point[1] >= c_matrix[i] + eps and \
                not ab_matrix[i][0] * point[0] + ab_matrix[i][1] * point[1] >= c_matrix[i] - eps:
            return False
    if point[0] < 0 or point[1] < 0:
        return False
    return True


def all_inequalities_solved_max(point, ab_matrix, c_matrix):
    eps = 0.001
    for i in range(0, len(ab_matrix)):
        if not ab_matrix[i][0] * point[0] + ab_matrix[i][1] * point[1] <= c_matrix[i] + eps and \
                not ab_matrix[i][0] * point[0] + ab_matrix[i][1] * point[1] <= c_matrix[i] - eps:
            return False
    if point[0] < 0 or point[1] < 0:
        return False
    return True


def weak_inequalities(point, ab_matrix, c_matrix):
    eps = 0.001
    weak_indexes = []
    for i in range(0, len(ab_matrix)):
        if c_matrix[i] - eps <= ab_matrix[i][0] * point[0] + ab_matrix[i][1] * point[1] <= c_matrix[i] + eps:
            weak_indexes.append(i)
    return weak_indexes


def system_solve(first, second, c_matrix):
    main_det = first[0] * second[1] - second[0] * first[1]
    x_det = c_matrix[0] * second[1] - c_matrix[1] * first[1]
    y_det = first[0] * c_matrix[1] - second[0] * c_matrix[0]

    if main_det == 0:
        if x_det == 0 and y_det == 0:
            return INF
        else:
            return False
    else:
        x = x_det / main_det
        y = y_det / main_det
        return [x, y]


def find_border_points(ab_matrix, c_matrix, dual):
    points = []
    for i in range(0, len(ab_matrix)):
        for j in range(i, len(ab_matrix)):
            sys = system_solve(ab_matrix[i], ab_matrix[j], [c_matrix[i], c_matrix[j]])
            if sys and sys != INF:
                points.append(sys)
    for i in range(0, len(ab_matrix)):
        sys = system_solve(ab_matrix[i], [1, 0], [c_matrix[i], 0])
        if sys and sys != INF:
            points.append(sys)
    for i in range(0, len(ab_matrix)):
        sys = system_solve(ab_matrix[i], [0, 1], [c_matrix[i], 0])
        if sys and sys != INF:
            points.append(sys)

    del_list = []
    for i in range(0, len(points)):
        if dual:
            if not all_inequalities_solved_min(points[i], ab_matrix, c_matrix):
                del_list.append(points[i])
        else:
            if not all_inequalities_solved_max(points[i], ab_matrix, c_matrix):
                del_list.append(points[i])
    for i in del_list:
        points.remove(i)

    for i in points:
        for j in range(0, len(i)):
            if i[j] == - 0:
                i[j] = 0.0

    print("BORDER POINTS:")
    print(points)
    return points


def find_min_value(p_matrix, points):
    min_value = math.inf
    min_index = 0
    for i in range(0, len(points)):
        value = p_matrix[0] * points[i][0] + p_matrix[1] * points[i][1]
        if value < min_value:
            min_value = value
            min_index = i
    return min_index, min_value


def linear_program_solve(ab_matrix, c_matrix, p_matrix, dual=False):
    # print("ab:", ab_matrix)
    # print("c:", c_matrix)
    # print("p:", p_matrix)
    print_program(ab_matrix, c_matrix, p_matrix, dual)
    
    points = find_border_points(ab_matrix, c_matrix, dual)
    min_index, min_value = find_min_value(p_matrix, points)

    if not dual:
        print(points[min_index])
    else:
        min_weak_inequalities = weak_inequalities(points[min_index], ab_matrix, c_matrix)
        # print(min_weak_inequalities)
        return min_weak_inequalities, min_value


def dual_problem(ab_matrix, c_matrix, p_matrix):
    dual_ab_matrix = [list(x) for x in zip(*ab_matrix)]
    return linear_program_solve(dual_ab_matrix, p_matrix, c_matrix, True)


def find_primal_point(weak_indexes, ab_matrix, c_matrix):
    new_a = []
    new_b = []
    for i in weak_indexes:
        new_a.append(ab_matrix[0][i])
        new_b.append(ab_matrix[1][i])
    sys = system_solve(new_a, new_b, c_matrix)
    new_sys = []
    for i in range(0,len(ab_matrix[0])):
        new_sys.append(0.0)
    j = 0
    for i in range(0, len(new_sys)):
        if i in weak_indexes:
            new_sys[i] = sys[j]
            j = j + 1

    for i in range(0, len(new_sys)):
        if new_sys[i] == - 0:
            new_sys[i] = 0.0

    if sys and sys != INF:
        print("OPTIMAL POINT:")
        print(new_sys)


def print_program(ab_matrix, c_matrix, p_matrix, dual=False):
    if dual:
        inequality = " >="
        objective = " -> min"
        print("DUAL PROBLEM:")
    else:
        print("PRIMAL PROBLEM:")
        inequality = " <="
        objective = " -> max"

    for j in range(0, len(ab_matrix)):
        for i in range(0, len(ab_matrix[j])):
            print(ab_matrix[j][i], " * x", (i + 1), sep='', end='')
            if i != len(ab_matrix[j]) - 1:
                print(" + ", sep='', end='')
        print(inequality, c_matrix[j])
    print("x1, x2 >= 0\n\nOBJECTIVE FUNCTION:")
    for i in range(0, len(p_matrix)):
        print(p_matrix[i], " * x", (i + 1), sep='', end='')
        if i != len(p_matrix) - 1:
            print(" + ", sep='', end='')
    print(objective, "\n")


if __name__ == '__main__':
    data = load_data("data.json")
    ab = data['ab']
    p = data['p']
    c = data['c']

    if len(ab[0]) > 2:
        weak, objective_value = dual_problem(ab, c, p)
        find_primal_point(weak, ab, c)
        print("OBJECTIVE FUNCTION VALUE:")
        print(objective_value)
    else:
        linear_program_solve(ab, c, p)
