#!/usr/bin/python
# -*- coding: UTF-8 -*-
import re

from bs4 import BeautifulSoup

pattern = re.compile(r'\s+')


def clean_format(text):
    '''
    clean text format for text extract from html
    :param text:
    :return:
    '''
    return re.sub(pattern, " ", text.replace('\n', ' ').replace(u'\u00a0', " "))


def clean_declaration_html(html_text):
    if html_text is None or html_text == "":
        return ""
    soup = BeautifulSoup(html_text, "lxml")
    cleanText = soup.get_text()
    cleanText = clean_format(cleanText)
    return cleanText


def clean_html_text(html_text):
    if html_text is None or html_text == "":
        return ""
    soup = BeautifulSoup(html_text, "lxml")
    codeTags = soup.find_all(name=["pre", 'blockquote'])

    for tag in codeTags:
        if tag.string:
            tag.string = tag.string + " . \n "

    cleanText = soup.get_text()

    cleanText = clean_format(cleanText)
    return cleanText


def clean_html_text_with_format(html_text):
    if html_text is None or html_text == "":
        return ""
    soup = BeautifulSoup(html_text, "lxml")
    codeTags = soup.find_all(name=["pre", 'blockquote'])

    for tag in codeTags:
        if tag.string:
            tag.string = tag.string + " . \n "

    text = soup.get_text()
    text = text.replace(u'\u00a0', " ")
    lines = (line.strip() for line in text.splitlines())
    new_lines = []
    for t in lines:
        if t:
            new_lines.append(t)
        else:
            if new_lines and new_lines[-1] != "\n":
                new_lines.append("\n")
    lines = new_lines

    # break multi-headlines into a line each
    chunks = (phrase.strip() if phrase != '\n' else phrase for line in lines for phrase in line.split("  "))
    # drop blank lines
    text = ' '.join(chunk for chunk in chunks if chunk)
    text = text.replace(" \n ", "\n")

    return text


def clean_html_text_with_replacement(html_text):
    '''
    clean the html text with consider <pre> and <li> tag.
    :param html_text:
    :return:
    '''
    if html_text is None or len(html_text) == 0:
        return ""

    soup = BeautifulSoup(html_text, "lxml")
    codeTags = soup.find_all(name=["pre", 'blockquote'])

    for tag in codeTags:
        tag.string = "@C@ . "

    list_groups = soup.find_all(name=["ol", "ul"])
    for list_group in list_groups:
        list_items = list_group.find_all("li")
        num = 1
        for item in list_items:
            item.string = "{0}.{1}\n.".format(str(num), item.string)
            num = num + 1

    # todo: the sentence may lack of Punctuation mark in every <p> tag end. it will be

    cleanText = soup.get_text()
    cleanText = clean_format(cleanText)
    return cleanText


def get_api_qualifier_name_from_api_document_link(api_document_link):
    remove_start_string = api_document_link.lstrip("../")
    if remove_start_string.endswith(".html"):
        clean_string = remove_start_string[:-5]
    else:
        clean_string = remove_start_string

    return clean_string.replace("/", ".")


def extract_method_parameters_qualified_type_map_from_declaration_html(declaration_html):
    if declaration_html is None or declaration_html == "":
        return None
    soup = BeautifulSoup(declaration_html, "lxml")
    a_links = soup.find_all(name=["a", ])

    qualified_name_map = {}
    for a_link in a_links:
        api_document_link = a_link['href']
        if api_document_link:
            api_class_simple_name = a_link.get_text()
            api_class_qualified_name = get_api_qualifier_name_from_api_document_link(api_document_link)
            if qualified_name_map[api_class_simple_name] and api_class_qualified_name != qualified_name_map[
                api_class_simple_name]:
                raise Exception
            else:
                qualified_name_map[api_class_simple_name] = api_class_qualified_name
    return qualified_name_map


def parse_declaration_html_with_full_qualified_type(declaration_html):
    if declaration_html is None or declaration_html == "":
        return None
    soup = BeautifulSoup(declaration_html, "lxml")
    a_links = soup.find_all(name=["a", ])

    for a_link in a_links:
        api_document_link = a_link['href']
        if api_document_link:
            api_class_qualified_name = get_api_qualifier_name_from_api_document_link(api_document_link)
            a_link.string = api_class_qualified_name
    clean_text = soup.get_text()
    return clean_format(clean_text)


def parse_parameters_string_to_list(parameters_string):
    result = []
    parameters_list = parameters_string.split(",")
    for parameter_declaration in parameters_list:
        parameter_name = parameter_declaration.split(" ")[-1].strip()
        parameter_type = " ".join(parameter_declaration.split(" ")[:-1]).strip()
        result.append({"parameter_type": parameter_type, "parameter_name": parameter_name})
    return result