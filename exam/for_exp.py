'''
Create and print table for .md files.
'''
from typing import List


def get_log_output(path: str):
    with open(path, "r", encoding="utf-8") as file:
        lines = file.read().split("\n")
    result = []
    for line in lines:
        if line.startswith("$ sudo"):
            result.append([line.split()[-1]])
        elif line.startswith("pgbench: fatal:"):
            result[-1].append("error")
            result[-1].append("error")
        elif line.startswith("latency average ="):
            result[-1].append(line.split()[-2])
        elif line.startswith("tps ="):
            result[-1].append(line.split()[2])
    return result


def get_result_table(path: str):
    result = get_log_output(path)
    result_table = []
    for i in range(3):
        result_table.append([])
        for j in range(3):
            result_table[i].append([])

    result_table[-1].pop()
    for i in range(0, len(result)-1, 8):
        result_table[0][0].append(result[i])
        result_table[0][1].append(result[i + 3])
        result_table[0][2].append(result[i + 6])
        result_table[1][0].append(result[i + 1])
        result_table[1][1].append(result[i + 4])
        result_table[1][2].append(result[i + 7])
        result_table[2][0].append(result[i + 2])
        result_table[2][1].append(result[i + 5])
    return result_table


def print_md_tables_with_log_result(path: str):
    result_table = get_result_table(path)
    result_table[2].append([]) # just for print in the 3d table with sql file
    for tab in result_table:
        print('\n\n\n')
        print("|   | c = 5  | c = 50  | c = 200    |")
        print("|---|--------|---------|------------|")
        row_count = len(tab[0])
        for row in range(row_count):
            s = f'| {tab[0][row][0]} |'
            for col in tab:
                if col != []:
                    s += f' latency = {col[row][1]} ms <br/> tps = {col[row][2] } |'
            print(s)


def print_md_tables_with_difference_in_log_result(result_table_1: List, result_table_2: List):
    for tab_1, tab_2 in zip(result_table_1, result_table_2):
        print('\n\n\n')
        print("|   | c = 5  | c = 50  | c = 200    |")
        print("|---|--------|---------|------------|")
        row_count = len(tab_1[0])
        for row in range(row_count):
            s = f'| {tab_1[0][row][0]} |'
            for col1, col2 in zip(tab_1, tab_2):
                if any([elem == "error" for elem in [col1[row][1],col2[row][1],col1[row][2],col2[row][2]]]):
                    s += f" Can't calculate |"
                else:
                    c_1_1 = float(col1[row][1])
                    c_1_2 = float(col2[row][1])
                    c_2_1 = float(col1[row][2])
                    c_2_2 = float(col2[row][2])
                    if col1 != []:
                        s += f' latency = {"- " + str(round(c_1_1 - c_1_2, 6)) if c_1_2 <= c_1_1 else "+ " + str(round(c_1_2 - c_1_1, 6))} ms ' \
                             f'<br/> tps = {"- " + str(round(c_2_1 - c_2_2, 6)) if c_2_2 <= c_2_1 else "+ " + str(round(c_2_2 - c_2_1, 6))} |'
            print(s)




if __name__ == "__main__":
    path1 = './experiments/e_1.md'
    path2 = './experiments/e_2.md'
    # path3 = './experiments/e_3_6.md'
    path6 = './experiments/e_6_2.md'
    path7 = './experiments/e_7.md'
    path8 = './experiments/e_8.md'

    path9 = './experiments/e_9.md'
    path10 = './experiments/e_10.md'
    path11 = './experiments/e_11.md'
    path12 = './experiments/e_12.md'

    path13 = './experiments/e_13.md'
    path14 = './experiments/e_14.md'
    path15 = './experiments/e_15.md'


    # print_md_tables_with_log_result(path15)
    print_md_tables_with_difference_in_log_result(get_result_table(path14), get_result_table(path15))
