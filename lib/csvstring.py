from io import StringIO
import csv


def value_to_csv(value):
    with StringIO() as output:
        writer = csv.writer(output)
        writer.writerow(value)
        return output.getvalue()


def values_to_csv(matrix):
    with StringIO() as output:
        writer = csv.writer(output)
        for value in matrix:
            writer.writerow(value)
        return output.getvalue()


def csv_to_values(csv_file_name):
    with open(csv_file_name, encoding='utf-8') as f:
        return from_input(f)


def csvstring_to_values(csvstring):
    with StringIO(csvstring) as input:
        return from_input(input)


def from_input(input):
    values = []
    reader = csv.reader(input)
    for val in reader:
        values.append(val)
    return values
