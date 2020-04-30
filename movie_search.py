import requests
from bs4 import BeautifulSoup
import os


def insert_at_beginning(list_y_index, type_file):
    list_x = list_y_index.split(type_file)
    ''.join(list_x[:-1])
    str_file = list_x[0] + type_file
    return str_file


def introduction():
    print('v1.5 - DISCLAIMER - TITLE INPUT IS CASE SENSITIVE\n')
    print('Load times depend on your connection and how long the websites take to respond.')

    while True:
        user_input = input('Enter the title of a movie: ')
        if len(user_input) > 0:
            break

    os.system('cls')
    print('Searching for ' + user_input + '...')
    return user_input


def responding_links(page_main):
    initial_link_list = []
    for page_index in page_main:
        # noinspection PyBroadException
        try:
            initial_link_list.append(page_index.a.get('href')[7:][:-88])
        except:
            pass

    blacklist_file = open('blacklist.txt').read()  # for blacklisting links that do not give video files
    blacklist = blacklist_file.split('\n')

    blacklisted_pass_list = [index for index in initial_link_list if not any(keyword in index for keyword in blacklist)]

    print()
    links_return = []
    for index in blacklisted_pass_list:
        # noinspection PyBroadException
        try:
            index_c = requests.head(index, timeout=6, allow_redirects=False)
            if index_c.status_code == 200:
                links_return.append(index)
        except:
            pass
    return links_return


def file_and_size(list_input, comp_name):
    link_size_dict = {}
    for link in list_input:
        size_get = requests.get(link).text
        size_get = BeautifulSoup(size_get, 'lxml')

        link_get = size_get.find_all('a')
        href_get = [z.get('href') for z in link_get]  # retrieves links on open directories
        href_get.pop(0)  # removes '../' at beginning of list

        href_temp = []
        try:
            href_temp = [z for z in href_get if any(name in z for name in comp_name)]
        except TypeError:
            pass

        file_test = ['.mkv', '.avi', '.mp4']
        file_not = ['.srt', 'Index of', '.html', 'mp3']
        href_f = [z for z in href_temp if any(file in z for file in file_test) if not all(x in z for x in file_not)]

        href_temp.clear()
        for z in href_f:
            href_temp.append(
                z.replace('%20', ' ').replace('%28', '(').replace('%29', ')').replace('%5B', '[').replace('%5D', ']'))

        href_temp_47 = [z[:47] for z in href_temp]

        block_text = size_get.text
        block_list = block_text.split('\n')

        name_size = [z for z in block_list if any(index in z for index in href_temp_47)]

        mod_name_size = []
        for x in name_size:
            if '\r' in x:
                mod_name_size.append((x.replace('\r', '')))
            elif '\xa0' in x:
                mod_name_size.append((x.replace('\xa0', '')))

        _size_final = []
        for z in mod_name_size:
            split_temp = z.split(' ')

            for index in split_temp:
                if '.avi' in index:
                    beg_str = insert_at_beginning(index, '.avi')
                    split_temp.remove(index)
                    split_temp.insert(0, beg_str)
                elif '.mkv' in index:
                    beg_str = insert_at_beginning(index, '.mkv')
                    split_temp.remove(index)
                    split_temp.insert(0, beg_str)
                elif '.mp4' in index:
                    beg_str = insert_at_beginning(index, '.mp4')
                    split_temp.remove(index)
                    split_temp.insert(0, beg_str)

            split_temp = [split_temp[0], split_temp[-1]]

            if 'K' in split_temp[-1]:
                _size_final.append(split_temp[-1].replace('K', 'KB'))
            elif 'G' in split_temp[-1]:
                _size_final.append(split_temp[-1].replace('G', 'GB'))
            elif 'M' in split_temp[-1]:
                _size_final.append(split_temp[-1].replace('M', 'MB'))
            else:
                byte_divide = round((int(split_temp[-1]) / 1000000000), 2)
                if byte_divide >= 1:
                    _size_final.append(str(byte_divide) + 'GB')
                else:
                    _size_final.append(str(byte_divide) + 'MB')

        fin_link_list = [link + x for x in href_f]

        index_size = 0
        for _link_ in fin_link_list:
            link_size_dict[_link_] = _size_final[index_size]
            index_size += 1
        return link_size_dict


def main():
    user_search = introduction()

    user_search = user_search.replace(":", "")  # colons do not normally appear in open directories
    user_search = user_search.replace("-", "").replace("  ", " ")  # nor do hyphens or double spaces

    title = list(user_search.split(' '))  # splits each word from 'question_title' into a list: 'title'

    google_link = ('https://www.google.com/search?q=intext%3A%22' + str('+'.join(
        title)) + '%22+intitle%3A%22index.of%22++%2B(wmv|mpg|avi|mp4|mov)+-inurl%3A(''jsp|pl|php|html|aspx|htm|cf|shtml)')  # adds each index from title list to google link

    page_source = requests.get(google_link).text  # creates variable 'page_source' which requests link
    page_source = BeautifulSoup(page_source, 'lxml')  # 'page_source' parsed through BeautifulSoup w/ 'lxml'
    page_source = page_source.find_all('div', class_='kCrYT')  # searched to find 'div' and 'class="KCrYT"'

    link_list = responding_links(page_source)

    print('\nResponding Links:')
    for index in link_list:
        print(index)

    print('\nSearching responding links for', user_search, '...')

    name_test = [str('.'.join(title)), str(user_search),
                 str('%20'.join(title))]  # checks for title separated by: spaces, periods, or %20 (space)

    final_dict = file_and_size(link_list, name_test)

    max_length_key = 0
    for key in final_dict:  # finds max length of key, used in print formatting in next for loop
        length_key = len(key)
        if length_key > max_length_key:
            max_length_key = length_key

    os.system('cls')

    print(user_search, '\n')
    print(f" #  File{' ' * (max_length_key - 3)}Size")  # formatting of header
    print(" _" + ('_' * (max_length_key + 9)))  # creates long lines to make header look pretty

    iii = 1
    for key in final_dict:
        space_diff = ' ' * (max_length_key - len(key))
        if iii < 10:
            print(f' {iii}: {key} {space_diff}{final_dict[key]}')
        else:
            print(f'{iii}: {key} {space_diff}{final_dict[key]}')
        iii += 1

    input('\nPress enter to exit.')


main()
