import requests
from bs4 import BeautifulSoup
import os


    list_ = list_index.split(type_file)
    str_file = list_[0] + type_file
    return str_file


def remove_date_time(list_index, string):  # used in other_fix()
    new_list = list_index.split(string)
    new_str = new_list[0] + string
    return new_str


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


def responding_links(google_page):
    google_links = []
    for link in google_page:
        try:
            google_links.append(link.a.get('href')[7:-88])
        except:
            pass

    blacklist_file = open('blacklist.txt').read()  # for blacklisting links that do not give video files
    blacklist = blacklist_file.split('\n')
    included_links = [link for link in google_links if not any(name in link for name in blacklist)]

    return_links = []
    for link in included_links:
        try:
            link_status = requests.head(link, timeout=6, allow_redirects=False)
            if link_status.status_code == 200:
                return_links.append(link)
        except:
            pass
    return return_links


def other_fix(list_input):
    file = []
    size = []
    for index in list_input:
        _list_ = index.split('  ')  # double space
        file.append(_list_[0])

        if 'G' in _list_[-1]:
            byte = remove_date_time(_list_[-1], 'G')
            size.append(byte.strip().replace('G', 'GB'))
        elif 'M' in _list_[-1]:
            byte = remove_date_time(_list_[-1], 'M')
            size.append(byte.strip().replace('M', 'MB'))
        elif 'K' in _list_[-1]:
            byte = remove_date_time(_list_[-1], 'K')
            size.append(byte.strip().replace('K', 'KB'))
    return size


def file_and_size(list_input, compare_name):
    dict_link_size = {}
    for link in list_input:
        size = requests.get(link).text
        size = BeautifulSoup(size, 'lxml')
        link_anchors = size.find_all('a')
        size = size.text.split('\n')

        href = [z.get('href') for z in link_anchors]  # retrieves links on open directories
        href.pop(0)  # removes '../' at beginning of list

        href_temp = []
        try:
            href_temp = [index for index in href if any(name in index for name in compare_name)]
        except TypeError:
            pass

        correct_file = ['.mkv', '.avi', '.mp4']
        exclude_file = ['.srt', 'Index of', '.html', 'mp3']
        href_final = [z for z in href_temp if any(file in z for file in correct_file) if not all(x in z for x in exclude_file)]

        href_temp.clear()
        for z in href_final:
            href_temp.append(
                z.replace('%20', ' ').replace('%28', '(').replace('%29', ')').replace('%5B', '[').replace('%5D', ']'))

        # compares first 47 characters in the name of files found, to see if it matches search term
        href_47 = [z[:47] for z in href_temp]
        name_size = [z for z in size if any(index in z for index in href_47)]

        default_directory = []
        other_directory = []
        for x in name_size:
            if '\r' in x:
                default_directory.append((x.replace('\r', '')))
            elif '\xa0' in x:
                default_directory.append((x.replace('\xa0', '')))
            else:
                other_directory.append(x)

        if len(other_directory) > 0:
            final_links = [link + x for x in href_final]
            file_size = other_fix(other_directory)

            _int_ = 0
            for _link_ in final_links:
                dict_link_size[_link_] = file_size[_int_]
                _int_ += 1
            continue

        size_final = []
        for z in default_directory:
            list_ = z.split(' ')

            for index in list_:
                if '.avi' in index:
                    beg_str = insert_at_beginning(index, '.avi')
                    list_.remove(index)
                    list_.insert(0, beg_str)
                elif '.mkv' in index:
                    beg_str = insert_at_beginning(index, '.mkv')
                    list_.remove(index)
                    list_.insert(0, beg_str)
                elif '.mp4' in index:
                    beg_str = insert_at_beginning(index, '.mp4')
                    list_.remove(index)
                    list_.insert(0, beg_str)

            list_ = [list_[0], list_[-1]]

            if 'K' in list_[-1]:
                size_final.append(list_[-1].replace('K', 'KB'))
            elif 'G' in list_[-1]:
                size_final.append(list_[-1].replace('G', 'GB'))
            elif 'M' in list_[-1]:
                size_final.append(list_[-1].replace('M', 'MB'))
            else:
                byte_divide = round((int(list_[-1]) / 1000000000), 2)
                if byte_divide >= 1:
                    size_final.append(str(byte_divide) + 'GB')
                else:
                    size_final.append(str(byte_divide) + 'MB')

        final_links = [link + x for x in href_final]

        index_size = 0
        for _link_ in final_links:
            dict_link_size[_link_] = size_final[index_size]
            index_size += 1

        return dict_link_size


def main():
    user_search = introduction()

    user_search = user_search.replace(":", "")  # colons do not normally appear in open directories
    user_search = user_search.replace("-", "").replace("  ", " ")  # nor do hyphens or double spaces

    title = list(user_search.split(' '))  # splits each word from 'question_title' into a list: 'title'

    google_link = ('https://www.google.com/search?q=intext%3A%22' + str('+'.join(
        title)) + '%22+intitle%3A%22index.of%22++%2B(wmv|mpg|avi|mp4|mov)+-inurl%3A(''jsp|pl|php|html|aspx|htm|cf|shtml)')

    google_page = requests.get(google_link).text  # creates variable 'page_source' which requests link
    google_page = BeautifulSoup(google_page, 'lxml')  # 'page_source' parsed through BeautifulSoup w/ 'lxml'
    google_page = google_page.find_all('div', class_='kCrYT')  # searched to find 'div' and 'class="KCrYT"'

    link_list = responding_links(google_page)

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

