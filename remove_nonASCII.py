# Remove non-ASCII characters in CSV file

import sys
import re

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Please specify a CSV file')
        sys.exit(1)

    input_file = sys.argv[1]
    print('Input file: {}'.format(input_file))

    if input_file.endswith('.csv'):
        output_file = input_file.split('.csv')[0]
    elif input_file.endswith('.txt'):
        output_file = input_file.split('.txt')[0]
    else:
        print('The file must end with ".csv" or ".txt"')
        sys.exit(1)

    output_file += '_nonASCII_removed.csv'
    print('Output file: {}'.format(output_file))

    # Detect encoding of input_file
    # res = chardet.detect(open(input_file, 'rb').read(10))
    # input_encoding = res['encoding']
    # print('Input encoding detected: {}, with {} confidence'.format(input_encoding, res['confidence']))

    with open(input_file, 'rb') as fr, open(output_file, 'w') as fw:
        lines = fr.read()

        if b'\r' in lines:
            print('New line is separated by "\\r"')
            lines = lines.split(b'\r')
        elif b'\n' in lines:
            print('New line is separated by "\\n"')
            lines = lines.split(b'\n')

        for line in lines:
            # replace non-ASCII characters with ''
            line = ''.join(chr(c) if c < 128 else '' for c in line).strip()

            # remove rows that do not contain separater '\t'
            if '\t' not in line:
                print('Remove a line that does not contain "\\t"')
                continue

            # replace consecutive underscores __ with space
            line = re.sub(r'[_|,]{2,}', ' ', line)

            # replace double quotes with ''
            line = re.sub(r'\"', '', line)

            fw.write(line + '\n')

        print('Done!')
