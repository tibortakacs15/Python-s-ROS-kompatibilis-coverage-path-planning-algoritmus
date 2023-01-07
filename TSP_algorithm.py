#!/usr/bin/env python3

import sys
import random
import copy

def osszehasonlitas(lista1, lista2):
    for i in range(0, len(lista1)):
        if lista1[i] == 100:
            continue
        if lista2[i] == 100:
                lista1.pop(i)
                lista1.insert(i, 100)
        if lista2[i] < lista1[i]:
            lista1.pop(i)
            lista1.insert(i, lista2[i])
    return lista1

def k_varos_beszurasa(matrix, reszkorut, k):
    m = 1000
    i = 0
    idx = 0
    while i < len(reszkorut) - 1:
        osszeg = 0.0
        u = reszkorut[i]
        v = reszkorut[i + 1]
        osszeg = matrix[u][k] + matrix[k][v] - matrix[u][v]
        if osszeg < m:
            m = osszeg
            idx = i
        i += 1
        if i == len(reszkorut) - 1:
            u = reszkorut[i]
            v = reszkorut[0]
            osszeg = matrix[u][k] + matrix[k][v] - matrix[u][v]
            if osszeg < m:
                m = osszeg
                idx = i
    return idx



def TSP_Nearest_Addition(s_matrix, vec):
    reszkorut = [0]
    idx = 0
    r = 0
    while r < len(s_matrix) - 1:
        _min = 10000000
        if r == 0:
            for i in range(0, len(s_matrix)):
                if vec[i] != 100 and vec[i] < _min:
                    _min = vec[i]
                    idx = i
            reszkorut.append(idx)
        else:
            vec = osszehasonlitas(vec, s_matrix[idx])
            for i in range(0, len(s_matrix)):
                if vec[i] != 100 and vec[i] < _min:
                    _min = vec[i]
                    idx = i
            reszkorut.append(idx)
        r += 1

    return reszkorut


def TSP_Nearest_Insertion(s_matrix, vec):
    reszkorut = [0]
    idx = 0
    r = 0
    k = 0
    while r < len(s_matrix) - 1:
        _min = 1000
        if r == 0:
            for i in range(0, len(s_matrix)):
                if vec[i] != 100 and vec[i] < _min:
                    _min = vec[i]
                    k = i
            reszkorut.append(k)
        else:
            vec = osszehasonlitas(vec, s_matrix[k])
            for i in range(0, len(s_matrix)):
                if vec[i] != 100 and vec[i] < _min:
                    _min = vec[i]
                    k = i
            idx = k_varos_beszurasa(matrix, reszkorut, k)
            reszkorut.insert(idx + 1, k)
        r += 1

    return reszkorut


def TSP_Farthest_Insertion(s_matrix, vec):
    reszkorut = [0]
    idx = 0
    k = 0
    r = 0
    while r < len(s_matrix) - 1:
        _max = -1
        if r == 0:
            for i in range(0, len(s_matrix)):
                if vec[i] != 100 and vec[i] > _max:
                    _max = vec[i]
                    k = i
            reszkorut.append(k)
        else:
            vec = osszehasonlitas(vec, s_matrix[k])
            for i in range(0, len(s_matrix)):
                if vec[i] != 100 and vec[i] > _max:
                    _max = vec[i]
                    k = i
            idx = k_varos_beszurasa(s_matrix, reszkorut, k)
            reszkorut.insert(idx + 1, k)
        r += 1

    return reszkorut

def celfuggvenyKiszamitasa(matrix, reszkorut):
    celfuggveny = 0.0
    utolso_elem = reszkorut[len(matrix) - 1]
    celfuggveny = matrix[utolso_elem][0]
    for i in range(0, len(reszkorut) - 1):
        k = reszkorut[i]
        kk = reszkorut[i + 1]
        celfuggveny += matrix[k][kk]
    return celfuggveny


def _min(matrix,s_matrix, a, b, c):
    vec = copy.deepcopy(matrix[0])
    #tsp = []
    if a < b and a < c:
        return TSP_Nearest_Addition(matrix, vec)
    elif b < c:
        return TSP_Nearest_Insertion(s_matrix, vec)
    else: 
        return TSP_Farthest_Insertion(s_matrix, vec)


def minKoltseg(matrix, s_matrix, vec):
    reszkorut_N_A = []
    reszkorut_N_I = []
    reszkorut_F_I = []

    celfuggveny_N_A = 0.0
    celfuggveny_N_I = 0.0
    celfuggveny_F_I = 0.0

    vec = copy.deepcopy(matrix[0])
    reszkorut_N_I = TSP_Nearest_Insertion(s_matrix, vec)
    celfuggveny_N_I = celfuggvenyKiszamitasa(matrix, reszkorut_N_I)

    vec = copy.deepcopy(matrix[0])
    reszkorut_F_I = TSP_Farthest_Insertion(s_matrix, vec)
    celfuggveny_F_I = celfuggvenyKiszamitasa(matrix, reszkorut_F_I)

    vec = copy.deepcopy(matrix[0])
    reszkorut_N_A = TSP_Nearest_Addition(s_matrix, vec)
    celfuggveny_N_A = celfuggvenyKiszamitasa(matrix, reszkorut_N_A)

    return _min(matrix, s_matrix, celfuggveny_N_A, celfuggveny_N_I, celfuggveny_F_I)

def kiir(matrix, n):
    for i in range(0, n):
        for j in range(0, n):
            print(matrix[i][j], end=' ')
        print(end='\n')

def matrix_generalas(n):
    matrix = []
    for i in range(0, n):
        l = []
        for j in range(0, n):
            if i == j:
                l.append(100)
            else:
                l.append(random.randint(1, 9))
        matrix.append(l)
    return matrix

'''
matrix = [[100, 2, 11, 10, 8, 7, 6, 5],
          [6, 100, 1, 8, 8, 4, 6, 7],
          [5, 12, 100, 11, 8, 12, 3, 11],
          [11, 9, 10, 100, 1, 9, 8, 10],
          [11, 11, 9, 4, 100, 2, 10, 9],
          [12, 8, 5, 2, 11, 100, 11, 9],
          [10, 11, 12, 10, 9, 12, 100, 3],
          [7, 10, 10, 10, 6, 3, 1,100]]
 '''

try:
    n = int(sys.argv[1])
    matrix = matrix_generalas(n)
    kiir(matrix, n)
    s_matrix = copy.deepcopy(matrix)
    vec = copy.deepcopy(matrix[0])
    m = []
    m = minKoltseg(matrix, s_matrix, vec)
    print("Reszkorut: ", m)
    print("Celfuggveny: ", celfuggvenyKiszamitasa(matrix, m))
except ValueError as err:
    print(err)

