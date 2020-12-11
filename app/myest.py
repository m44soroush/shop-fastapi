if __name__ == '__main__':
    name_score = []
    for i in range(int(input())):
        name = input()
        score = float(input())
        name_score.append([name, score])

    set_of_scores = sorted(list(set([student[0] for student in name_score])))
    second_lowest_score = set_of_scores[1]
    second_lowest_names = [student[0]
                           for student in name_score
                           if student[1] == second_lowest_score]
    second_lowest_names.sort()

    for name in second_lowest_names:
        print(name)
