import math
from prettytable import PrettyTable

def getVectorSpaceModel(queries, query_weight, document_weight):
    query_matrix, query_result = getQueryDistance(query_weight)
    print("query_matrix",query_matrix)
    print("query_result",query_result)
    document_matrix, document_result = getDocumentDistance(document_weight)
    print("document_matrix",document_matrix)
    print("document_result",document_result)
    dot_document_matrix, dot_document_result = getDotProduct(query_matrix, document_matrix)
    print("dot_document_matrix",dot_document_matrix)
    print("dot_document_result",dot_document_result)

    print_tabel_hasil(queries, query_matrix, query_result, document_matrix, document_result, dot_document_matrix,
                      dot_document_result)

    doc_similarity = cosineSimilarity(query_result,document_result,dot_document_result)
    print("doc_similarity",doc_similarity)
    return doc_similarity

def getQueryDistance(term_weight):
    calculation_matrix = {}
    total_weight = 0
    for weight in term_weight.keys():
        term_res = math.pow(term_weight[weight],2)
        total_weight += term_res
        calculation_matrix[weight] = term_res
    return calculation_matrix, math.sqrt(total_weight)

def getDocumentDistance(term_weights):
    doc_calculation_matrix = {}
    result_matrix = {}
    for docnum, term_weight in term_weights.items():
        calculation_matrix = {}
        total_weight = 0
        for weight in term_weight.keys():
            term_res = math.pow(term_weight[weight],2)
            total_weight += term_res
            calculation_matrix[weight] = term_res
        doc_calculation_matrix[docnum] = calculation_matrix
        result_matrix[docnum] = math.sqrt(total_weight)
    return doc_calculation_matrix, result_matrix

def getDotProduct(query_matrix,document_matrix):
    doc_calculation_matrix = {}
    result_matrix = {}
    for docnum, term_weight in document_matrix.items():
        calculation_matrix = {}
        total_weight = 0
        for weight in term_weight.keys():
            if weight in query_matrix.keys():
                term_res = term_weight[weight] * query_matrix[weight]
                total_weight += term_res
                calculation_matrix[weight] = term_res
        doc_calculation_matrix[docnum] = calculation_matrix
        result_matrix[docnum] = total_weight
    return doc_calculation_matrix, result_matrix

def cosineSimilarity(query_result,document_result,dot_document_result):
    doc_similarity = {}
    print("query_result",query_result)
    print("document_result",document_result)
    print("dot_document_result",dot_document_result)

    for docnum, term_weight in document_result.items():
        print("term_weight",term_weight)
        if term_weight == 0 or query_result == 0:
            doc_similarity[docnum] = 0
        else:
            doc_similarity[docnum] = (dot_document_result[docnum])/(query_result*term_weight)
    return doc_similarity

def print_tabel_hasil(queries, query_matrix, query_result, document_matrix, document_result, dot_document_matrix, dot_document_result):
    headers = ['Query']
    headers = headers + ['Q^2']
    for num in range(len(document_matrix.keys())):
        headers = headers + ['D' + str(num + 1)+'^2']
    for num in range(len(document_matrix.keys())):
        headers = headers + ['Q*D' + str(num + 1)]
    t = PrettyTable(headers)


    for query in queries:
        row = [query]

        if query in query_matrix.keys():
            row += [query_matrix[query]]
        else:
            row += ['0']

        for dm in document_matrix.values():
            if query in dm.keys():
                row += [dm[query]]
            else:
                row += ['0']

        for ddm in dot_document_matrix.values():
            if query in ddm.keys():
                row += [ddm[query]]
            else:
                row += ['0']

        t.add_row(row)
    upperrow = ['']
    row = ['']
    upperrow += ['sqrt(Q)']
    row += [query_result]
    for docnum in document_result.keys():
        upperrow += ['sqrt(Di)']
        row += [round(document_result[docnum], 4)]
    for docnum in dot_document_result.keys():
        upperrow += ['sum(Q*Di)']
        row += [round(dot_document_result[docnum], 4)]
    t.add_row(upperrow)
    t.add_row(row)

    print(t)
