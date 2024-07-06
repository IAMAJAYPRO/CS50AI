import os
import random
import re
import sys
from collections import Counter

DAMPING = 0.85
SAMPLES = 10000


def main():
    if len(sys.argv) != 2:
        sys.exit("Usage: python pagerank.py corpus")
    corpus = crawl(sys.argv[1])
    """from pprint import pprint
    pprint(corpus)"""
    ranks = sample_pagerank(corpus, DAMPING, SAMPLES)
    print(f"PageRank Results from Sampling (n = {SAMPLES})")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")
    ranks = iterate_pagerank(corpus, DAMPING)
    print(f"PageRank Results from Iteration")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")


def crawl(directory):
    """
    Parse a directory of HTML pages and check for links to other pages.
    Return a dictionary where each key is a page, and values are
    a list of all other pages in the corpus that are linked to by the page.
    """
    pages = dict()

    # Extract all links from HTML files
    for filename in os.listdir(directory):
        if not filename.endswith(".html"):
            continue
        with open(os.path.join(directory, filename)) as f:
            contents = f.read()
            links = re.findall(r"<a\s+(?:[^>]*?)href=\"([^\"]*)\"", contents)
            pages[filename] = set(links) - {filename}

    # Only include links to other pages in the corpus
    for filename in pages:
        pages[filename] = set(
            link for link in pages[filename]
            if link in pages
        )

    return pages


def transition_model(corpus: dict[str, set[str]], page, damping_factor):
    """
    Return a probability distribution over which page to visit next,
    given a current page.

    With probability `damping_factor`, choose a link at random
    linked to by `page`. With probability `1 - damping_factor`, choose
    a link at random chosen from all pages in the corpus.
    """
    prob = {}
    for link in corpus:
        prob[link] = (1-damping_factor)/len(corpus) + \
            damping_factor*(1/len(corpus[page]) if link in corpus[page] else 0)
    return prob


def sample_pagerank(corpus: dict[str, set[str]], damping_factor, n: int):
    """
    Return PageRank values for each page by sampling `n` pages
    according to transition model, starting with a page at random.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    sps = Counter()
    cur_page = random.choice(list(corpus.keys()))
    for _ in range(n):
        tm = transition_model(corpus, cur_page, damping_factor)
        sps[cur_page] += 1
        cur_page = random.choices(
            list(tm.keys()), weights=list(tm.values()), k=1)[0]

    return {link: sps[link]/n for link in sps}


def iterate_pagerank(corpus: dict[str, set[str]], damping_factor):
    """
    Return PageRank values for each page by iteratively updating
    PageRank values until convergence.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    left_prob = (1-damping_factor)/len(corpus)
    PR = {page: 1/len(corpus) for page in corpus}

    while True:
        tmp = {}
        for page in corpus:
            su = 0
            for link in corpus:
                if corpus[link]:
                    if page in corpus[link]:
                        su += PR[link]/len(corpus[link])
                else:
                    su += PR[link]/len(corpus)

            right_prob = su*damping_factor
            """= damping_factor * \
                sum(PR[link]/len(corpus[link])
                    for link in corpus if page in corpus[link])"""

            tmp[page] = left_prob + right_prob
        if False:  # debugger
            su_pro = sum(tmp.values())
            print(su_pro)
            for page in tmp:
                tmp[page] /= su_pro
        if all(abs(tmp[page]-PR[page]) <= 0.001 for page in PR):
            PR = tmp
            break
        PR = tmp
    # print(sum(tmp.values()))
    return PR


if __name__ == "__main__":
    main()
