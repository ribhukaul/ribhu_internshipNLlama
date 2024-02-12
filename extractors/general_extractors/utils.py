from collections import defaultdict
import re
import string

def select_desired_page(text, words_repr):
    """Select the page with the most occurrences of the words in words_repr.

    Args:
        text (lst): list of pages text
        words_repr (lst): list of words to look for in the pages provided

    Returns:
        str: page nindex with the most occurrences of the words in words_repr
    """
    counter = defaultdict(int)

    for i, page in enumerate(text):
        if page == "":
            continue

        # Remove punctuation and replace \n with space
        content = page.page_content.lower().replace('\n', ' ')
        for word in words_repr:
            # count how many times the word is in the page
            counter[str(i)] += content.count(word)

    # Page with most occurrences
    pg_number = max(counter, key=counter.get)


    return pg_number


def select_desired_table(tables, words_repr):
    """Select the table with the most occurrences of the words in words_repr.

    Args:
        tables (lst): list of df tables
        words_repr (lst): list of words to look for in the pages provided

    Returns:
        int: table index with the most occurrences of the words in words_repr
    """
    counter = defaultdict(int)
    # Search all the tables
    for i, table in enumerate(tables):
        for word in words_repr:
            # print(word)
            # print(table.apply(lambda col:col.str.count(word, flags=re.IGNORECASE)).sum().sum())

            counter[str(i)] += (
                table.apply(lambda col: col.str.count(word, flags=re.IGNORECASE))
                .sum()
                .sum()
            )

    # Page with most occurrences
    tb_number = max(counter, key=counter.get)
    return tb_number


def select_desired_table_only_header(tables, words_repr):#change from normal is that it only looks at the header
    """Select the table with the most occurrences of the words in words_repr.

    Args:
        tables (lst): list of df tables
        words_repr (lst): list of words to look for in the pages provided

    Returns:
        int: table index with the most occurrences of the words in words_repr
    """
    new_tables = [table.iloc[0].to_frame() for table in tables]

        
    counter = defaultdict(int)
    # Search all the tables
    for i, table in enumerate(new_tables):
        for word in words_repr:
            # print(word)
            # print(table.apply(lambda col:col.str.count(word, flags=re.IGNORECASE)).sum().sum())

            counter[str(i)] += (
                table.apply(lambda col: col.str.count(word, flags=re.IGNORECASE))
                .sum()
                .sum()
            )

    # Page with most occurrences
    tb_number = max(counter, key=counter.get)
    return tb_number

