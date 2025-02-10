import gzip

START = 22
END = 36


def preprocess(file):
    with gzip.open(file, "rt", encoding="utf-8") as f:
        lines = f.readlines()
    lines.sort(key=lambda line: int(line[START:END]))
    with gzip.open(file, "wt", encoding="utf-8") as f:
        f.writelines(lines)
