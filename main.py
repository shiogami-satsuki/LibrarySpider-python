import requests
import json
from bs4 import BeautifulSoup


def get_covers(isbn_list):
    api = "https://book-resource.dataesb.com/websearch/metares?cmdACT=getImages&isbns="
    isbn_arg = ','.join(list(map(str, isbn_list)))
    url = api + isbn_arg
    response = requests.get(url)
    trim_text = response.text.lstrip('(').rstrip(')')
    data = json.loads(trim_text)
    return data['result']


def get_cover(isbn):
    return get_covers([isbn])[0]["coverlink"]


def get_book_simple(book_id):
    api = "http://opac.gzlib.org.cn/opac/book/"
    url = api + str(book_id) + "?view=simple"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'lxml')
    data = soup.select("#bookInfoTable")
    print(url)
    tr = data[0].select("tr")
    for line in tr:
        left = line.select(".leftTD")[0].text.split()
        right = line.select(".rightTD")[0].text.split()
        # print(right)
        print(''.join(left), '\t\t', ' '.join(right))


def get_holding(book_id, limit_libcodes=[]):
    api = "http://opac.gzlib.org.cn/opac/api/holding/"
    args = "?limitLibcodes="
    url = api + str(book_id)
    response = requests.get(url)
    data = json.loads(response.text)
    return data


def get_holding_previews(book_id_list, cur_libcodes=[]):
    api = "http://opac.gzlib.org.cn/opac/book/holdingPreviews?return_fmt=json&bookrecnos="
    args = "&limitLibcodes="
    url = api + ','.join(list(map(str, book_id_list))) + args + ','.join(cur_libcodes)
    response = requests.get(url)
    data = json.loads(response.text)
    return data["previews"]


def get_search(keyword, search_way="title", rows=10, page=1, go_next_page=False):
    api = "http://opac.gzlib.org.cn/opac/search?"
    # args = "searchSource=reader&scWay=dim&sortWay=score&sortOrder=desc&rows=10
    # &hasholding=1&curlibcode=GT&searchWay=title&q="
    args = "searchWay=" + search_way + "&rows=" + str(rows) + "&page=" + str(page) + "&q="
    url = api + args + str(keyword)
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'lxml')
    data = soup.select(".resultTable")
    books_data = []
    books_info = []
    for i in range(len(data[0].contents)):
        if i % 2 == 1: books_data.append(data[0].contents[i])
    for book in books_data:
        books_info.append({
            "title": book.select(".title-link")[0].text.strip(),
            "author": book.select(".author-link")[0].text.strip(),
            "publisher": book.select(".publisher-link")[0].text.strip(),
            "type": book.select(".booktypeIcon")[0].parent.text.split()[1],
            "isbn": book.select(".bookcover_img")[0]["isbn"].replace("-", ""),
            "book_id": book.find("input")["value"]})
    search_meta = soup.select("#search_meta")
    total_result = int(list(search_meta[0].strings)[3].split(",")[1].strip().split()[1])
    this_used_time = float(list(search_meta[0].strings)[3].split(",")[2].strip().split()[1])
    used_time = this_used_time
    if total_result / rows - page > 0 and go_next_page:
        next_page = get_search(keyword, search_way, rows, page + 1, True)
        used_time = this_used_time + next_page["used_time"]
        books_info.extend(next_page["books_info"])
    return {"books_info": books_info, "total_result": total_result, "used_time": used_time}


"""
hold = get_holding(1919773)
for book in hold["holdingList"]:
    print("recno:", book["recno"])
    print("state:", hold["holdStateMap"][str(book["state"])]["stateName"])
    print("barcode:", book["barcode"])
    if book["barcode"] in hold["loanWorkMap"]:
        print("loanDate:", hold["loanWorkMap"][book["barcode"]]["loanDate"])
        print("returnDate:", hold["loanWorkMap"][book["barcode"]]["returnDate"])
    print("orglib:", hold["libcodeMap"][book["orglib"]])
    print("orglocal:", hold["localMap"][book["orglocal"]])
    print("curlib:", hold["libcodeMap"][book["curlib"]])
    print("curlocal:", hold["localMap"][book["curlocal"]])
    print("cirtype:", hold["pBCtypeMap"][book["cirtype"]]["name"])
    print()
"""
#
# books = get_search("东野圭吾", "author")
# print(books)
# print(len(books["books_info"]))

# get_book_simple(3003674840)
"""
id_list = [1919773]
pr = get_holding_previews(id_list)
for id in id_list:
    for loc in pr[str(id)]:
        print(loc["curlibName"], "\t", loc["curlocalName"], "\t", loc["loanableCount"], ",total", loc["copycount"])
"""
