from nltk import word_tokenize
import easyocr
import re
import cv2 as cv
import os
import numpy as np
import nltk


# ITEM IMAGE

def double_line_fixing(list_of_list):
    for i in range(1, len(list_of_list)):
        if i == len(list_of_list):
            break
        if len(list_of_list[0]) == 2:

            try:
                if type(list_of_list[i][0]) == str and type(float(list_of_list[i][-1][2])) == float:
                    pass
            except:
                data = ' '.join(list_of_list[i])
                list_of_list[i - 1][0] += ' ' + data
                #                 del list_of_list[i]
                list_of_list[i] = ['nan']
        else:
            print(list_of_list[i])
            if 'otal' in ' '.join(list_of_list[i]):
                #             print('yes')
                break

            elif len(list_of_list[i]) == 1:
                #             print('elifff    ',final[i])
                list_of_list[i - 1][0] += ' ' + list_of_list[i][0]
                list_of_list[i] = ['nan']

    return list_of_list


def remove_nan_list(double_line_fixed):
    for i in double_line_fixed:
        if ' '.join(i) == 'nan':
            double_line_fixed.remove(i)
    return double_line_fixed


def fixing_missing_value(clean_data):

    for i in clean_data:
        if len(clean_data[0]) == 2:
            break
        else:
            if 'otal' in ' '.join(i):
                break
            else:
                if len(i) != len(clean_data[0]):
                    for index in range(len(clean_data[0])):
                        if 'qty' in clean_data[0][index]:
                            i.insert(index, 'nan')

    return clean_data


def spacing_issue(fixed_missed):
    for j in fixed_missed:
        if len(j) == 3:
            try:
                if type(float(j[1])) == float:
                    pass
            except:
                data = ' '.join(j[0:-1])
                del j[0]
                del j[0]
                j.insert(0, data)
    for index in range(1, len(fixed_missed)):
        if 'subtotal' in ' '.join(fixed_missed[index]) or 'total' in ' '.join(fixed_missed[index]):
            fixed_missed.insert(index, ['\n\n\n\n'])
            break
    index = fixed_missed.index(['\n\n\n\n'])
    for k in fixed_missed[index + 1:]:
        if len(k) == 1:
            k.append('nan')
    return fixed_missed


# Description image


def applying_ocr(img):
    reader = easyocr.Reader(['en'], gpu=False)
    return reader.readtext(img)


def get_org(img_name, ocr):
    gray_image = cv.cvtColor(img_name, cv.COLOR_BGR2GRAY)

    thresh_value, thresh_img = cv.threshold(gray_image, 0, 255, cv.THRESH_OTSU | cv.THRESH_BINARY)
    kernel = np.ones((4, 4), np.uint8)
    kernel_1 = np.ones((5, 4), np.uint8)
    erode_img = cv.dilate(thresh_img, kernel, iterations=2)
    eroded_img = cv.erode(erode_img, kernel_1, iterations=2)

    return ocr.readtext(eroded_img, detail=0)[0]


def arranging_sent(img_data):
    data = sorted(img_data, key=lambda x: [x[0][0][1], x[0][0][0]])

    for index in range(len(data)):
        for index in range(len(data) + 1):
            if index == len(data) - 1:
                break
            else:
                if data[index][0][0][0] < data[index - 1][0][0][0] and data[index][0][0][1] - data[index - 1][0][0][1] <= 10:
                    data[index], data[index - 1] = data[index - 1], data[index]

    return data


def get_table_data(text):
    indx = []

    for ind in range(len(text)):
        if 'Price' in text[ind][1] or 'Quan' in text[ind][1] or 'Item' in text[ind][1] or 'Name' in text[ind][1] or 'Qty' in text[ind][1] or 'Iten' in text[ind][1]:
            indx.append(ind)
            break

    for ind in range(indx[0], len(text)):

        if 'Cash:' in text[ind][1] or 'Total' in text[ind][1] or 'Value' in text[ind][1] or 'Balance' in text[ind][1] or "TOTAL" in text[ind][1]:
            indx.append(ind)

    return text[indx[0]:indx[-1] + 2]


def get_headings(table_data, image, ocr):
    head = []
    heading = []
    for i in table_data:
        head.append(i)
        if 'al' in i[1]:
            break
    # print('Done')

    for i in head:
        starting = (int(i[0][0][0]) - 25, int(i[0][0][1]) - 10)
        ending = (int(i[0][2][0]) + 20, int(i[0][2][1]) + 50)

        crop_img = image[int(starting[1]): int(ending[1]), int(starting[0]):int(ending[0])]
        heading.append(ocr.readtext(crop_img))

    headers = []
    for ls in heading:
        for ele in ls:
            headers.append(ele[1])
        headers.append('\n')

    data = " ".join(headers)
    refine_data = data.split('\n')
    # print(refine_data[0])
    curr_data = word_tokenize(refine_data[0])
    if len(curr_data) > 1:
        refine_data.insert(0, "Description")
        refine_data.insert(1, curr_data[0])
        del refine_data[2]

    else:
        refine_data.insert(0, "Description")

    for index in range(len(refine_data)):
        refine_data[index] = refine_data[index].replace(',', ' ')

    return refine_data


def data_into_lst(table_data):
    count = 0
    dic = {}
    for i in range(len(table_data)):
        if i == 0:
            dic[count] = [table_data[i][1]]
        elif abs(table_data[i][0][0][1] - table_data[i - 1][0][0][1]) <= 12:
            if abs(table_data[i - 1][0][2][0] - table_data[i][0][0][0]) <= 10:
                data = dic.get(count)
                #             data.append(table_data[i][1])
                data[-1] += ' ' + table_data[i][1].replace(',', '')
                dic[count] = data
            else:
                data = dic.get(count)
                data.append(table_data[i][1].replace(',', ''))
                dic[count] = data
        else:
            count += 1
            dic[count] = [table_data[i][1].replace(',', '')]

    list_of_list = []
    for i in range(len(dic)):
        list_of_list.append(dic.get(i))
    return list_of_list


def main_fix_points(lst):
    for index in range(1, len(lst)):
        try:

            if type(lst[index]) == list:
                # print(lst[index])
                if '.' in lst[index][0]:
                    # print(lst[index][0])

                    data = lst[index][0].split('.')
                    data_1 = lst[index][-1].split('.')

                    lst[index][0] = data[0]
                    lst[index][-1] = data_1[0]
                    lst[index] = type_int(lst[index], lst[0])
                    # print(lst[index])

                elif '.' in lst[index][-1]:
                    data = lst[index][-1].split('.')
                    data_1 = lst[index][0].split('.')

                    lst[index][-1] = data[0]
                    lst[index][0] = data_1[0]

                    lst[index] = type_int(lst[index], lst[0])

                else:
                    lst[index] = type_int(lst[index], lst[0])
            else:
                # print('else: ', lst[index])
                dat = lst[index]
                dat = dat.split(' ')
                lst[index] = dat
                # print(f'dat {dat}')
                if '.' in lst[index][1]:
                    # print(lst[index][1])
                    data, noisy_data = lst[index][1].split('.')
                    lst[index][1] = data
                    lst[index] = type_int(lst[index], lst[0])

                elif '.' in lst[index][-1]:
                    data, noisy_data = lst[index][-1].split('.')
                    lst[index][-1] = data
                    lst[index] = type_int(lst[index], lst[0])

                else:
                    lst[index] = ' '.join(dat)

        except:
            pass

    return lst


def type_int(data, headings):
    try:
        if type(float(data[0])) == type(float(data[-1])):

            if len(data) == len(headings):
                pass

            else:
                curr_data = data

                for index in range(len(headings)):
                    if 'ty' in headings[index]:
                        ind = index

                curr_data.insert(ind, 'nan')
                data = curr_data
                # print('data', data)
    except:
        data = ' '.join(data)
        # print('working')

    return data


def removing_noise(text):
    for index in range(len(text)):

        if type(text[index]) == str:
            norm_text = re.sub(r"[^a-zA-Z0-9.%,]", " ", text[index].lower())
            text[index] = norm_text
        else:
            for i in range(len(text[index])):
                norm_text = re.sub(r"[^a-zA-Z0-9.%,]", " ", text[index][i].lower())
                text[index][i] = norm_text

    return text


def fixing_end_table(data_n):
    starting_range = 2
    for index in range(2, len(data_n)):

        if type(data_n[index]) == str and type(data_n[index + 1]) == str:

            for start_index in range(starting_range, len(data_n)):
                if type(data_n[start_index]) == str:
                    data_n[start_index] = word_tokenize(data_n[start_index])
                # data_n[start_index] = data_n[start_index].split(' ')
            break

        else:
            starting_range += 1

    for index in range(starting_range, len(data_n)):
        lst = data_n[index]
        count = 0
        for i in range(len(lst)):
            try:
                # print(f'Count: {count}')
                if type(float(lst[count])) == float:
                    # print('working 1')
                    # print("Lst", lst[count])
                    data_n[index].insert(count, ',')
                    count += 2
                    data_n[index].insert(count, ',')
                    count += 1
                    # print(count)
            except:
                if count == 2:
                    # print('working 2')
                    data_n[index].insert(count, ',')
                    count += 1
                    data_n[index].insert(count, 'nan')
                    count += 1
                    data_n[index].insert(count, ',')

                # print(f'except: {lst[count]}')
                count += 1
                # print(count)

        try:
            if 'nan' in lst[-1] or ',' in lst[-1] or ',' in lst[-2]:
                pass

            elif type(float(lst[-1])) == float:
                lst.insert(len(lst) - 1, ',')
                data_n[index] = lst

        except:
            lst.insert(len(lst), ',')
            lst.insert(len(lst) + 1, 'nan')
            data_n[index] = lst

    return data_n


def finding_date_invoice(arranged_data):
    date_pattern = r'^(\d{4}|\d{2}|\d{1})(-|/)(\d{2}|\d{1})(-|/)(\d{4}|\d{2})'
    finded_lst = []
    for index in range(len(arranged_data)):
        # print(arranged_data[index][1])
        if 'Price' in arranged_data[index][1] or 'Total' in arranged_data[index][1]:
            break

        # print(arranged_data[index][1])
        lst = arranged_data[index][1].split(' ')
        if "invoice" in arranged_data[index][1].lower() or "bill" in arranged_data[index][1].lower() or "inv" in \
                arranged_data[index][1].lower() or "trans" in arranged_data[index][1].lower() or "rec" in \
                arranged_data[index][1].lower() or "receipt" in \
                arranged_data[index][1].lower():

            finded_lst.append(arranged_data[index][1])

            try:
                if type(float(arranged_data[index][1][-2])) == float:
                    pass

            except:
                finded_lst.append(arranged_data[index + 1][1])

        for data in lst:
            if re.match(date_pattern, data):
                print(arranged_data[index][1])
                finded_lst.append(arranged_data[index][1])

    return finded_lst


def removing_noise_int(text):
    for index in range(1, len(text)):

        if 'item' in ' '.join(text[0]) or 'name' in ' '.join(text[0]):

            if "total" in " ".join(text[index]):
                if 'nan' == text[index][-1]:
                    pass

                else:
                    norm_text = re.sub(r"[^0-9.,]", "0", text[index][-1].lower())
                    text[index][-1] = norm_text
                break

            if len(text[index]) == 1:
                pass

            elif type(text[index]) == list:
                for i in range(1, len(text[index])):

                    if 'nan' == text[index][i]:
                        pass

                    else:
                        norm_text = re.sub(r"[^0-9.,]", "0", text[index][i].lower())
                        text[index][i] = norm_text

        else:

            if "total" in " ".join(text[index]):
                if 'nan' == text[index][-1]:
                    pass

                else:
                    norm_text = re.sub(r"[^0-9.,]", "0", text[index][-1].lower())
                    text[index][-1] = norm_text

                break

            if len(text[index]) == 1:
                pass

            elif type(text[index]) == list:
                for i in range(len(text[index])):
                    if 'nan' == text[index][i]:
                        pass
                    else:
                        norm_text = re.sub(r"[^0-9.,]", "0", text[index][i].lower())
                        text[index][i] = norm_text

    return text


def returning_flags(data):
    subtotal = 0
    count = 0
    for index in range(1, len(data)):

        if len(data[index]) == 1:
            pass

        elif "total" in " ".join(data[index]):

            if 'nan' == data[index][-1]:
                subtotal = data[index][-1]

            elif 'nan' == data[index][-2]:
                subtotal = data[index][-1]

            else:
                try:
                    # print(data[index][-1])
                    subtotal = float(data[index][-1])

                except:
                    subtotal = float(data[index][-2])

            break

        elif type(data[index]) == list:

            count += float(data[index][-1])

    if count == subtotal:
        flag = "#04AA6D"
        # print(f"Total: {subtotal}", f"Count: {count}")
    else:
        flag = "red"
        # print(f"Total: {subtotal}", f"Count: {count}")

    return flag


def fix_indent(invoice_date):
    index_date = ''
    index_inv = ''

    for index in range(len(invoice_date)):
        if '-' in invoice_date[index] or '/' in invoice_date[index]:
            index_date = index
            # print(f'Index: {index}')

        if "invoice" in invoice_date[index].lower() or "bill" in invoice_date[index].lower() or "inv" in invoice_date[
            index].lower() or "trans" in invoice_date[index].lower() or "rec" in invoice_date[
            index].lower() or "receipt" in invoice_date[index].lower():
            index_inv = index
            try:
                # print("Testing_1: ", invoice_date[index])
                if type(int(invoice_date[index][-1])) == int:
                    pass
            except:
                try:
                    # print("Testing_2: ", invoice_date[index + 1])
                    if type(int(invoice_date[index + 1][-2])) == int:
                        invoice_date[index] += " " + invoice_date[index + 1]
                except:
                    invoice_date[index] += ": " + "NAN"

    # print(f'Inv: {invoice_date[index_inv]}')
    # print(type(index_date))

    if type(index_date) == str:
        index_date = -1
        invoice_date.append("NAN")

    elif type(index_inv) == str:
        index_inv = -1
        invoice_date.append("NAN")

    dic = {"Date": invoice_date[index_date], "Invoice": invoice_date[index_inv]}

    return dic


def main_function(encode_img):
    print('Working 1')
    nltk.download('punkt')
    print('Working 2')
    decode = np.array(encode_img, dtype='uint8')
    print('Working 3')
    img = cv.imdecode(decode, cv.IMREAD_COLOR)
    print('Working 4')

    reader = easyocr.Reader(['en'], gpu=False)
    print('Working 5')

    new_img = img.copy()
    print('Working 6')

    img_data = reader.readtext(img)
    print('Working 7')

    org_name = get_org(new_img, reader)
    print('Working 8')
    bill_date_data = finding_date_invoice(img_data)
    print('Working 9')
    date_invoice = fix_indent(bill_date_data)
    print('Working 10')
    arranged_data = arranging_sent(img_data)
    print('Working 11')
    table_data = get_table_data(arranged_data)
    print('Working 12')

    head = []
    for i in table_data:
        head.append(i[1])
        if 'Price' in i[1] or 'Total' in i[1] or 'Amount' in i[1]:
            break

    if 'Item' in ' '.join(head) or 'Name' in ' '.join(head):
        # print('item')
        list_of_list = data_into_lst(table_data)
        double_line_fixed = double_line_fixing(list_of_list)
        rem_nan = remove_nan_list(double_line_fixed)
        clean_data = removing_noise(rem_nan)
        fixed_missed = fixing_missing_value(clean_data)
        final = spacing_issue(fixed_missed)
        dict = {"Organization Name: ": org_name, 'Date: ': date_invoice.get('Date'), "Invoice: ": date_invoice.get('Invoice')}
        bill_date_data.insert(0, org_name)

        cleaned_data = removing_noise_int(final)
        flags = returning_flags(cleaned_data)

        dic = {'data': final, 'dict': dict, 'flags': flags}

    else:
        # print('description')
        headings = get_headings(table_data, new_img, reader)
        clean_heading = removing_noise(headings)

        data_table = data_into_lst(table_data)
        clean_data = removing_noise(data_table)
        data = main_fix_points(clean_data)
        write_able_data = fixing_end_table(data)

        bill_date_data.insert(0, org_name)
        dict = {"Organization Name: ": org_name, 'Date: ': date_invoice.get('Date'), "Invoice: ": date_invoice.get('Invoice')}

        del write_able_data[1]
        write_able_data[0] = clean_heading

        cleaned_data = removing_noise_int(write_able_data)
        flags = returning_flags(cleaned_data)
        for inde in range(len(write_able_data)):
            if type(write_able_data[inde]) == str:
                write_able_data[inde+1].insert(0, write_able_data[inde])
        for rem in write_able_data:
            if type(rem) == str:
                write_able_data.remove(rem)

        for indexx in range(len(write_able_data)):
            if ',' in write_able_data[indexx]:
                data = ' '.join(write_able_data[indexx])
                write_able_data[indexx] = data.split(',')

        for index in range(1, len(write_able_data)):
            if 'total' in ' '.join(write_able_data[index]) or 'amount' in ' '.join(write_able_data[index]):
                write_able_data.insert(index, ['\n\n\n\n'])
                break
        dic = {'data': write_able_data, 'dict': dict, "flags": flags}

    return dic