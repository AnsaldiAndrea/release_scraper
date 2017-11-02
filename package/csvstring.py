from io import StringIO
import csv


def value_to_csv(value):
    """covert an object to a csv formatted string"""
    with StringIO() as output:
        writer = csv.writer(output)
        writer.writerow(value)
        return output.getvalue()


def values_to_csv(matrix):
    """covert a list of objects to a csv formatted string"""
    with StringIO() as output:
        writer = csv.writer(output)
        for value in matrix:
            writer.writerow(value)
        return output.getvalue()


def csv_to_values(csv_file_name):
    """covert a csv file to an object"""
    with open(csv_file_name, encoding='utf-8') as f:
        return from_input(f)


def csvstring_to_values(csvstring):
    """covert a string in csv format to an object"""
    with StringIO(csvstring) as input:
        return from_input(input)


def from_input(input):
    """aux function"""
    values = []
    reader = csv.reader(input)
    for val in reader:
        values.append(val)
    return values
